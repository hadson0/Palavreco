import time
from PIL import Image, ImageFont, ImageDraw


class Display:
    def __init__(self, matrix):
        self.__background = Image.open(r"assets/background.png")
        self.__border = Image.open(r"assets/border.png")
        self.__correct = Image.open(r"assets/correct.png")
        self.__wrong_place = Image.open(r"assets/wrong_place.png")
        self.__wrong = Image.open(r"assets/wrong.png")
        self.__font = ImageFont.truetype(r"assets/Roboto-Regular.ttf", 80)

        self.update(matrix)

    def __draw_box(self, letter_tuple):
        """Draw a colored text box.

        Args:
            letter_tuple (tuple): (letter, tag). 
            Tag: "c" (correct), "w" (wrong), "wp" (wrong place).

        Returns:
            Text box image.
        """
        
        letter = letter_tuple[0].upper()
        tag = letter_tuple[1]

        if tag == "c":
            box = self.__correct.copy()  # Green box
        elif tag == "wp":
            box = self.__wrong.copy()  # Yellow box
        elif tag == "w":
            box = self.__wrong_place.copy()  # Grey box

        draw = ImageDraw.Draw(box)

        bw, bh = box.size  # (box width, box height)
        lw, lh = draw.textsize(letter, font=self.__font)  # (letter width, letter height)
        letter_coord = ((bw - lw)/2, (bh - lh - 17)/2)  # Centralized letter coord

        draw.text(letter_coord, letter,
                  font=self.__font, fill="white")

        return box

    def update(self, matrix):
        """Updates the game display and saves it in assets folder (assets/display.png).

        Args:
            matrix (dict): A dict of tuples, with a guess letter and a tag.
            Tag: "c" (correct), "w" (wrong), "wp" (wrong place).
        """

        display = self.__background.copy()

        y = 165  # Y-coordinate of the first box
        for i in range(6):
            x = 82  # X-coordinate of the first box

            for j in range(5):
                if i >= len(matrix):  # If there isn't more guesses, place empty box
                    display.paste(self.__border, (x, y), mask=self.__border)
                else:   # Otherwise, place a colored box with the letter
                    box = self.__draw_box(matrix[i][j])
                    display.paste(box, (x, y), mask=box)

                x += 114  # 100 (box width) + 14 (spacing)
            y += 122  # 100 (box height) + 22 (spacing)

        display.save(r"assets/display.png")
