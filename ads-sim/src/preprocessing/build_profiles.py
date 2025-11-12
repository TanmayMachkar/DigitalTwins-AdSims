import json, random
from pathlib import Path
from collections import Counter
import numpy as np

RAW = Path("data/raw_reddit")
OUT = Path("data/twins")
OUT.mkdir(parents=True, exist_ok=True)

def extract_keywords(text):
    tokens = [t.lower().strip(".,!?()[]") for t in text.split()]
    return [t for t in tokens if len(t) > 3]

def build_profiles_from_subreddit_file(infile, max_profiles=200):
    posts = json.load(open(infile))
    authors = {}
    for p in posts:
        a = p.get("author") or f"anon_{random.randint(1,99999)}"
        authors.setdefault(a, []).append(p)
    profiles = []
    for user, user_posts in list(authors.items())[:max_profiles]:
        texts = " ".join([p.get("title","") + " " + (p.get("selftext") or "") for p in user_posts])
        kw = Counter(extract_keywords(texts)).most_common(20)
        interests = [k for k,_ in kw[:5]]
        profile = {
            "id": f"twin_{user}",
            "username": user,
            "activity_count": len(user_posts),
            "interests": interests,
            "post_times": [p["created_utc"] for p in user_posts],
            "history_sample": user_posts[:10],
            "price_sensitivity": float(np.clip(1 - min(1, len(user_posts)/100), 0.1, 1.0)),
            "channels": random.choice([["instagram","youtube"], ["tiktok","instagram"], ["youtube"], ["twitter","reddit"]])
        }
        profiles.append(profile)
    return profiles

if __name__ == "__main__":
    pfile = RAW / "running_posts.json"
    profiles = build_profiles_from_subreddit_file(str(pfile), max_profiles=300)
    for p in profiles:
        out = OUT / f"{p['id']}.json"
        out.write_text(json.dumps(p, indent=2))
    print("Wrote", len(profiles), "profiles")
