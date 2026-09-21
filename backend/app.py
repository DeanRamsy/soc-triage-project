# ============================================================================
# ATTRIBUTION: Asynchronous API request payloads and connection error-handling
# structures were adapted from the official Ollama API developer documentation
# (https://github.com/ollama/ollama) and standard Python Flask routing paradigms.
# ============================================================================
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import os
import logging

# Import our modular perception and action modules
from database import DatabaseManager
from parser import TriageParser

# Initialize Flask App with CORS enabled for frontend connection
app = Flask(__name__)
CORS(app)  # Enables cross-origin request sharing between React and Flask

# Configure logger
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = Flask.logging_log = logging.getLogger(__name__)

# Instantiate database manager (credentials can also be loaded via os.getenv)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "triage_app")
DB_PASS = os.getenv("DB_PASS") # Must be set in environment for security
if not DB_PASS:
    raise RuntimeError("Database connection password (DB_PASS) environment variable is missing. Server termination initiated.")
DB_NAME = os.getenv("DB_NAME", "SOCTriage")
db_manager = DatabaseManager(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen:0.5b")
MOCK_MODE = os.getenv("MOCK_LLM", "false").lower() == "true"

def construct_few_shot_prompt(log_data):
    """Step 3: Few-Shot Prompt Construction to anchor reasoning."""
    prompt = f"""You are an expert cybersecurity analyst. Analyze the network connection log and output ONLY valid JSON. Do not include any conversational text, greetings, or formatting ticks like ```json.

Example Input:
{{'Source_IP': '192.168.1.5', 'Dest_Port': 22, 'Protocol': 'tcp', 'Conn_State': 'S0', 'Service_Name': 'ssh'}}

Example Output:
{{
    "CLASSIFICATION": "Vulnerability",
    "CONFIDENCE_SCORE": 0.85,
    "EXPLANATION": "Connection attempt to SSH port 22 with state S0 indicates a potential scanning or brute-force attempt."
}}

Actual Input:
{log_data}

Actual Output:
"""
    return prompt

@app.route("/api/health", methods=["GET"])
def health_check():
    """Verify backend, database connectivity, and local LLM presence."""
    db_status = "Connected"
    llm_status = "Available"
    
    # 1. Test database connection
    try:
        conn = db_manager.get_connection()
        conn.close()
    except Exception:
        db_status = "Disconnected/Lab Offline"
        
    # 2. Test Ollama availability
    try:
        if not MOCK_MODE:
            response = requests.get("http://localhost:11434/", timeout=2)
            if response.status_code != 200:
                llm_status = "Unavailable"
        else:
            llm_status = "Mock Active"
    except Exception:
        llm_status = "Unavailable"
        
    return jsonify({
        "status": "Healthy" if db_status == "Connected" else "Degraded",
        "database": db_status,
        "local_llm": llm_status,
        "mock_mode": MOCK_MODE
    })

@app.route("/api/triage", methods=["GET", "POST"])
def run_triage():
    """
    Main triage endpoint. Extracts a batch of logs and processes them individually
    through the local Qwen pipeline, applying robust case-insensitive heuristics.
    """
    limit = request.args.get("limit", default=10, type=int)
    results = []
    
    try:
        # Extract network logs from the Perception layer (MySQL 3NF)
        batch_logs = db_manager.extract_triage_batch(limit=limit)
    except Exception as e:
        logger.warning(f"Database extract failed ({e}). Triggering black-box mock data fallback.")
        # Agile Fallback: Provide synthetic logs to keep developers unblocked
        batch_logs = [
            {"UID": "MOCK-001", "Timestamp": "2026-08-14 02:00:00", "Source_IP": "192.168.1.105", "Source_Port": 49152, "Dest_IP": "10.0.0.5", "Dest_Port": 22, "Protocol": "tcp", "Conn_State": "S0", "Service_Name": "ssh"},
            {"UID": "MOCK-002", "Timestamp": "2026-08-14 02:01:00", "Source_IP": "192.168.1.10", "Source_Port": 51221, "Dest_IP": "8.8.8.8", "Dest_Port": 53, "Protocol": "udp", "Conn_State": "SF", "Service_Name": "dns"},
            {"UID": "MOCK-003", "Timestamp": "2026-08-14 02:02:00", "Source_IP": "185.220.x.x", "Source_Port": 40129, "Dest_IP": "192.168.1.200", "Dest_Port": 443, "Protocol": "tcp", "Conn_State": "S0", "Service_Name": "ssl"}
        ][:limit]

    # Process logs through local AI reasoning pipeline
    for i, log in enumerate(batch_logs):
        start_time = time.time()
        uid = log.get("UID", f"UNK-{i}")
        
        # Prepare semantic inputs
        prompt = construct_few_shot_prompt(log)
        
        # Determine whether to execute live inference or use mock fallback
        if MOCK_MODE:
            # Deterministic Mock Fallback for speedy local development
            time.sleep(0.5)  # Simulate modest processing latency (500ms)
            if log.get("Dest_Port") == 22 or "185.220" in log.get("Source_IP", ""):
                model_output = 'CLASSIFICATION: vulnerability\nEXPLANATION: Connection to SSH port or suspicious external IP flagged with S0 state, indicating scans.'
            else:
                model_output = 'CLASSIFICATION: normal\nEXPLANATION: Established connection is consistent with authorized internal domain resolution.'
            latency_ms = (time.time() - start_time) * 1000
        else:
            try:
                # Query local Ollama instance
                response = requests.post(OLLAMA_URL, 
                    json={
                        "model": MODEL_NAME,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Rigid deterministic constraint
                            "num_predict": 150   # Max Token budget limit
                        }
                    }, timeout=10) # Protect against infinite loops
                response.raise_for_status()
                latency_ms = (time.time() - start_time) * 1000
                model_output = response.json().get("response", "")
            except Exception as e:
                logger.error(f"Inference engine failure for UID {uid}: {e}. Triggering heuristic fallback.")
                # Local service offline fallback
                model_output = "CLASSIFICATION: vulnerability\nEXPLANATION: Local inference server offline. Defaulted to vulnerability triage alert."
                latency_ms = (time.time() - start_time) * 1000

        # Pass generative output through advanced heuristic parser
        parsed_results = TriageParser.parse_llm_response(model_output)
        
        # Assemble unified triage object
        results.append({
            "uid": uid,
            "timestamp": str(log.get("Timestamp", "")),
            "source_ip": log.get("Source_IP"),
            "dest_port": log.get("Dest_Port"),
            "protocol": log.get("Protocol"),
            "conn_state": log.get("Conn_State"),
            "service_name": log.get("Service_Name"),
            "classification": parsed_results["classification"],
            "confidence_score": parsed_results["confidence_score"],
            "explanation": parsed_results["explanation"],
            "latency_ms": round(latency_ms, 0)
        })

    # Output statistics summary
    total_processed = len(results)
    avg_latency = sum(r["latency_ms"] for r in results) / total_processed if total_processed else 0
    success_rate = sum(1 for r in results if r["classification"] != "Unknown") / total_processed if total_processed else 0

    return jsonify({
        "total_processed": total_processed,
        "average_latency_ms": round(avg_latency, 0),
        "parsing_success_rate": round(success_rate * 100, 1),
        "triaged_alerts": results
    })

if __name__ == "__main__":
    logger.info("Initializing Flask triage app secure backend server...")
    # Run locally on Port 5000 (accessible internally to React)
    app.run(host="0.0.0.0", port=5000, debug=True)
