# finetuning/train.py

import torch
import argparse # <-- Import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

# --- Configuration (now set in main) ---
BASE_MODEL = "meta-llama/Meta-Llama-3-8B"

def main():
    # --- NEW: Add argument parser ---
    parser = argparse.ArgumentParser(description="Train a LoRA adapter for a specific user.")
    parser.add_argument("--user", type=str, required=True, help="The username to train on (e.g., 'ricky-from-scotland')")
    args = parser.parse_args()

    # --- NEW: Paths are now dynamic based on the user ---
    TRAIN_DATA = f"data/processed/user_datasets/{args.user}.jsonl"
    OUTPUT_DIR = f"models/{args.user}-lora-adapter" # Save adapter to a user-specific folder
    
    print(f"--- Starting LoRA training for user: {args.user} ---")
    print(f"Reading data from: {TRAIN_DATA}")
    print(f"Saving adapter to: {OUTPUT_DIR}")

    # 1. Load Dataset
    print("Loading dataset...")
    dataset = load_dataset("json", data_files=TRAIN_DATA, split="train")

    # 2. Configure 4-bit Quantization (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    # 3. Load Base Model
    print("Loading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False

    # 4. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # 5. Configure LoRA
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
    )
    
    # 6. Configure Training Arguments
    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_train_epochs=3,  # <-- Increased epochs to 3 for better learning on small data
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_strategy="epoch",
        optim="paged_adamw_8bit",
        lr_scheduler_type="cosine",
        max_length=512,
        dataset_text_field="text",
        packing=True,
    )

    # 7. Initialize Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        processing_class=tokenizer,
        args=training_args,
    )

    # 8. Train!
    print("Starting training...")
    trainer.train()

    # 9. Save the adapter
    print(f"Training complete. Saving adapter to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)

if __name__ == "__main__":
    main()