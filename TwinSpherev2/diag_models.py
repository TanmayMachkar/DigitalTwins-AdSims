import os
from letta_client import Letta
from dotenv import load_dotenv

load_dotenv()
client = Letta(
    base_url=os.getenv("LETTA_SERVER_URL", "http://localhost:8282")
)

print("\n--- EXACT GPT-4O-MINI HANDLE ---")
try:
    for m in list(client.models.list()):
        if "gpt-4o-mini" in m.handle.lower():
            print(f"FOUND: [{m.handle}]")
except Exception as e:
    print(f"Error checking models: {e}")
