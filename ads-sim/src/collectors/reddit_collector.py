import os, json
from pathlib import Path
import praw
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
OUT_DIR = Path("data/raw_reddit")
OUT_DIR.mkdir(parents=True, exist_ok=True)

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

def fetch_subreddit_recent_posts(subreddit, limit=500):
    posts = []
    for p in tqdm(reddit.subreddit(subreddit).hot(limit=limit)):
        posts.append({
            "id": p.id,
            "title": p.title,
            "selftext": p.selftext,
            "author": str(p.author) if p.author else None,
            "created_utc": p.created_utc,
            "score": p.score,
            "num_comments": p.num_comments,
            "subreddit": subreddit
        })
    out_path = OUT_DIR / f"{subreddit}_posts.json"
    out_path.write_text(json.dumps(posts, indent=2))
    print("Saved", out_path)

if __name__ == "__main__":
    fetch_subreddit_recent_posts("running", limit=1000)
    fetch_subreddit_recent_posts("Fitness", limit=1000)