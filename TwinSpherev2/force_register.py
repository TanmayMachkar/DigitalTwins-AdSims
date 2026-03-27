import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8282/v1"
OPENROUTER_KEY = "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"

def register_provider():
    print(f"Connecting to Local Letta at {BASE_URL}...")
    
    # Payload to register OpenAI-style provider (using OpenRouter)
    payload = {
        "name": "openai",
        "provider_type": "openai",
        "endpoint": "https://openrouter.ai/api/v1",
        "api_key": OPENROUTER_KEY
    }

    try:
        # Create Provider
        response = requests.post(f"{BASE_URL}/providers", json=payload)
        if response.status_code == 200 or response.status_code == 201:
            print("Successfully registered OpenRouter as the OpenAI provider!")
        else:
            print(f"Provider registration result: {response.status_code} - {response.text}")
            
        # List models to see if it synced
        models_resp = requests.get(f"{BASE_URL}/models")
        if models_resp.status_code == 200:
            models = models_resp.json()
            # In v1.x, the response might be a list or a dict with a 'data' key
            data = models.get('data', models) if isinstance(models, dict) else models
            print(f"\nAvailable Models now: {[m.get('handle') for m in data]}")
        
    except Exception as e:
        print(f"Error communicating with local Letta: {e}")

if __name__ == "__main__":
    register_provider()
