# finetuning/prepare_dataset.py

import json
import logging
import os
from transformers import AutoTokenizer
from tqdm import tqdm

RAW_DATA_FILE = "data/raw/1oe62zw_user_histories.json"
OUTPUT_DIR = "data/processed/user_datasets/"
BASE_MODEL = "meta-llama/Meta-Llama-3-8B"

LLAMA3_CHAT_TEMPLATE = (
    "{{ bos_token }}"
    "{% for message in messages %}"
        "{{ '<|start_header_id|>' + message['role'] + '<|end_header_id|>\n\n' + message['content'] | trim + '<|eot_id|>' }}"
    "{% endfor %}"
    "{% if add_generation_prompt %}"
        "{{ '<|start_header_id|>assistant<|end_header_id|>\n\n' }}"
    "{% endif %}"
)

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/prepare_dataset.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main():
    logger.info(f"Loading tokenizer ({BASE_MODEL})...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    except Exception as e:
        logger.error(f"Failed to load tokenizer. Are you logged in? (huggingface-cli login)")
        logger.error(f"Error: {e}")
        return

    if tokenizer.chat_template is None:
        logger.warning("tokenizer.chat_template is None. Manually setting Llama-3 template.")
        tokenizer.chat_template = LLAMA3_CHAT_TEMPLATE

    logger.info(f"Reading raw data from {RAW_DATA_FILE}")
    with open(RAW_DATA_FILE, 'r', encoding='utf-8') as f:
        user_histories = json.load(f)

    logger.info(f"Loaded histories for {len(user_histories)} users.")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_users = 0
    for username, comments in tqdm(user_histories.items(), desc="Processing users"):
        if not comments:
            logger.warning(f"No comments for {username}, skipping.")
            continue

        output_file_path = os.path.join(OUTPUT_DIR, f"{username}.jsonl")
        total_comments_for_user = 0

        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            for comment in comments:
                body = comment.get('body')
                if not body or len(body.split()) < 5:
                    continue

                messages = [
                    {"role": "system", "content": f"You are a Reddit user named {username}."},
                    {"role": "user", "content": "Write a typical Reddit comment."},
                    {"role": "assistant", "content": body}
                ]

                try:
                    formatted_text = tokenizer.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=False
                    ) + tokenizer.eos_token
                except Exception as e:
                    logger.error(f"Failed to apply chat template: {e}")
                    return

                f_out.write(json.dumps({"text": formatted_text}) + "\n")
                total_comments_for_user += 1

        logger.info(f"Created {output_file_path} with {total_comments_for_user} comments.")
        total_users += 1

    logger.info(f"Done. Processed {total_users} users into {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
