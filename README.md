
# 🚨 911 Call AI - Automated Emergency Call Processing System

## 📌 Overview
This project automates **911 emergency call processing** using **AI-driven transcription, categorization, and operator compliance evaluation**.  
It is designed for **CJIS-compliant in-house deployments** at emergency dispatch centers.

---

## ✅ Features
- **Real-time Call Transcription** (Whisper AI)
- **Speaker Identification** (Pyannote Audio)
- **Emergency Categorization** (GPT-4o)
- **Operator Script Compliance Scoring**
- **Full Automation via Background Service**
- **Secure On-Premise Deployment**

---

# 🛠️ **1. Installation**
## 🔹 **Step 1: Clone the Repository**
```
bash
git clone https://github.com/YOUR_USERNAME/911-call-ai.git
cd 911-call-ai
```
🔹 Step 2: Set Up Python Virtual Environment
```
python3 -m venv env
source env/bin/activate  # macOS/Linux
env\Scripts\activate      # Windows
```
🔹 Step 3: Install Dependencies
```
pip install -r requirements.txt
```


⸻

🏃 2. Running the System

🔹 Run the Full Pipeline Manually
```
python3 scripts/process_911_call.py
```
✅ This records, transcribes, categorizes, and evaluates compliance in one run.

🔹 Run as a Continuous Background Service
```
nohup python3 scripts/911_service.py &
```
✅ Runs the system continuously, processing new calls.

🔹 Stop the Background Service
```
pkill -f 911_service.py
```


⸻

🧪 3. Testing

Run unit tests for each module:
```
python3 -m unittest discover -s tests
```


⸻

🔒 4. CJIS-Compliant Deployment Guide

On-Premise Secure Installation

🔹 Step 1: Provision a Dedicated Server
	•	Use Ubuntu Server 22.04 LTS
	•	Ensure AES-256 encryption for data storage
	•	Limit network access to approved 911 center IPs

🔹 Step 2: Install Required System Packages
```
sudo apt update && sudo apt install -y python3 python3-venv ffmpeg portaudio19-dev
```
🔹 Step 3: Clone and Configure the System
```
git clone https://github.com/YOUR_USERNAME/911-call-ai.git
cd 911-call-ai
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
🔹 Step 4: Run as a Persistent System Service
```
sudo nano /etc/systemd/system/911-service.service
```
Paste the following:
```
[Unit]
Description=911 Call Processing AI
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/911-call-ai/scripts/911_service.py
WorkingDirectory=/path/to/911-call-ai
Restart=always
User=911admin

[Install]
WantedBy=multi-user.target
```
Save and exit, then enable and start the service:
```
sudo systemctl enable 911-service
sudo systemctl start 911-service
```
🔹 Step 5: Monitor Logs
```
sudo journalctl -u 911-service -f
```

⸻

📊 6. Future Enhancements
	•	Database Integration (Store reports in PostgreSQL instead of JSON)
	•	Web Dashboard (Monitor real-time compliance scores)
	•	Multi-language Support (For non-English emergency calls)

⸻

📜 7. License

© 2025. This project follows CJIS-compliant security standards and is intended for authorized emergency use only.

---

