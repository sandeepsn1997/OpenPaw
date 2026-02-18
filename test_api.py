import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    try:
        res = requests.get(f"{BASE_URL}/health")
        print(f"Health: {res.status_code}, {res.json()}")
    except Exception as e:
        print(f"Health failed: {e}")

def test_dashboard():
    try:
        res = requests.get(f"{BASE_URL}/dashboard/stats")
        print(f"Dashboard: {res.status_code}, {res.json()}")
    except Exception as e:
        print(f"Dashboard failed: {e}")

def test_agents():
    try:
        # Create an agent
        agent_data = {
            "model_name": "llama-3.3-70b-versatile",
            "temperature": 0.5,
            "max_tokens": 1024,
            "system_prompt": "You are a test agent."
        }
        res = requests.post(f"{BASE_URL}/agents?name=TestAgent", json=agent_data)
        print(f"Create Agent: {res.status_code}, {res.json()}")
        
        # List agents
        res = requests.get(f"{BASE_URL}/agents")
        print(f"List Agents: {res.status_code}, {len(res.json())} agents found")
    except Exception as e:
        print(f"Agents failed: {e}")

if __name__ == "__main__":
    test_health()
    test_dashboard()
    test_agents()
