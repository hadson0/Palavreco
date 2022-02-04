from datetime import datetime
from setup import logger
from game import Game
import json
import time


class Bot:
    def __init__(self, client):
        self.__client = client
        self.__since_id = 1
        self.__game_data = {}
        self.__games = {}
        self.__id = int(self.__client.get_me().data["id"])

        self.__load_data()

    def __load_data(self):
        """Loads the data from the game_data.json file."""

        logger.info("Loading data...")
        with open("game_data.json") as data_file:
            self.__game_data = json.load(data_file)

        for id, game in self.__game_data.items():
            new_game = Game(id)
            new_game.set_data(game)
            self.__games[id] = new_game

    def __save_data(self):
        """Saves the data to the game_data.json file."""

        for id, game in self.__games.items():
            if game.time_limit < datetime.today():
                self.__game_data.pop(id, None)
            else:
                self.__game_data[id] = game.get_data()

        logger.info("Saving data...")
        with open("game_data.json", "w+") as data_file:
            data_json = json.dumps(self.__game_data, indent=True)
            data_file.write(data_json)

    def get_origin(self, tweet_id):
        tweet = self.__client.get_tweet(
            id=tweet_id, expansions="referenced_tweets.id.author_id")

        if tweet.data.id in self.__games:
            return tweet.data.id

        return self.get_origin(tweet.includes["tweets"][0].id)

    def create_game(self, tweet_id):
        logger.info("Creating a new game...")

        new_game = Game(tweet_id)
        self.__games[tweet_id] = new_game

        logger.info(f"Game created, ID: {tweet_id}")

        try:
            logger.info("Replying...")
            #  response = self.client.create_tweet(
            #    text="",
            #    in_reply_to_tweet_id=tweet_id,
            # )

            # logger.info(
            # f"https://twitter.com/user/status/{response.data['id']}")
            # new_game.current_tweet = response.data['id']
        except Exception as exc:
            logger.exception("Error while replying")
            raise exc

        self.__save_data()

    def continue_game(self, tweet_id):
        origin = self.get_origin(tweet_id)
        game = self.__games[origin]

        tweet = self.__client.get_tweet(
            id=tweet_id, expansions="referenced_tweets.id.author_id")
        is_replying_to_the_game = tweet.includes["tweets"][0].id == game.current_tweet
        author_id = tweet.data["author_id"]
        text = tweet.data["text"]
        guess = ""

        for word in text.split():
            if word.startswith("!") and len(word) == 6:
                guess = word[1:]

        if game.player_id != author_id or not is_replying_to_the_game:
            return

        game.play(guess)

        try:
            logger.info("Replying...")
            #  response = self.client.create_tweet(
            #    text="",
            #    in_reply_to_tweet_id=tweet_id,
            # )

            # logger.info(
            # f"https://twitter.com/user/status/{response.data['id']}")
            # game.current_tweet = response.data['id']
        except Exception as exc:
            logger.exception("Error while replying")
            raise exc

        if game.has_ended():
            self.__games.pop(origin, None)
            self.self.__game_data.pop(id, None)

        self.__save_data()

    def search_mentions(self):
        """Searches for mentions to create or continue a game."""

        logger.info("Searching for new mentions...")

        mentions = list(self.__client.get_users_mentions(
            id=self.__id, since_id=self.__since_id))

        if mentions.data:
            for mention in mentions.data:
                mention = self.__client.get_tweet(
                    id=mention["id"], expansions="referenced_tweets.id.author_id")

                self.__since_id = mention.data["id"]
                author_id = mention.data["author_id"]

                is_not_reply = mention.data["in_reply_to_user_id"] is not self.__id
                is_not_mine = author_id is not self.__id

                if is_not_mine:
                    logger.info(
                        f"New mention found: https://twitter.com/user/status/{mention.data['id']}")

                    if is_not_reply:
                        self.create_game(mention.data["id"])
                    else:
                        self.continue_game(mention.data["id"])

        time.sleep(12)
