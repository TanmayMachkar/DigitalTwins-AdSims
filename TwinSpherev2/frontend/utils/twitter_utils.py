import re
import snscrape.modules.twitter as sntwitter

def extract_tweet_id_from_url(url: str) -> str:
    match = re.search(r'twitter\.com/.+/status/(\d+)', url)
    return match.group(1) if match else None

def fetch_tweet_content(tweet_url: str):
    tweet_id = extract_tweet_id_from_url(tweet_url)
    if not tweet_id:
        raise ValueError("Invalid Twitter URL format.")
    
    for tweet in sntwitter.TwitterTweetScraper(tweet_id).get_items():
        return {
            "text": tweet.content,
            "image_url": tweet.media[0].fullUrl if tweet.media else None,
            "username": tweet.user.username,
        }
    
    raise ValueError("Tweet not found.")