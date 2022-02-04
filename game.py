from __future__ import unicode_literals
from setup import config
from unidecode import unidecode
from datetime import datetime, timedelta
import random


class Game:
    def __init__(self, tweet_id, player_id):
        self.id = tweet_id
        self.__player_id = player_id
        self.__current_tweet = tweet_id
        self.__time_limit = datetime.today() + timedelta(60)

        self.__answer = random.choice(config["word-list"])
        self.__wrong = set()
        self.__wrong_place = set()
        self.__correct = set()
        self.__guesses = []
        self.__attempts = 0

    def get_data(self):
        data = {
            "id": self.id,
            "player-id": self.__player_id,
            "current-tweet": self.__current_tweet,
            "time-limit": self.__time_limit.strftime("%d/%m/%Y"),
            "answer": self.__answer,
            "wrong": self.__wrong,
            "correct": self.__correct,
            "wrong-place": self.__wrong_place,
            "guesses": self.__guesses,
            "attempts": self.__attempts,
        }
        return data

    def set_data(self, data):
        self.__id = data["origin-tweet"]
        self.__player_id = data["player-id"]
        self.__current_tweet = data["current-tweet"]
        self.__time_limit = datetime.strptime(data["time-limit"], "%d/%m/%Y")

        self.__answer = data["answer"]
        self.__wrong = data["wrong"]
        self.__wrong_place = data["wrong-place"]
        self.__correct = data["correct"]
        self.__guesses = data["guesses"]
        self.__attempts = data["attempts"]

    @property
    def id(self):
        return self.__id

    @property
    def player_id(self):
        return self.__player_id

    @property
    def time_limit(self):
        return self.__time_limit

    @property
    def current_tweet(self):
        return self.__current_tweet

    @current_tweet.setter
    def current_tweet(self, new_tweet_id):
        self.__current_tweet = new_tweet_id

    def has_lost(self):
        lost = False
        if self.__attempts > 6:
            lost = True
        return lost

    def has_won(self):
        won = False
        if self.guess == self.__answer:
            won = True
        return won

    def has_ended(self):
        ended = False
        if self.has_won() or self.has_lost():
            ended = True
        return ended

    def __check_guess(self, guess):
        """Checks if the guess is valid, if so, classifies each letter as "wrong", "wrong place" or "correct".

        Args:
            guess (str)

        Returns:
            True: If the guess is valid
            False: If the guess is invalid
        """

        answer = unidecode(self.__answer)
        guess = unidecode(guess.lower())

        if not guess.isalpha() or len(guess) != 5:
            return False

        for index, letter in enumerate(guess):
            if letter == answer[index]:
                self.__correct.add(letter)
            elif letter in answer:
                self.__wrong_place.add(letter)
            else:
                self.__wrong.add(letter)

        return True

    def play(self, guess):  
        is_valid = self.__check_guess(guess)

        if self.__check_guess(guess):
            self.__guesses.append(guess)
            self.__attempts += 1
