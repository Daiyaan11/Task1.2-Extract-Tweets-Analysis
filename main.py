import os
import json
import re
import tweepy
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
load_dotenv()

# Twitter API credentials from .env file
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

def collect_tweets(query, geocode, max_tweets=100):
    """Collect tweets based on a query and save them to a JSON file."""
    tweets_data = []

    # Use geocode to limit tweets to Johannesburg area
    for tweet in tweepy.Cursor(api.search_tweets, q=query, geocode=geocode, lang="en", tweet_mode="extended").items(max_tweets):
        tweets_data.append(tweet._json)  # Save raw tweet data

    # Save to JSON file
    if not os.path.exists("data"):
        os.makedirs("data")
    with open("data/tweets.json", "w") as file:
        json.dump(tweets_data, file, indent=4)
    print(f"Collected {len(tweets_data)} tweets and saved to data/tweets.json")

def extract_hashtags(tweets):
    """Extract hashtags from a list of tweets."""
    hashtags = []
    for tweet in tweets:
        if "entities" in tweet and "hashtags" in tweet["entities"]:
            hashtags.extend([tag["text"].lower() for tag in tweet["entities"]["hashtags"]])
    return hashtags

def clean_tweet_text(text):
    """Clean tweet text by removing URLs, mentions, special characters, and extra whitespace."""
    text = re.sub(r"http\S+|www.\S+", "", text)  # Remove URLs
    text = re.sub(r"@\w+", "", text)             # Remove user mentions
    text = re.sub(r"#", "", text)                # Remove hashtag symbols
    text = re.sub(r"[^A-Za-z\s]", "", text)      # Remove special characters and numbers
    text = text.lower()                          # Convert to lowercase
    text = re.sub(r"\s+", " ", text).strip()     # Remove extra whitespace
    return text

# Define your search query and location (Johannesburg)
query = "(#servicedelivery OR #municipality OR #eskom OR #citypower OR #joburgwater) AND (complaint OR issue OR problem)"
geocode = "-26.2041,28.0473,30km"  # Latitude, longitude, and radius around Johannesburg

# Step 1: Collect tweets based on the query and location
collect_tweets(query, geocode)

# Step 2: Load tweet data and analyze hashtags
with open("data/tweets.json", "r") as file:
    tweets_data = json.load(file)

hashtags = extract_hashtags(tweets_data)
hashtag_counts = Counter(hashtags)
print("Most common hashtags:", hashtag_counts.most_common(10))

# Step 3: Preprocess and clean tweet texts
cleaned_texts = [clean_tweet_text(tweet["full_text"]) for tweet in tweets_data if "full_text" in tweet]
print("Sample cleaned tweet:", cleaned_texts[0] if cleaned_texts else "No tweets available")
