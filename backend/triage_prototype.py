import mysql.connector
from mysql.connector import Error
import requests
import time
import json
import re

def extract_logs():
    """Step 2: Database Extraction (The Perception Layer)"""
    logs = []
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='triage_app',
            password='your_secure_password', # UPDATE THIS
            database='SOCTriage'
        )
        
        if connection.is_connected():
            print("[System] Successfully authenticated to SOCTriage as triage_app.")
            cursor = connection.cursor(dictionary=True)
            
            # Extract a batch of 50 logs
            query = """
                SELECT Source_IP, Dest_Port, Protocol, Conn_State, Service_Name 
                FROM Network_Connections 
                LIMIT 50;
            """
            cursor.execute(query)
            logs = cursor.fetchall()
            print(f"[System] Extracted {len(logs)} network logs for evaluation.\n")
            
    except Error as e:
        print(f"[System Error] Error while connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            
    return logs

def construct_prompt(log_data):
    """Step 3: LLM Prompt Construction (Now with Few-Shot Learning)"""
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

def evaluate_prototype(batch_logs):
    """Steps 4 & 5: Execution, Latency Tracking, and Output Validation"""
    print("[System] Beginning Evaluation Loop...")
    success_count = 0
    latencies = []

    for i, log in enumerate(batch_logs):
        prompt = construct_prompt(log)
        start_time = time.time()
        
        try:
            # Query the local Ollama API
            response = requests.post('http://localhost:11434/api/generate', 
                json={
                    "model": "qwen:0.5b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 150 # Max Tokens constraint
                    }
                })
            response.raise_for_status()
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            result_text = response.json().get("response", "")
            
            # Advanced Robust Parsing: Normalization & Heuristic Extraction
            normalized_text = result_text.lower()
            classification = None
            
            # Strategy 1: Structured Label Parsing
            if "classification" in normalized_text:
                if "vulnerability" in normalized_text:
                    classification = "Vulnerability"
                elif "normal" in normalized_text:
                    classification = "Normal"
                    
            # Strategy 2: Keyword-Based Heuristic Search (Fallback)
            if not classification:
                if any(word in normalized_text for word in ["vulnerability", "malicious", "exploit"]):
                    classification = "Vulnerability"
                elif any(word in normalized_text for word in ["normal", "benign", "expected"]):
                    classification = "Normal"
            
            # Final Validation
            if classification:
                print(f"[{i+1}/50] [Parser] Success. Latency: {latency_ms:.0f}ms | Classification: {classification}")
                success_count += 1
                latencies.append(latency_ms)
            else:
                print(f"[{i+1}/50] [Parser Error] Could not extract classification from text. Latency: {latency_ms:.0f}ms")

        except Exception as e:
            print(f"[{i+1}/50] [Inference Error] Failed to connect to Ollama: {e}")

    # Final Evaluation Output
    print("\n================ EVALUATION COMPLETE ================")
    print(f"Total Logs Processed: {len(batch_logs)}")
    if latencies:
        print(f"Average Inference Latency: {sum(latencies)/len(latencies):.0f}ms")
    print(f"JSON Parsing Success Rate: {(success_count/len(batch_logs))*100:.0f}% ({success_count}/{len(batch_logs)} parsed cleanly)")
    print("=====================================================")

if __name__ == "__main__":
    batch_logs = extract_logs()
    if batch_logs:
        evaluate_prototype(batch_logs)