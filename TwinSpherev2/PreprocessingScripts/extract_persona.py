import pandas as pd
import json
import time
import random
import requests
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Load environment variables from the root .env file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, '.env')
load_dotenv(env_path)

# Config
# Note: The .env file uses OPENROUTER_API_KEY
OPEN_ROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPEN_ROUTER_API_KEY:
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")

if OPEN_ROUTER_API_KEY:
    print(f"[i] API Key found (ends with ...{OPEN_ROUTER_API_KEY[-4:]})")
else:
    print("[!] ERROR: OPENROUTER_API_KEY not found in .env or environment.")

# Prompt Template
def build_prompt(tweet_block):
    return f"""
Analyze the following Twitter content from a user. Based on their language, common themes, and overall behavior expressed in these tweets, infer the following personality traits. Output the results as a detailed persona paragraph.

1.  **Interests/Topics:** List 3-5 keywords or phrases describing their main interests and the topics they discuss.
2.  **Communication Style & Tone:** Describe how they express themselves.
3.  **General Sentiment:** Describe their overall emotional leaning.
4.  **Engagement Patterns:** Describe how they interact on the platform.

Ensure your output is a paragraph detailing the persona, using the points mentioned above. There should be nothing apart from this paragraph in your output.

The following Content section contains the latest 100 tweets of the user concatenated together as a string and seperated by the separator "<ENDOFTWEET>"

Content: {tweet_block}
""".strip()

# Function to call OpenRouter with DeepSeek
def query_openrouter(prompt, model="deepseek/deepseek-chat"):
    if not OPEN_ROUTER_API_KEY:
        return "ERROR: Missing API Key"
        
    headers = {
        "Authorization": f"Bearer {OPEN_ROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/tanma/TwinSpherev2", 
        "X-Title": "TwinSphere Persona Extraction"
    }
    
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }

    # SSL V3 Alert bad record mac often happens due to network issues. 
    # Adding a simple retry mechanism.
    for attempt in range(3):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=45
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            elif response.status_code == 401:
                return f"ERROR: API error 401: {response.text} (Check your API key in .env)"
            else:
                return f"ERROR: API error {response.status_code}: {response.text}"
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            if attempt < 2:
                print(f"  - Attempt {attempt+1} failed ({e}). Retrying in 2 seconds...")
                time.sleep(2)
            else:
                return f"ERROR: Connection/SSL Error after 3 attempts: {e}"
        except Exception as e:
            return f"ERROR: Unexpected error: {e}"

def main():
    # Load Data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "grouped_concatenated_tweets.csv")
    
    if not os.path.exists(data_path):
        print(f"[!] Data source not found: {data_path}")
        return

    print(f"[i] Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    output_data = []

    # Sample 10 for testing as per the notebook logic
    num_to_process = 10
    sampled_df = df.sample(min(num_to_process, len(df)))
    
    # Ensure Data directory exists
    output_dir = os.path.join(parent_dir, "Data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"[+] Created directory: {output_dir}")
    output_csv = os.path.join(output_dir, "Persona.csv")

    # Iterate through rows and generate personas
    for i, (_, row) in enumerate(sampled_df.iterrows()):
        name = row["name"]
        tweets = row["concatenated_tweets"]
        print(f"[{i+1}/{len(sampled_df)}] Processing {name}...")

        try:
            prompt = build_prompt(tweets)
            response = query_openrouter(prompt)
            
            if response.startswith("ERROR:"):
                print(f"  [!] {response}")
                if "401" in response:
                    print("  [!] Stopping run to check credentials.")
                    break
            else:
                new_entry = {"name": name, "persona": response}
                output_data.append(new_entry)
                
                # Incremental Save
                if os.path.exists(output_csv):
                    try:
                        temp_df = pd.read_csv(output_csv)
                        temp_df = pd.concat([temp_df, pd.DataFrame([new_entry])], ignore_index=True)
                    except:
                        temp_df = pd.DataFrame([new_entry])
                else:
                    temp_df = pd.DataFrame([new_entry])
                
                temp_df.to_csv(output_csv, index=False)
                print(f"  [+] Saved persona for {name}")
                
            time.sleep(1.5)
        except Exception as e:
            print(f"  [!] Unexpected error for {name}: {e}")
            continue

    if output_data:
        print(f"\n[+] Finished. Successfully saved {len(output_data)} personas to {output_csv}")
    else:
        print("\n[!] No personas were successfully extracted.")

if __name__ == "__main__":
    main()
