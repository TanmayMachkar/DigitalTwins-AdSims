# finetuning/merge_model.py

import logging
import os
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "meta-llama/Meta-Llama-3-8B"
OFFLOAD_DIR = "models/offload"

os.makedirs("logs", exist_ok=True)


def get_logger(user: str) -> logging.Logger:
    logger = logging.getLogger("merge")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(f"logs/merge_{user}.log")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def main():
    parser = argparse.ArgumentParser(description="Merge a user's LoRA adapter into the base model.")
    parser.add_argument("--user", type=str, required=True, help="The username of the adapter to merge")
    args = parser.parse_args()

    logger = get_logger(args.user)

    ADAPTER_PATH = f"models/{args.user}-lora-adapter"
    OUTPUT_PATH = f"models/llama-3-8b-{args.user}-expert"

    logger.info(f"Merging model for user: {args.user}")
    logger.info(f"Base model: {BASE_MODEL}")
    logger.info(f"Adapter: {ADAPTER_PATH}")
    logger.info(f"Output: {OUTPUT_PATH}")

    os.makedirs(OFFLOAD_DIR, exist_ok=True)

    logger.info("Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    logger.info("Base model loaded.")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    logger.info(f"Loading LoRA adapter from {ADAPTER_PATH}...")
    model_to_merge = PeftModel.from_pretrained(
        base_model,
        ADAPTER_PATH,
        offload_dir=OFFLOAD_DIR
    )

    logger.info("Merging adapter into base model...")
    merged_model = model_to_merge.merge_and_unload()
    logger.info("Merge complete.")

    logger.info(f"Saving merged model to {OUTPUT_PATH}...")
    merged_model.save_pretrained(OUTPUT_PATH)
    tokenizer.save_pretrained(OUTPUT_PATH)
    logger.info("Done. Merged model saved successfully.")


if __name__ == "__main__":
    main()
