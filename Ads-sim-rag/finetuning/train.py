# finetuning/train.py

import logging
import os
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

BASE_MODEL = "meta-llama/Meta-Llama-3-8B"

os.makedirs("logs", exist_ok=True)


def get_logger(user: str) -> logging.Logger:
    logger = logging.getLogger("train")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(f"logs/train_{user}.log")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def main():
    parser = argparse.ArgumentParser(description="Train a LoRA adapter for a specific user.")
    parser.add_argument("--user", type=str, required=True, help="The username to train on (e.g., 'ricky-from-scotland')")
    args = parser.parse_args()

    logger = get_logger(args.user)

    TRAIN_DATA = f"data/processed/user_datasets/{args.user}.jsonl"
    OUTPUT_DIR = f"models/{args.user}-lora-adapter"

    logger.info(f"Starting LoRA training for user: {args.user}")
    logger.info(f"Reading data from: {TRAIN_DATA}")
    logger.info(f"Saving adapter to: {OUTPUT_DIR}")

    logger.info("Loading dataset...")
    dataset = load_dataset("json", data_files=TRAIN_DATA, split="train")
    logger.info(f"Dataset loaded: {len(dataset)} examples")

    logger.info("Configuring 4-bit quantization (QLoRA)...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    logger.info(f"Loading base model: {BASE_MODEL}")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False
    logger.info("Base model loaded.")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    logger.info("Configuring LoRA...")
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
    )

    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=10,
        save_strategy="epoch",
        optim="paged_adamw_8bit",
        lr_scheduler_type="cosine",
        max_length=512,
        dataset_text_field="text",
        packing=True,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        processing_class=tokenizer,
        args=training_args,
    )

    logger.info("Starting training...")
    trainer.train()

    logger.info(f"Training complete. Saving adapter to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    logger.info("Adapter saved successfully.")


if __name__ == "__main__":
    main()
