# # src/simulator.py

# from openai import OpenAI
# from src.rag_engine import retrieve_context
# from src.config import OPENAI_API_KEY

# client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# def simulate_reaction(post_text, twin_id, collection):

#     retrieved_contexts = retrieve_context(post_text, collection, twin_id)

#     if not retrieved_contexts:
#         print(f"[Warn] No historical context found for {twin_id} relevant to the post.")
#         context_text = "No specific memories found."
#     else:
#         context_text = "\n\n".join(retrieved_contexts)

#     # Create the prompt that gives the model its persona
#     prompt = f"""
#             You are {twin_id}, a Reddit user.
#             Here are some of your past comments, which show your tone, style, and interests:
#             ---
#             {context_text}
#             ---

#             A new Reddit post appears with the title:
#             "{post_text}"

#             Write a comment in your typical style and tone, using your general knowledge.
#             """

#     # --- DYNAMIC MODEL SELECTION ---
#     # twin_id is "twin_ricky-from-scotland"
#     # We need the model name, e.g., "ricky-expert"
#     base_username = twin_id.replace("twin_", "")
#     model_name = f"{base_username}-expert"

#     print(f"\n--- Loading persona model: {model_name} ---")

#     try:
#         completion = client.chat.completions.create(
#             model=model_name,  # <-- This is now dynamic!
#             messages=[
#                 {"role": "user", "content": prompt},
#             ]
#         )
#         response_text = completion.choices[0].message.content

#     except Exception as e:
#         print(f"[ERROR] Failed to get response from model {model_name}.")
#         print(f"Did you create this model in Ollama? Error: {e}")
#         # --- FALLBACK ---
#         # If the persona model fails, use the base llama3
#         print("--- FALLING BACK TO BASE LLAMA3 ---")
#         completion = client.chat.completions.create(
#             model="llama3",
#             messages=[
#                 {"role": "user", "content": prompt},
#             ]
#         )
#         response_text = completion.choices[0].message.content

#     return response_text

from openai import OpenAI
from src.rag_engine import retrieve_context
from src.config import OPENAI_API_KEY

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def simulate_reaction(post_text, twin_id, collection):
    
    # --- 1. RAG (This works perfectly) ---
    retrieved_contexts = retrieve_context(post_text, collection, twin_id)
    
    if not retrieved_contexts:
        print(f"[Warn] No historical context found for {twin_id} relevant to the post.")
        context_text = "No specific memories found."
    else:
        context_text = "\n\n".join(retrieved_contexts)

    # --- 2. The Final, Robust Prompt ---
    # This prompt tells the base 'llama3' model its role, its persona,
    # the context, and the task.
    prompt = f"""
You are a simulation assistant. Your task is to simulate a Reddit user named {twin_id}.
I will give you some of their past comments to help you understand their tone, style, and interests.
Then, I will give you a new Reddit post title, and you must generate a *plausible, new* Reddit comment that this user would write in English.

--- USER'S PAST COMMENTS ---
{context_text}
--- END OF PAST COMMENTS ---

A new Reddit post appears with the title:
"{post_text}"

Now, please generate a realistic Reddit comment from {twin_id}.
"""
    
    # --- 3. The Model (This is the fix) ---
    # We stop using the broken, finetuned model.
    # We use the smart, general-purpose 'llama3' model, which
    # is powerful enough to follow our prompt.
    model_name = "llama3" 
    
    print(f"\n--- Loading base model: {model_name} (with RAG context) ---")
    
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": f"You are simulating a Reddit user: {twin_id}."},
                {"role": "user", "content": prompt},
            ]
        )
        response_text = completion.choices[0].message.content
    
    except Exception as e:
        print(f"[ERROR] Failed to get response from model {model_name}: {e}")
        response_text = "[Simulation Failed]"

    return response_text