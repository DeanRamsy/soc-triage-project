# AI-Driven Multi-Modal Triage Assistant

**BSc Computer Science Final Project (CM3070)**  
*University of London*

This repository contains the source code for the AI-Driven Multi-Modal Triage Assistant prototype. The system parses raw MySQL network connection logs, formats them into structured prompts, and routes them through a local 0.5B parameter LLM to generate security triage classifications and explanations.


## 1. System Architecture

The project follows a three-tier Sense-Reason-Act loop:

* **Sense (Perception Layer):** Reads network connection records from a normalized 3NF MySQL database (`SOCTriage`).
* **Reason (Reasoning Layer):** Flask backend (`app.py`) querying a local Ollama instance running `qwen:0.5b` with strict temperature controls (0.1).
* **Act (Action Layer):** Regex parsing engine (`parser.py`) that converts unconstrained LLM text into structured JSON schema for a React dashboard (`App.js`).


## 2. Directory Structure

soc_triage_project/
├── backend/
│   ├── app.py                # Flask API server
│   ├── database.py           # MySQL connection manager
│   ├── parser.py             # Regex parser &amp; fallback logic
│   ├── test_components.py    # Unit tests for database, LLM, and parser
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/                  # React dashboard components
│   └── package.json          # Node dependencies
├── schema.sql                # MySQL relational schema &amp; sample data
└── README.md                 # Project manual


## 3\. Environment &amp; Prerequisites

* **Python:** 3.9+
* **Node.js:** v18+ and `npm`
* **MySQL:** v8.0+
* **Ollama:** Local installation with the `qwen:0.5b` model pulled (`ollama pull qwen:0.5b`)


## 4\. Setup Instructions

### Backend Setup

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


### Database Setup

mysql -u root -p -e "CREATE DATABASE SOCTriage;"
mysql -u root -p SOCTriage &lt; schema.sql


### Frontend Setup

cd frontend
npm install


## 5\. Running the Application

### Option A: Developer Mock Mode (Recommended for quick testing)

Runs the system using local mock responses without requiring MySQL or Ollama to be running.

**Terminal 1 (Backend):**

cd backend
source venv/bin/activate
export MOCK_LLM="true"
python3 app.py


**Terminal 2 (Frontend):**

cd frontend
npm start


Access the dashboard at `http://localhost:3000`.

### Option B: Live Mode (Requires local MySQL and Ollama)

**Terminal 1 (Backend):**

cd backend
source venv/bin/activate
unset MOCK_LLM
python3 app.py


**Terminal 2 (Frontend):**

cd frontend
npm start


## 6\. Testing

To verify component connectivity, parsing fallbacks, and local execution latency, run:

cd backend
source venv/bin/activate
python3 test_components.py