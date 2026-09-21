import os
import sys
import requests
import time

# Incorporate our local directory path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from parser import TriageParser

# Safely extract database password from the environment variable
DB_PASS = os.getenv("DB_PASS")

print("====================================================")
print("[Step 2.1] Initializing Core Local Triage Components")
print("====================================================")

if not DB_PASS:
    print("[Error] DB_PASS environment variable not found!")
    print("Please set it in your terminal first: export DB_PASS='your_password'")
    sys.exit(1)

# 1. Establish Database Extraction Connection
print("\n[Step 2.2] Testing MySQL 3NF Database Extraction...")
try:
    db = DatabaseManager(password=DB_PASS)
    # Fetch 1 sample connection log
    logs = db.extract_triage_batch(limit=1)
    if logs:
        test_log = logs[0]  # Assign the first log from the list
        print(f"|-- SUCCESS: Log retrieved from database!")
        print(f"|   +-- UID: {test_log['UID']}")
        print(f"|   +-- Timestamp: {test_log['Timestamp']}")
        print(f"|   +-- Source IP: {test_log['Source_IP']}")
        print(f"|   +-- Dest Port: {test_log['Dest_Port']}")
        print(f"|   +-- Service Guess: {test_log['Service_Name']}")
    else:
        print("|-- WARNING: Database connection successful, but table is empty.")
        sys.exit(1)
except Exception as e:
    print(f"|-- FAILURE: Could not connect or query database. Details: {e}")
    sys.exit(1)

# 2. Query Local Ollama Server
print("\n[Step 2.3] Testing Local Ollama Inference (qwen:0.5b)...")
ollama_url = "http://localhost:11434/api/generate"
test_prompt = f"""You are an expert cybersecurity analyst. Analyze this log and output strictly in this format:
CLASSIFICATION: normal
EXPLANATION: Connection to DNS port 53 matches expected corporate network resolution patterns.

Log to analyze:
{test_log}
"""

payload = {
    "model": "qwen:0.5b",
    "prompt": test_prompt,
    "stream": False,
    "options": {
        "temperature": 0.1,  # Set a low temperature to restrict model randomness
        "num_predict": 120   # Cap output generation to protect Mac memory bounds
    }
}

try:
    start_time = time.time()
    response = requests.post(ollama_url, json=payload, timeout=15)
    response.raise_for_status()
    latency_ms = (time.time() - start_time) * 1000
    raw_response = response.json().get("response", "")
    print(f"|-- SUCCESS: Local model generated response in {round(latency_ms, 0)}ms.")
    print(f"|-- Raw LLM Output:\n{raw_response}")
except Exception as e:
    print(f"|-- FAILURE: Could not communicate with Ollama server: {e}")
    print("Please verify that the Ollama app is open and running on your Mac.")
    sys.exit(1)

# 3. Test Parser Integration
print("\n[Step 2.4] Testing Heuristic Regex Extraction...")
try:
    parsed_results = TriageParser.parse_llm_response(raw_response)
    print("|-- SUCCESS: Heuristic normalizer successfully parsed output.")
    print(f"|   +-- Normalised Classification: {parsed_results['classification']}")
    print(f"|   +-- Confidence Assessment: {parsed_results['confidence_score']}")
    print(f"|   +-- Extracted Explanation: {parsed_results['explanation']}")
except Exception as e:
    print(f"|-- FAILURE: Parser error: {e}")
    sys.exit(1)

print("\n====================================================")
print("             ALL LOCAL VERIFICATIONS PASSED         ")
print("====================================================")