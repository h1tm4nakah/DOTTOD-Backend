import re
from typing import Dict


def filter_tweet_text(input_text: str) -> str:
    # Remove trailing and starting white spaces
    filtered_text = input_text.strip()
    # Remove urls from the tweet
    filtered_text = re.sub(r"http\S+", " ", filtered_text)
    # Remove hashtags
    filtered_text = re.sub('#', ' ', filtered_text)
    # Remove new lines
    filtered_text = re.sub('\n', ' ', filtered_text)
    # Remove emoji
    regrex_pattern = re.compile(pattern="["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        u"\U00002500-\U00002BEF"  # chinese char
                                        u"\U00002702-\U000027B0"
                                        u"\U00002702-\U000027B0"
                                        u"\U000024C2-\U0001F251"
                                        u"\U0001f926-\U0001f937"
                                        u"\U00010000-\U0010ffff"
                                        u"\u2640-\u2642" 
                                        u"\u2600-\u2B55"
                                        u"\u200d"
                                        u"\u23cf"
                                        u"\u23e9"
                                        u"\u231a"
                                        u"\ufe0f"  # dingbats
                                        u"\u3030"
                                        "]+", flags=re.UNICODE)

    return regrex_pattern.sub(r'', filtered_text).strip()


def get_tweet_score(t: Dict[str, str]) -> int:
    return (
        t.public_metrics['like_count'] +
        t.public_metrics['retweet_count'] +
        t.public_metrics['reply_count']
    )