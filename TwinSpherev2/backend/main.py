from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import tempfile
import shutil
import uuid
import asyncio
import os
from letta_client import Letta
from backend.simulation import run_simulation_with_image
from dotenv import load_dotenv
load_dotenv()

SHARED_BLOCK_LABEL = "public_reactions"

client = Letta(
    api_key=os.getenv("LETTA_API_KEY"),
    base_url=os.getenv("LETTA_SERVER_URL", "https://api.letta.com")
)

app = FastAPI()
 
@app.get("/")
def read_root():
    return {"status": "backend is running", "api": "TwinSphere AI API"}


# CORS setup for Streamlit UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simulate/")
async def simulate_post_with_image(
    image_url: str = Form(...),
    post_text: str = Form(...),
    post_id: str = Form(...)
):
    # Save uploaded image to temp file
    # image_path = None
    # if image:
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
    #         shutil.copyfileobj(image.file, tmp)
    #         image_path = tmp.name

    # Load all active agents
    try:
        url = os.getenv("LETTA_SERVER_URL", "https://api.letta.com")
        agents_page = client.agents.list()
        # Convert SyncArrayPage directly to a list to avoid len() errors
        agents = list(agents_page)
        
        print(f"[DEBUG] Connecting to: {url}")
        print(f"[DEBUG] Total agents found on Letta: {len(agents)}")
        
        if not agents:
            return {"error": "No agents found in your Letta account. Please run createagents.py first."}
            
    except Exception as e:
        print(f"[DEBUG] Error listing agents: {e}")
        return {"error": f"Failed to list agents: {str(e)}"}
    
    # blocks_page might be a SyncArrayPage
    blocks_page = client.blocks.list(label=SHARED_BLOCK_LABEL)
    existing = list(blocks_page)
    shared_block_id = existing[0].id if existing else None

    # Run simulation
    try:
        results = await run_simulation_with_image(
            agents=agents,
            post_id=post_id,
            post_text=post_text,
            image_url=image_url,
            shared_block_id=shared_block_id
        )
        return results
    except Exception as e:
        return {"error": f"Simulation failed: {str(e)}"}
