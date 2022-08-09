from flask_restx import Model
from flask_restx.fields import String
from flask_restx.inputs import email
from flask_restx.reqparse import RequestParser
from datetime import datetime
from typing import Dict, List
from flask import request
from parole_politiche.models.exhibition import Piece

def array_type(value, name):
    full_json_data = request.get_json()
    my_list = full_json_data[name]
    if not isinstance(my_list, list):
        raise ValueError("The parameter " + name + " is not a valid array")
    return my_list


auth_reqparser = RequestParser(bundle_errors=True)
auth_reqparser.add_argument(
    name="email", type=email(), location="form", required=True, nullable=False
)
auth_reqparser.add_argument(
    name="password", type=str, location="form", required=True, nullable=False
)

admin_tweet_date_parser = RequestParser(bundle_errors=True)
admin_tweet_date_parser.add_argument(
    "date", location="args", type=lambda date: datetime.strptime(date, '%d/%m/%Y'), store_missing=False
)
admin_tweet_date_parser.add_argument(
    "usernames", location="args",action='split', store_missing=False
)

admin_tweet_submit_parser = RequestParser(bundle_errors=True)
admin_tweet_submit_parser.add_argument('tweets', type=array_type, location="json")

admin_tweet_load_translated_parser = RequestParser(bundle_errors=True)
admin_tweet_load_translated_parser.add_argument('load_translated', type=str, location="args", store_missing=False)

admin_tweet_load_generated_parser = RequestParser(bundle_errors=True)
admin_tweet_load_generated_parser.add_argument('load_generated', type=str, location="args", store_missing=False)

admin_tweet_submit_translation_parser = RequestParser(bundle_errors=True)
admin_tweet_submit_translation_parser.add_argument('input_translated', type=str, location="form", store_missing=False)

admin_tweet_submit_generated_parser = RequestParser(bundle_errors=True)
admin_tweet_submit_generated_parser.add_argument('artifact_url_1', type=str, location="json", store_missing=False)
admin_tweet_submit_generated_parser.add_argument('artifact_url_2', type=str, location="json", store_missing=False)
admin_tweet_submit_generated_parser.add_argument('artifact_url_3', type=str, location="json", store_missing=False)
admin_tweet_submit_generated_parser.add_argument('artifact_url_4', type=str, location="json", store_missing=False)


def get_generation_filters():
    filters_dict = admin_tweet_load_generated_parser.parse_args()
    if "load_generated" in filters_dict:
        return True
    else:
        return Piece.artifact_url_1.is_(None)


def get_translation_filters():
    filters_dict = admin_tweet_load_translated_parser.parse_args()
    if "load_translated" in filters_dict:
        return True
    else:
        return Piece.input_translated.is_(None)

def get_submitted_tweets():
    tweets_dict = admin_tweet_submit_parser.parse_args()
    tweets: List[Dict[str, str]] = []
    if "tweets" in tweets_dict:
        tweets = tweets_dict["tweets"]

    return tweets

user_model = Model(
    "User",
    {
        "email": String,
        "public_id": String,
        "role": String,
        "registered_on": String(attribute="registered_on_str"),
        "token_expires_in": String,
    },
)

