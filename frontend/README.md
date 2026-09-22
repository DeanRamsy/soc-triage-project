AI-Driven Multi-Modal Triage Assistant (Sense-Reason-Act)
University of London BSc Computer Science Final Project
This repository contains the complete prototype implementation of the AI-Driven Multi-Modal Triage Assistant, developed as part of the University of London BSc Computer Science final capstone project.
The primary objective of this system is to alleviate Security Operations Center (SOC) analyst alert fatigue and calibrate human trust under production constraints. It achieves this by orchestrating a localized, privacy-preserving Large Language Model (LLM) to perform near-real-time triage and generate natural language security explanations over raw network connection logs.
1. Architectural Overview
The system is designed around a decoupled, three-tier model that implements the classic robotic Sense-Reason-Act loop:
Perception Layer (Sense): A read-only database connector that securely queries raw network connection telemetry from a highly normalized Third Normal Form (3NF) MySQL database.
Reasoning Layer (Reason): A Flask REST API that formats database telemetry into structured prompts and orchestrates a local quantized large language model (Qwen 0.5B via Ollama) to evaluate threat intent.
Action Layer (Act): A case-insensitive heuristic regex parsing engine that normalizes unstructured model outputs on-the-fly and serves them to a high-contrast, born-accessible React dashboard.
2. Directory Layout
The project structure is organized to isolate dependencies and maintain modular boundaries:
soc_triage_project/
├── backend/
│   ├── app.py                (Flask REST API Server)
│   ├── database.py           (MySQL Connection Manager)
│   ├── parser.py             (Heuristic Regex Parser)
│   ├── test_components.py    (Component-level Verification Script)
│   └── requirements.txt      (Python dependencies)
├── frontend/
│   ├── src/
│   │   ├── App.js            (React Dashboard Interface)
│   │   └── index.js
│   ├── package.json          (Frontend dependencies)
│   └── package-lock.json
├── schema.sql                (3NF Relational Database Schema)
└── README.md                 (This Technical Manual)
3. System Requirements
Hardware Requirements
Processor: Quad-core Intel Core i5 / AMD Ryzen 5 minimum (Apple Silicon M1/M2/M3 or dedicated Nvidia GPU highly recommended for local model execution).
Memory: 8 GB of RAM minimum (16 GB recommended).
Storage: 1.5 GB of free disk space (to accommodate Python virtual environments, Node modules, and local model weights).
Software Prerequisites
Operating System: macOS, Windows 10/11, or Linux (Ubuntu/Debian).
Python Runtime: Python 3.9 to 3.12.
Node.js Runtime: Node.js LTS (v18 or newer) with npm.
MySQL Server: MySQL Community Server (v8.0 or newer).
Ollama: A local installation of the Ollama inference engine.
4. Setup and Installation
Step 4.1: Database Seeding
Start your local MySQL instance.
In your terminal, create the target database and seed the normalized schema and sample telemetry:
mysql -u root -p -e "CREATE DATABASE SOCTriage;"
mysql -u root -p SOCTriage < schema.sql
Step 4.2: Local LLM Configuration
Ensure the Ollama service is active on your host machine.
Pull the lightweight, quantized 0.5-billion parameter Qwen model:
ollama pull qwen:0.5b
Step 4.3: Backend Environment Setup
Navigate into the backend directory:
cd backend
Initialize and activate a Python virtual environment:
python3 -m venv venv
source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate
Install the required Python packages:
pip install -r requirements.txt
Step 4.4: Frontend Environment Setup
Open a new terminal tab and navigate to the frontend folder:
cd frontend
Install the necessary JavaScript dependencies:
npm install
5. Execution Instructions
Reviewers can run and test this project in two distinct configurations. Option A is highly recommended for standard evaluations, as it bypasses the need for local database engines and Ollama models.
Standard Developer Mock Mode 
This mode runs the entire system using structured, local mock fallbacks. It allows you to evaluate the React user interface, check accessibility compatibility, and test dashboard interactions instantly.
Activate the Backend (Terminal Window 1):
cd backend
source venv/bin/activate
export MOCK_LLM="true"
python3 app.py
Launch the React Frontend (Terminal Window 2):
cd frontend
npm start
Open your browser and navigate to http://localhost:3000.
6. Project Verification & Testing
Before running the full web server, you can execute individual component-level integration tests to verify database connectivity, local model response times, and regex parsing success:
cd backend
source venv/bin/activate
python3 test_components.py
This verification script isolates each tier of your pipeline and outputs structured metrics to the terminal, confirming that the system is ready for live operational use.