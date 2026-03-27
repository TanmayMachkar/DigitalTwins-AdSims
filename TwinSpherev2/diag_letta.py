import os
from letta_client import Letta
from dotenv import load_dotenv

load_dotenv()
client = Letta(
    base_url=os.getenv("LETTA_SERVER_URL", "http://localhost:8282")
)

print("\n--- Listing Models Handles (v1.x style) ---")
try:
    # Let's see what's currently synced
    models = list(client.models.list())
    for m in models:
        print(f"Handle: {m.handle}, ID: {m.id}, Provider: {m.provider_name or 'N/A'}")
except Exception as e:
    print(f"Error checking models: {e}")

print("\n--- Listing Providers (v1.x style) ---")
try:
    # Some versions have it under client.providers, others have it nested
    # Since client.providers failed, it might be an internal helper or CLI-only
    print("Trying to find provider list...")
    # Actually, in some clients it's hidden. Let's try to see if it's there as a property
    print(f"Has providers? {hasattr(client, 'providers')}")
    print(f"Has models? {hasattr(client, 'models')}")
except Exception as e:
    print(f"Error: {e}")
