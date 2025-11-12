# finetuning/merge_model.py

import torch
import argparse # <-- Import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

# --- Configuration ---
BASE_MODEL = "meta-llama/Meta-Llama-3-8B"
OFFLOAD_DIR = "models/offload"

def main():
    # --- NEW: Add argument parser ---
    parser = argparse.ArgumentParser(description="Merge a user's LoRA adapter into the base model.")
    parser.add_argument("--user", type=str, required=True, help="The username of the adapter to merge")
    args = parser.parse_args()
    
    # --- NEW: Paths are now dynamic based on the user ---
    ADAPTER_PATH = f"models/{args.user}-lora-adapter"
    OUTPUT_PATH = f"models/llama-3-8b-{args.user}-expert"

    print(f"--- Merging model for user: {args.user} ---")
    print(f"Loading base model: {BASE_MODEL}")
    os.makedirs(OFFLOAD_DIR, exist_ok=True)

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    print(f"Loading adapter: {ADAPTER_PATH}")
    model_to_merge = PeftModel.from_pretrained(
        base_model, 
        ADAPTER_PATH, 
        offload_dir=OFFLOAD_DIR
    )

    print("Merging adapter into base model...")
    merged_model = model_to_merge.merge_and_unload()
    print("Merge complete.")

    print(f"Saving merged model to {OUTPUT_PATH}...")
    merged_model.save_pretrained(OUTPUT_PATH)
    tokenizer.save_pretrained(OUTPUT_PATH)
    print("Done.")

if __name__ == "__main__":
    main()