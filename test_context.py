import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_chat_context():
    print("--- Testing Chat Context ---")
    try:
        # 1. Create a conversation
        res = requests.post(f"{BASE_URL}/chat/conversations")
        conv_id = res.json()["conversation_id"]
        print(f"Created Conversation: {conv_id}")

        # 2. Tell the agent my name
        msg1 = "Hello! My name is Sandeep. Remember that."
        print(f"\nUser: {msg1}")
        res = requests.post(f"{BASE_URL}/chat", json={
            "conversation_id": conv_id,
            "message": msg1
        })
        print(f"Agent: {res.json()['reply']}")

        # 3. Ask for name
        msg2 = "What is my name?"
        print(f"\nUser: {msg2}")
        res = requests.post(f"{BASE_URL}/chat", json={
            "conversation_id": conv_id,
            "message": msg2
        })
        print(f"Agent: {res.json()['reply']}")

        # 4. Check if we can list it
        res = requests.get(f"{BASE_URL}/chat/conversations")
        print(f"\nList Conversations: Found {len(res.json())} sessions")

    except Exception as e:
        print(f"Chat Context Test failed: {e}")

if __name__ == "__main__":
    test_chat_context()
