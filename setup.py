import json
import logging
import tweepy

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(message)s')

file_handler = logging.FileHandler("logs.log")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

with open(r"data/config.json") as config_file:
    config = json.load(config_file)


def get_client():
    api_key = config["api-key"]
    api_key_secret = config["api-key-secret"]
    bearer_token = config["bearer-token"]
    access_token = config["access-token"]
    access_token_secret = config["access-token-secret"]

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=True
    )

    logger.info("API initialized")

    return client
