import os
from letta_client import Letta
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("LETTA_API_KEY")
print(f"Key found: {key[:10]}...{key[-5:] if key else 'None'}")

try:
    client = Letta(token=key)
    # Try a simple list tools call which is usually low impact
    tools = client.tools.list()
    print(f"Success! Found {len(tools)} tools.")
except Exception as e:
    print(f"Failed: {e}")
