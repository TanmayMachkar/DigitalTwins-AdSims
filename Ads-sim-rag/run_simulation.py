import csv
import os
from src.reddit_client import fetch_commenters_histories
from src.twin_builder import build_twin_profiles
from src.rag_engine import create_vector_db
from src.simulator import simulate_reaction

POST_URL = "https://www.reddit.com/r/animequestions/comments/1krk2jt/which_one_do_yall_prefer_naruto_or_one_piece/"
OUTPUT_CSV = "simulation_results.csv"
CSV_HEADER = ["username", "predicted_response", "post_url"]

print("Fetching user histories...")
user_histories, post_info = fetch_commenters_histories(POST_URL)
print("Data fetching complete.")

print("Building twin profiles...")
build_twin_profiles(f"data/raw/{post_info['id']}_user_histories.json")
print("Twin profiles built.")

# quit()

print("Creating vector database...")
collection = create_vector_db("data/processed/")
print("Vector database ready.")

print(f"Loading existing data from {OUTPUT_CSV} (if any)...")
all_results = {}
if os.path.isfile(OUTPUT_CSV):
    try:
        with open(OUTPUT_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_results[row["username"]] = row
        print(f"Loaded {len(all_results)} existing records.")
    except Exception as e:
        print(f"Could not read {OUTPUT_CSV}: {e}")

print(f"Starting simulation for {len(user_histories)} users...")
for username in user_histories.keys():
    print(f"--- Simulating for: {username} ---")
    
    predicted_response = simulate_reaction(
        post_info["title"], 
        f"twin_{username}", 
        collection
    )
    
    print(f"🧠 Simulated reaction by {username}:\n{predicted_response}\n")
    
    new_row = {
        "username": username, 
        "predicted_response": predicted_response, 
        "post_url": POST_URL
    }
    
    all_results[username] = new_row

print(f"\nSaving all {len(all_results)} results to {OUTPUT_CSV}...")
try:
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(all_results.values())
    
    print("✅ Successfully saved all results.")

except Exception as e:
    print(f"❌ Error saving to CSV: {e}")