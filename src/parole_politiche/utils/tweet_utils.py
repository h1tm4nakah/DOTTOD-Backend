import re
from typing import Dict


def filter_tweet_text(input_text: str) -> str:
    # Remove trailing and starting white spaces
    filtered_text = input_text.strip()
    # Remove urls from the tweet
    filtered_text = re.sub(r"http\S+", "", filtered_text)
    # Remove hashtags
    filtered_text = re.sub(r"#\S+", "", filtered_text)
    # Remove new lines
    filtered_text = re.sub('\n', '', filtered_text)
    # TODO: Remove emoji

    return filtered_text


def get_tweet_score(t: Dict[str, str]) -> int:
    return (
        t.public_metrics['like_count'] +
        t.public_metrics['retweet_count'] +
        t.public_metrics['reply_count']
    )