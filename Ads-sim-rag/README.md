# Ad Simulation with Digital Twins

## Fine-Tuning Pipeline

**1. Prepare dataset**
Converts raw Reddit user histories into JSONL chat format for training.
```bash
python finetuning/prepare_dataset.py
```

**2. Train LoRA adapter**
Fine-tunes a LoRA adapter on top of LLaMA 3 8B using QLoRA (4-bit quantization) for a specific user.
```bash
python finetuning/train.py --user <username>
```

**3. Merge adapter into base model**
Merges the trained LoRA adapter into the base LLaMA 3 8B model to produce a standalone model.
```bash
python finetuning/merge_model.py --user <username>
```

**4. Convert to GGUF**
Converts the merged HuggingFace model to GGUF format for use with Ollama.
```bash
python convert_hf_to_gguf.py <path_to_merged_model> --outfile <output_path>.gguf --outtype q8_0
```

**5. Load into Ollama**
Registers the GGUF model in Ollama using a Modelfile that sets the user persona.
```bash
ollama create <model-name> -f <OllamaModelfile>
```

**6. Run the model**
Starts an interactive session with the fine-tuned persona model.
```bash
ollama run <model-name> "<prompt>"
```

---

## Simulation Pipeline

**collect.py**
Fetches Reddit post metadata and commenter histories using the Reddit API, then builds digital twin profiles for each user. Skips users already collected.
```bash
python collect.py --url <reddit_post_url>
```

**index.py**
Embeds all twin profile comments into a ChromaDB vector database using `all-MiniLM-L6-v2`. Skips users already indexed. Safe to re-run after adding new profiles.
```bash
python index.py
```

**simulate.py**
Simulates each user's reaction to the Reddit post using RAG-retrieved context and LLaMA 3 8B via Ollama. Skips users already simulated. Results are saved to a CSV file named after the post ID.
```bash
python simulate.py --post-id <post_id>
python simulate.py --post-id <post_id> --limit 10
```

---

## Running

To start both the backend and frontend servers, run:
```bash
start.bat
```

This will open two command windows:
- **Backend**: Running on `http://localhost:8000`
- **Frontend**: Running on `http://localhost:5173`
