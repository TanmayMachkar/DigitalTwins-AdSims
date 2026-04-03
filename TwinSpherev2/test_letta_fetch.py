import os
from letta_client import Letta
from dotenv import load_dotenv

load_dotenv()
client = Letta(
    api_key=os.getenv("LETTA_API_KEY"),
    base_url=os.getenv("LETTA_SERVER_URL", "https://api.letta.com")
)
agents_page = client.agents.list()
print("Type of agents_page:", type(agents_page))
print("Has data?", hasattr(agents_page, 'data'))

try:
    agents_list = list(agents_page)
    print("Successfully converted to list! Length:", len(agents_list))
except Exception as e:
    print("Error converting to list:", e)
