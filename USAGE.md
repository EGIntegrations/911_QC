Below is a step-by-step, “from-zero-to-production” play-book you can follow (or hand off to your client’s IT team) to deploy, test and operate the real-time 911-call QA platform you now have.
I’ve written it in the order you will actually perform the work, and I’ve called out Gotchas ⚠, Cost checkpoints 💲, and Security mandates 🔐 where they matter most.

⸻

1. Environment overview — what you’re installing

Layer	What it is	Why it’s needed	Where it runs now	Where it will run in 6-9 mo (GovCloud)
Audio-capture service (Python/FFmpeg)	Taps the live audio feed, chunks it into WAV & streams to Whisper	Real-time ingestion	On-prem Windows Server (as a Windows Service or Docker container)	EC2 (Win Server) in GovCloud
Whisper transcription service (OpenAI API, model = whisper-1)	Speech-to-text with high accuracy	Needed for downstream NLP	Same instance as above	Same (GovCloud VPC)
Speaker diarization (pyannote)	Tags caller vs. operator	Enables compliance scoring per speaker	GPU-enabled container or CPU fallback	GPU EC2 or AWS Inferentia
Categorizer & compliance scorer (GPT-4o)	Detects incident type & grades operator	Business logic core	Python container/service	Python Lambda or ECS Fargate
Flagging / alert router	Pushes “high-priority” incidents or scores < 50 to Mgmt. queue	Alerts supervisors in real-time	Redis pub/sub or Amazon SQS (local)	Amazon SQS + EventBridge
Encrypted object store	JSON transcripts + metadata	Historical analytics & audit	AES-256 encrypted share on the Windows server	Amazon S3 (GovCloud, SSE-KMS)
Dashboard / API	Optional demo UI; health probes	Validation/testing	Streamlit on-prem (demo only)	Can decommission or redeploy to ECS



⸻

2. Prerequisites on the call-center server

Item	Minimum spec / comment
Windows Server 2019+	.NET 4.8 installed (for some audio drivers)
Python 3.11 (x64)	Use the Microsoft Store or winget
Docker Desktop (Windows containers)	Recommended for easy upgrades
FFmpeg 7.x static	Already bundled in bin/ffmpeg — ensure bin is in PATH
GPU (optional)	NVIDIA RTX A2000 or better for pyannote or run CPU mode
Outbound 443	To api.openai.com & future GovCloud endpoints
VoIP or TDM tap	The service needs mirrored audio packets or SIP‐REC RTP stream



⸻

3. Installation (1–2 hours)

Do the following on the Windows server (or inside a Dockerfile if going containerized).

	1.	Clone your repo

git clone https://github.com/EGIntegrations/911_QC.git C:\911_QC
cd C:\911_QC


	2.	Create a virtual env (if not using Docker)

python -m venv .venv
.\.venv\Scripts\Activate.ps1


	3.	Install requirements (now upgraded for OpenAI v1.0 syntax)

pip install -r requirements.txt


	4.	Set environment variables — you may store these in Windows “System Environment Variables” or a .env file (Dotenv already loaded).

OPENAI_API_KEY=sk-********************************
WHISPER_SAMPLE_RATE=16000
COMPLIANCE_THRESHOLD=50
FLAG_KEYWORDS=gun,weapon,knife,hostage
REDIS_URL=redis://localhost:6379/0      # or AWS SQS ARN in future


	5.	Configure the audio tap
	•	If your Carbide phone system provides SIP-REC, mirror that RTP stream to the server’s NIC.
	•	Point audio_capture.py at that interface or adapt to your vendor’s API.
	6.	Register the service
	•	Windows service: nssm install 911AudioService "C:\911_QC\run_realtime.bat"
	•	Docker: build the Dockerfile and run with --restart=always.

⸻

4. Real-time keyword-flag & low-score queuing

Code hooks you already have

Script	Function	Addition you made
categorize_call.py	GPT classification	Writes {category, reasoning} JSON
evaluate_operator.py	GPT compliance	Publishes {"score":…, "transcript_id":…} to Redis/SQS when score < env COMPLIANCE_THRESHOLD
NEW flag_keywords.py	Simple regex on transcript text	Publishes to same queue when keyword hit

How it fires

flowchart LR
    A[GPT result or keyword hit] --> B[Redis/SQS "high_priority"]
    B --> C[Supervisor Dashboard / Email / PagerDuty]

When you move to GovCloud, swap Redis for Amazon SQS (same publish code, change the client).

⸻

5. Testing & Acceptance

Test phase	How to run	Expected pass
Unit tests	pytest tests/	≥ 90 % coverage
Synthetic call	Play prerecorded WAV via audio_capture.py --file demo.wav	Transcript JSON created under data/transcripts/, categorized JSON under categorized_calls/, compliance JSON under data/compliance/
Load test	locust with 20 concurrent calls (8 kbps each)	< 200 ms p95 end-to-end latency
Keyword flag	WAV saying “he has a gun”	Message appears in high-priority queue
Ops score fail	Script with missing steps	Supervisor alert in queue



⸻

6. Cost & usage monitoring

Cost driver 💲	Where to watch	Typical range	Mitigation
OpenAI tokens (Whisper & GPT-4o)	openai.api_usage dashboard	$0.006 / min (Whisper) + $0.01 / 1K tokens (GPT-4o)	Trim temperature, reduce max_tokens, sample rate
Egress bandwidth	ISP bill now; AWS Data Transfer later	70 kbps per active call	Use GovCloud VPC peering, compress JSON
Storage (JSON)	Local disk or S3	2 kb × calls/day	Lifecycle rules (archive > 180 days)
GPU hours	On-prem power or EC2 GPU	$0.674 / hour (g4dn.xlarge)	Switch to CPU nights/weekends



⸻

7. Security & compliance 🔐
	1.	Encryption in transit – TLS 1.2 on every call to OpenAI, SQS, S3.
	2.	Encryption at rest – AES-256 for JSON files (EFS + BitLocker now, S3 SSE-KMS later).
	3.	Zero PII in logs – mask caller names & phone numbers with ***.
	4.	API key rotation – monthly via Windows Task Scheduler or AWS Secrets Manager.
	5.	GovCloud lift-and-shift – deploy the same Docker images to ECS Fargate inside GovCloud; use VPC Endpoints to avoid public internet.

⸻

8. Phase timeline

Phase	Duration	Key deliverables
Phase 1 – Core ingestion	Week 1	Audio Capture → Whisper → JSON transcript
Phase 2 – NLP & compliance	Weeks 2–3	Categorizer, scoring, keyword flagging, alerts
Phase 3 – Harden & cut-over	Weeks 4–6	High-availability, security hardening, on-site acceptance, run-book hand-off

<img width="602" alt="Screenshot 2025-04-23 at 16 03 52" src="https://github.com/user-attachments/assets/06ac2177-0eee-4873-8aeb-0bf6c3e2cc48" />


⸻

The bottom line

Follow the checklist above and you will have a secure, real-time, production-ready 911 QA platform running on-prem within a month and seamlessly portable to AWS GovCloud when the client is ready.

If anything here needs deeper code snippets or screenshots, let me know and I’ll prepare them.
