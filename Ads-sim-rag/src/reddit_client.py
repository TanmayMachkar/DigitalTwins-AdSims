import praw
from tqdm import tqdm
from src.config import *
from src.utils import save_json, utc_to_str

def get_reddit_instance():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

def fetch_post_info(post_url):
    """Fetch only basic post info (for timestamp filtering)."""
    reddit = get_reddit_instance()
    submission = reddit.submission(url=post_url)
    submission.comments.replace_more(limit=0)

    post_info = {
        "id": submission.id,
        "title": submission.title,
        "num_comments": len(submission.comments),
        "created_utc": submission.created_utc,  # internal use only
        "created_str": utc_to_str(submission.created_utc),
        "commenters": [c.author.name for c in submission.comments if c.author]
    }
    save_json(post_info, f"{RAW_DIR}{submission.id}_post_meta.json")
    return post_info

def fetch_user_history_before(reddit, username, cutoff_timestamp, limit=300):
    """Fetch user's comments strictly before the cutoff date."""
    comments = []
    try:
        user = reddit.redditor(username)
        for c in user.comments.new(limit=limit):
            if c.created_utc < cutoff_timestamp:
                comments.append({
                    "body": c.body,
                    "subreddit": str(c.subreddit),
                    "created_utc": c.created_utc
                })
    except Exception as e:
        print(f"[WARN] Could not fetch user {username}: {e}")
    return comments

def fetch_commenters_histories(post_url):
    reddit = get_reddit_instance()
    post_info = fetch_post_info(post_url)
    cutoff = post_info["created_utc"]

    print(f"\nFetching user histories before {post_info['created_str']}...\n")
    all_users = {}
    for username in tqdm(post_info["commenters"]):
        history = fetch_user_history_before(reddit, username, cutoff)
        if history:
            all_users[username] = history

    save_json(all_users, f"{RAW_DIR}{post_info['id']}_user_histories.json")
    return all_users, post_info
