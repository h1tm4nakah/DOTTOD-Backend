import tweepy
import datetime
import os
from parole_politiche.models.exhibition import Participant


class TwitterClient(object):
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY", "")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET", "")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

    client = tweepy.Client(bearer_token=bearer_token)

    @staticmethod
    def get_tweets(user: Participant, date: datetime.date = None):
        start_date = date if date else datetime.datetime.now() - datetime.timedelta(days=1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date if date else datetime.datetime.now() - datetime.timedelta(days=1)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
        print("-------------------------------------------------------------------------")
        print(f"Fetching tweets for user {user.username} from {start_date} to {end_date}")
        response = TwitterClient.client.get_users_tweets(
            id=user.twitter_id,
            exclude=['retweets', 'replies'],
            start_time=start_date,
            end_time=end_date,
            tweet_fields=["public_metrics", "created_at"],
            max_results=50,
        )
        print(f"-- Found {len(response.data)} tweets")
        return response.data
