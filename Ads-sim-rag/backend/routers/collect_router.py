import json
import os
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.reddit_client import fetch_commenters_histories
from src.twin_builder import build_twin_profiles
from src.rag_engine import create_vector_db
from src.config import RAW_DIR, PROCESSED_DIR

router = APIRouter()


def event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


async def run_collect_pipeline(url: str):
    try:
        yield event({"type": "log", "message": f"Starting data collection for: {url}"})

        yield event({"type": "log", "message": "Fetching Reddit post and user histories..."})
        user_histories, post_info = fetch_commenters_histories(url)
        yield event({"type": "log", "message": f"Fetched {len(user_histories)} user histories for post '{post_info['title']}'"})

        histories_file = os.path.join(RAW_DIR, f"{post_info['id']}_user_histories.json")

        yield event({"type": "log", "message": "Building digital twin profiles..."})
        build_twin_profiles(histories_file)
        yield event({"type": "log", "message": f"Twin profiles built in {PROCESSED_DIR}"})

        yield event({"type": "log", "message": "Indexing profiles into vector database..."})
        create_vector_db(PROCESSED_DIR)
        yield event({"type": "log", "message": "Vector database indexed and ready."})

        yield event({"type": "done", "post_id": post_info["id"]})

    except Exception as e:
        yield event({"type": "error", "message": str(e)})


@router.get("/collect")
async def collect(url: str):
    return StreamingResponse(
        run_collect_pipeline(url),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
