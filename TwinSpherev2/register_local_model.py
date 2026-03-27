import os
from letta_client import Letta
from dotenv import load_dotenv

load_dotenv()
client = Letta(
    base_url=os.getenv("LETTA_SERVER_URL", "http://localhost:8282")
)

print("--- Registering OpenRouter Model Locally ---")
try:
    # In Letta v1.7.x, you can create a model handle
    # We use the 'openai' provider type since OpenRouter is OpenAI-compatible,
    # and we already passed the OPENROUTER_API_KEY to Docker.
    model = client.models.create(
        handle="openai/gpt-4o-mini",
        model_type="llm",
        context_window=128000
    )
    print(f"Successfully registered model: {model.handle} (ID: {model.id})")
except Exception as e:
    print(f"Error registering model: {e}")
    if "already exists" in str(e):
        print("Model already exists, proceeding...")

try:
    # Also register the embedding model handle
    emb = client.models.create(
        handle="letta/letta-free",
        model_type="embedding",
        context_window=8192
    )
    print(f"Successfully registered embedding: {emb.handle}")
except Exception as e:
    print(f"Note: {e}")
