# src/rag_engine.py

import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from src.config import OPENAI_API_KEY, EMBEDDING_DIR
import json, os

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

os.makedirs(EMBEDDING_DIR, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=EMBEDDING_DIR)

def create_vector_db(user_dir="data/processed/"):
    collection = chroma_client.get_or_create_collection(
        name="user_memory",
        embedding_function=embed_fn,
        metadata={"description": "Reddit twin memory DB"}
    )

    for file in os.listdir(user_dir):
        # --- THE FIX ---
        # Only process files that end with .json
        if file.endswith(".json"):
            path = os.path.join(user_dir, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for i, text in enumerate(data["source_comments"]):
                        print(f"Embedding {data['twin_id']} comment {i+1}/{len(data['source_comments'])}")
                        collection.add(
                            ids=[f"{data['twin_id']}_{i}"],
                            documents=[text],
                            metadatas={"user": data["twin_id"]}
                        )
            except json.JSONDecodeError:
                print(f"[WARN] Skipping file {file} as it is not valid JSON.")
            except Exception as e:
                print(f"[ERROR] Could not process file {file}: {e}")
    
    return collection

def retrieve_context(query, collection, twin_id, top_k=5):
    """
    Retrieve context specifically for the given twin_id.
    """
    results = collection.query(
        query_texts=[query], 
        n_results=top_k,
        where={"user": twin_id}  # Filter by metadata
    )
    
    if not results["documents"] or not results["documents"][0]:
        print(f"[Warn] No context found for twin_id: {twin_id}")
        return []

    return results["documents"][0]