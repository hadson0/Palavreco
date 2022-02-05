from datetime import datetime
from setup import logger
from game import Game
import json
import time


class Bot:
    def __init__(self, client):
        self.__client = client
        self.__id = int(self.__client.get_me().data["id"])

        self.__tweet_id_list = []
        self.__since_tweet_id = 1

        self.__games = {}
        self.__game_data = {}
        self.__past_game_data = {}
        self.__player_data = {}

        self.__load_data()

    def __load_data(self):
        """Loads the data from the data folder."""

        logger.info("Loading data...")

        # Loads the game data
        with open("data/game_data.json") as data_file:
            self.__game_data = json.load(data_file)

            for id, game in self.__game_data.items():
                new_game = Game(id)
                new_game.set_data(game)
                self.__games[id] = new_game

        # Loads the past game data
        with open("data/past_game_data.json") as data_file:
            self.__past_game_data = json.load(data_file)

        # Loads the ID list
        with open("data/id_list.json") as data_file:
            self.__tweet_id_list = json.load(data_file)
            self.__since_tweet_id = self.__tweet_id_list[-1]
            
        # Loads the player data
        with open("data/player_data.json") as data_file:
            self.__player_data = json.load(data_file)

    def __save_data(self):
        """Saves the data to the game_data.json file."""

        logger.info("Saving data...")

        # for id, game in self.__games.items():
        #     if game.time_limit < datetime.today():
        #         self.__past_game_data[id] = self.__game_data.pop(id, None)
        #     else:
        #         self.__game_data[id] = game.get_data()

        # Saves the game data
        with open("data/game_data.json", "w+") as data_file:
            game_data = json.dumps(self.__game_data, indent=True)
            data_file.write(game_data)

        # Saves the past game data
        with open("data/past_game_data.json", "w+") as data_file:
            past_game_data = json.dumps(self.__past_game_data, indent=True)
            data_file.write(past_game_data)

        # Saves the ID list
        with open("data/id_list.json", "w+") as data_file:
            id_list = json.dumps(self.__tweet_id_list, indent=True)
            data_file.write(id_list)
            
        # Saves the player data
        with open("data/player_data.json", "w+") as data_file:
            player_data = json.dumps(self.__player_data, indent=True)
            data_file.write(player_data)

    def get_origin(self, tweet_id):
        """Gets the tweet that originated the game."""

        tweet = self.__client.get_tweet(
            id=tweet_id, expansions="referenced_tweets.id.author_id")

        if tweet.data.id in self.__games or tweet.data["in_reply_to_user_id"] == None:
            return tweet.data.id

        return self.get_origin(tweet.includes["tweets"][0].id)

    def create_game(self, tweet_id, player_id):
        """Creates a new game and reply with an intro display to the tweet."""

        logger.info("Creating a new game...")

        try:
            logger.info("Replying...")

            # mediaID = self.__client.media_upload(r"assets/intro_display.png")
            # response = self.__client.create_tweet(text='',
            #                                       media={"media_ids": [mediaID]})

            # logger.info(
            #     f"https://twitter.com/user/status/{response.data['id']}")

            new_game = Game(tweet_id, player_id)
            # new_game.current_tweet = response.data['id']
            self.__games[tweet_id] = new_game

            # Add the game ID to the player data
            if str(player_id) not in self.__player_data:
                self.__player_data[str(player_id)] = {"games": []}
            if tweet_id not in self.__player_data[str(player_id)]["games"]:
                self.__player_data[str(player_id)]["games"].append(tweet_id)

            logger.info(f"Game created, ID: {tweet_id}")
        except Exception as exc:
            logger.exception("Error while replying")
            raise exc

        self.__save_data()

    def continue_game(self, tweet_id):
        """Continues an existing game."""

        game = self.__games[tweet_id]

        # Gets the tweet infos
        tweet = self.__client.get_tweet(
            id=tweet_id, expansions="referenced_tweets.id.author_id")
        is_replying_to_the_game = tweet.includes["tweets"][0].id == game.current_tweet
        author_id = tweet.data["author_id"]
        text = tweet.data["text"]

        # Verify if there is a guess
        guess = ""
        for command in text.split():
            if command.startswith("!") and len(command) == 6:
                guess = command[1:]

        # If the author is not the player or it is not replying to the current game tweet, returns
        if game.player_id != author_id or not is_replying_to_the_game:
            return

        logger.info("Continuing the game...")
        game.play(guess)

        try:
            logger.info("Replying...")

            # mediaID = self.__client.media_upload(r"assets/display.png")
            # response = self.__client.create_tweet(text='',
            #                                       media={"media_ids": [mediaID]})

            # logger.info(
            #     f"https://twitter.com/user/status/{response.data['id']}")
        except Exception as exc:
            logger.exception("Error while replying")
            raise exc

        # If the game has ended, adds it to the past game data
        if game.has_ended():
            self.__past_game_data[game.id] = self.__games.pop(game.id, None)
            self.self.__game_data.pop(game.id, None)

        self.__save_data()

    def search_mentions(self):
        """Searches for mentions to create or continue a game."""

        logger.info("Searching for new mentions...")

        mentions = list(self.__client.get_users_mentions(
            id=self.__id, since_id=self.__since_tweet_id))

        # If there is any mention
        if mentions[0]:
            for mention in mentions[0]:
                # Get the mention info
                mention = self.__client.get_tweet(
                    id=mention["id"], expansions="referenced_tweets.id.author_id")
                author_id = mention.data["author_id"]
                is_not_reply = mention.data["in_reply_to_user_id"] is not self.__id
                is_not_mine = author_id is not self.__id

                # Updates the ID list and the last mention (since_tweet_id)
                self.__since_tweet_id = mention.data["id"]
                self.__tweet_id_list.append(self.__since_tweet_id)

                if is_not_mine:
                    logger.info(
                        f"New mention found: https://twitter.com/user/status/{mention.data['id']}")

                    if is_not_reply:
                        self.create_game(mention.data["id"], author_id)
                    elif author_id in self.__player_data:
                        origin = self.get_origin(mention.data["id"])
                        
                        if origin in self.__player_data[author_id]["games"]:
                            self.continue_game(origin)

        time.sleep(12)
