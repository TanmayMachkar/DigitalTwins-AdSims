import json
import os

import chromadb
from chromadb.utils import embedding_functions
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.simulator import simulate_reaction
from src.config import RAW_DIR, EMBEDDING_DIR

router = APIRouter()


def event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


async def run_simulate_pipeline(post_id: str):
    try:
        meta_file = os.path.join(RAW_DIR, f"{post_id}_post_meta.json")
        histories_file = os.path.join(RAW_DIR, f"{post_id}_user_histories.json")

        if not os.path.isfile(meta_file) or not os.path.isfile(histories_file):
            yield event({"type": "error", "message": f"No data found for post ID '{post_id}'. Run Collect & Index first."})
            return

        with open(meta_file, "r", encoding="utf-8") as f:
            post_info = json.load(f)
        with open(histories_file, "r", encoding="utf-8") as f:
            user_histories = json.load(f)

        yield event({"type": "log", "message": f"Post: {post_info['title']}"})
        yield event({"type": "log", "message": f"Simulating {len(user_histories)} users..."})

        # Instantiate chromadb and embedding function INSIDE the generator to avoid
        # module-level SentenceTransformer instantiation that causes import-time failures.
        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        chroma_client = chromadb.PersistentClient(path=EMBEDDING_DIR)
        collection = chroma_client.get_collection(name="user_memory", embedding_function=embed_fn)

        total = 0
        for username, _ in user_histories.items():
            twin_id = f"twin_{username}"
            yield event({"type": "log", "message": f"Simulating {username}..."})
            response = simulate_reaction(post_info["title"], twin_id, collection)
            yield event({"type": "card", "username": username, "response": response})
            total += 1

        yield event({"type": "done", "total": total})

    except Exception as e:
        yield event({"type": "error", "message": str(e)})


@router.get("/simulate")
async def simulate(post_id: str):
    return StreamingResponse(
        run_simulate_pipeline(post_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
