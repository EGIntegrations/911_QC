1. Environment overview — what you’re installing

<img width="869" alt="Screenshot 2025-04-23 at 16 08 24" src="https://github.com/user-attachments/assets/f0d7de4e-f508-42c2-8c33-4cc7b447ff94" />

<img width="552" alt="Screenshot 2025-04-23 at 16 08 40" src="https://github.com/user-attachments/assets/e8e743a5-670f-4d5f-9e07-94a49d77132f" />



⸻

2. Prerequisites on the call-center server

<img width="571" alt="Screenshot 2025-04-23 at 16 06 48" src="https://github.com/user-attachments/assets/2838e6c2-128a-4eb4-b04f-3fff00ab69d3" />



⸻

3. Installation (1–2 hours)

Do the following on the Windows server (or inside a Dockerfile if going containerized).

	1.	Clone your repo
```
git clone https://github.com/EGIntegrations/911_QC.git C:\911_QC
cd C:\911_QC
```

	2.	Create a virtual env (if not using Docker)
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

	3.	Install requirements (now upgraded for OpenAI v1.0 syntax)
```
pip install -r requirements.txt
```

	4.	Set environment variables — you may store these in Windows “System Environment Variables” or a .env file (Dotenv already loaded).
```
OPENAI_API_KEY=sk-********************************
WHISPER_SAMPLE_RATE=16000
COMPLIANCE_THRESHOLD=50
FLAG_KEYWORDS=gun,weapon,knife,hostage
REDIS_URL=redis://localhost:6379/0      # or AWS SQS ARN in future
```

	5.	Configure the audio tap
	•	If your Carbide phone system provides SIP-REC, mirror that RTP stream to the server’s NIC.
	•	Point audio_capture.py at that interface or adapt to your vendor’s API.
	6.	Register the service
	•	Windows service: nssm install 911AudioService "C:\911_QC\run_realtime.bat"
	•	Docker: build the Dockerfile and run with --restart=always.

⸻

4. Real-time keyword-flag & low-score queuing

<img width="692" alt="Screenshot 2025-04-23 at 16 05 56" src="https://github.com/user-attachments/assets/871b5ab4-ef5c-46a6-bced-f8128cc91144" />


How it fires

```
flowchart LR
    A[GPT result or keyword hit] --> B[Redis/SQS "high_priority"]
    B --> C[Supervisor Dashboard / Email / PagerDuty]
```

When you move to GovCloud, swap Redis for Amazon SQS (same publish code, change the client).

⸻

5. Testing & Acceptance

<img width="682" alt="Screenshot 2025-04-23 at 16 05 26" src="https://github.com/user-attachments/assets/e74943f5-8d35-4ca0-9b62-d89c78fd041e" />




⸻

6. Cost & usage monitoring

<img width="996" alt="Screenshot 2025-04-23 at 16 04 58" src="https://github.com/user-attachments/assets/c272b920-5816-4e9b-87bc-6eadff053dd0" />



⸻

7. Security & compliance 🔐
	1.	Encryption in transit – TLS 1.2 on every call to OpenAI, SQS, S3.
	2.	Encryption at rest – AES-256 for JSON files (EFS + BitLocker now, S3 SSE-KMS later).
	3.	Zero PII in logs – mask caller names & phone numbers with ***.
	4.	API key rotation – monthly via Windows Task Scheduler or AWS Secrets Manager.
	5.	GovCloud lift-and-shift – deploy the same Docker images to ECS Fargate inside GovCloud; use VPC Endpoints to avoid public internet.

⸻

8. Phase timeline


<img width="602" alt="Screenshot 2025-04-23 at 16 03 52" src="https://github.com/user-attachments/assets/06ac2177-0eee-4873-8aeb-0bf6c3e2cc48" />


⸻

The bottom line

Follow the checklist above and you will have a secure, real-time, production-ready 911 QA platform running on-prem within a month and seamlessly portable to AWS GovCloud when the client is ready.

If anything here needs deeper code snippets or screenshots, let me know and I’ll prepare them.
