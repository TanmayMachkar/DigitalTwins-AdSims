from src.reddit_client import fetch_commenters_histories
from src.twin_builder import build_twin_profiles
from src.rag_engine import create_vector_db
from src.simulator import simulate_reaction

POST_URL = "https://www.reddit.com/r/Pretend2010Internet/comments/1oe62zw/who_will_have_a_better_carrermessi_vs_ronaldo/"
user_histories, post_info = fetch_commenters_histories(POST_URL)

build_twin_profiles(f"data/raw/{post_info['id']}_user_histories.json")

# quit()

collection = create_vector_db("data/processed/")

test_user = list(user_histories.keys())[0]
predicted_response = simulate_reaction(post_info["title"], f"twin_{test_user}", collection)

print(f"\n🧠 Simulated reaction by {test_user}:\n{predicted_response}")
