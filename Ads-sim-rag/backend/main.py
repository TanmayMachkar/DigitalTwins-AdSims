import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.collect_router import router as collect_router
from backend.routers.simulate_router import router as simulate_router

app = FastAPI(title="TwinSphere API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(collect_router, prefix="/api")
app.include_router(simulate_router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}
