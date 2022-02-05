from __future__ import unicode_literals
from display import Display
from setup import config
from unidecode import unidecode
from datetime import datetime, timedelta
import random


class Game:
    def __init__(self, tweet_id, player_id):
        self.__id = tweet_id
        self.__player_id = player_id
        self.__current_tweet = tweet_id
        self.__time_limit = datetime.today() + timedelta(60)

        self.__answer = random.choice(config["word-list"])

        self.__wrong = set()
        self.__wrong_place = set()
        self.__correct = set()
        self.__guesses = []
        self.__matrix = []
        self.__attempts = 0

        self.__display = Display(self.__matrix)

    def get_data(self):
        """Create a dict with the game attributes data.

        Returns:
            dict: Game data.
        """

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
            "matrix": self.__matrix,
            "attempts": self.__attempts,
        }
        return data

    def set_data(self, data):
        """Gets the data from the argument and sets it to the game attributes.

        Args:
            data (dict): Game data.
        """

        self.__id = data["origin-tweet"]
        self.__player_id = data["player-id"]
        self.__current_tweet = data["current-tweet"]
        self.__time_limit = datetime.strptime(data["time-limit"], "%d/%m/%Y")

        self.__answer = data["answer"]
        self.__wrong = data["wrong"]
        self.__wrong_place = data["wrong-place"]
        self.__correct = data["correct"]
        self.__guesses = data["guesses"]
        self.__matrix = data["matrix"]
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
    def current_tweet(self, new_tweet):
        self.__current_tweet = new_tweet

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

    def is_valid_guess(self, guess):
        """Checks if the guess has 5 alphabetical letters."""

        is_valid = False

        if guess.isalpha() and len(guess) == 5:
            is_valid = True

        return is_valid

    def play(self, guess):
        """If the guess is valid, saves and classifies it, then updates the display.

        Args:
            guess (str): 5 letters word
        """

        if not self.is_valid_guess(guess):
            return

        answer = unidecode(self.__answer)
        guess = unidecode(guess.lower())

        self.__matrix.append([])
        self.__guesses.append(guess)

        # Classifies the letter as correct, wrong or wrong place
        for index, letter in enumerate(guess):
            if letter == answer[index]:  # If it is the same letter, then it is "correct"
                self.__correct.add(letter)
                self.__matrix[-1].append((letter, "c"))
            elif letter in answer:  # If it is a answer letter, then it is "wrong place"
                self.__wrong_place.add(letter)
                self.__matrix[-1].append((letter, "w"))
            else:  # If none of the above , then it is "wrong"
                self.__wrong.add(letter)
                self.__matrix[-1].append((letter, "wp"))

        self.__attempts += 1
        self.__display.update(self.__matrix)
