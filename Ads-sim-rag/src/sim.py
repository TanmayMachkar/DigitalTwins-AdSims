# src/simulator.py

from openai import OpenAI
from src.rag_engine import retrieve_context
from src.config import OPENAI_API_KEY

# Initialize the client to use your local Ollama server
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def simulate_reaction(post_text, twin_id, collection):
    
    # 1. Retrieve context *only* for the specific twin
    retrieved_contexts = retrieve_context(post_text, collection, twin_id)
    
    if not retrieved_contexts:
        print(f"[Warn] No historical context found for {twin_id} relevant to the post.")
        context_text = "No specific memories found."
    else:
        context_text = "\n\n".join(retrieved_contexts)

    # 2. Create the prompt
    prompt = f"""
You are simulating a Reddit user twin ({twin_id}).

Here are some of their previous Reddit comments. Use these to understand their tone, opinions, and style:
---
{context_text}
---

A new Reddit post has appeared with the title:
"{post_text}"

Based *only* on the persona from the comments above, generate a realistic Reddit comment this twin would likely write in response to the post.
"""
    
    # 3. Call your custom-trained model
    completion = client.chat.completions.create(
        model="my-reddit-expert",  # <-- Uses your new finetuned model
        messages=[
            {"role": "system", "content": "You are a simulated Reddit user twin, adopting the persona of past comments to respond to a new post."},
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content