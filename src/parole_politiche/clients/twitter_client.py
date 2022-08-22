import tweepy
import datetime
import os
from parole_politiche.models.exhibition import Participant, Piece
from parole_politiche import db
import requests
import logging

class TwitterClient(object):
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")
    consumer_key = os.getenv("TWITTER_CONSUMER_KEY", "")
    consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET", "")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

    # To fetch tweets
    client = tweepy.Client(bearer_token=bearer_token)
    # To reply to tweets
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    reply_client = tweepy.API(auth)


    @staticmethod
    def get_tweets(user: Participant, date: datetime.date = None):
        start_date = date if date else datetime.datetime.now() - datetime.timedelta(days=1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date if date else datetime.datetime.now() - datetime.timedelta(days=1)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
        logging.log(logging.INFO, "-------------------------------------------------------------------------")
        logging.log(logging.INFO, f"Fetching tweets for user {user.username} from {start_date} to {end_date}")
        response = TwitterClient.client.get_users_tweets(
            id=user.twitter_id,
            exclude=['retweets', 'replies'],
            start_time=start_date,
            end_time=end_date,
            tweet_fields=["public_metrics", "created_at"],
            max_results=50,
        )
        logging.log(logging.INFO, f"-- Found {len(response.data) if response.data else 0} tweets")
        return response.data

    @staticmethod
    def reply_to_tweet(piece: Piece):
        '''
        Max 140 char reply
        '''
        if piece.tweet_response_id is not None:
            logging.log(logging.ERROR, f"The piece already has a response {piece.tweet_response_id}")
            return

        filename = f"DOEST_gallery_artwork"
        prompt = f"@{piece.account_username} Questa immagine è stata generata " \
                 f"da una intelligenza artificiale (AI) con con il testo di " \
                 f"questo tweet. https://doest-work.com/piece/{piece.tweet_id}"

        request = requests.get(piece.artifact_url_1, stream=True)
        if request.status_code == 200:
            with open(filename, 'wb') as image:
                for chunk in request:
                    image.write(chunk)

            res = TwitterClient.reply_client.update_status_with_media(
                filename=filename,
                status=prompt,
                in_reply_to_status_id=piece.tweet_id,
            )
            logging.log(logging.INFO, f"Generated response object with ID: {res.id_str}")

            piece.tweet_response_id = res.id_str
            db.session.commit()

            os.remove(filename)
        else:
            logging.log(logging.ERROR, f"Unable to download image for piece {piece}")


