import time
from PIL import Image, ImageFont, ImageDraw


class Display:
    def __init__(self, matrix):
        self.__matrix = matrix

        self.__background = Image.open(r"assets/background.png")
        self.__border = Image.open(r"assets/border.png")
        self.__correct = Image.open(r"assets/correct.png")
        self.__wrong_place = Image.open(r"assets/wrong_place.png")
        self.__wrong = Image.open(r"assets/wrong.png")
        self.__font = ImageFont.truetype(r"assets/Roboto-Regular.ttf", 80)

        self.update(matrix)

    def update(self, matrix):
        self.__matrix = matrix

        display = self.__background.copy()

        y = 165
        for i in range(6):
            x = 82

            for j in range(5):
                if i >= len(matrix):
                    display.paste(self.__border, (x, y), mask=self.__border)
                else:
                    letter = matrix[i][j][0].upper()
                    tag = matrix[i][j][1]

                    if tag == "c":
                        block = self.__correct.copy()
                    elif tag == "wp":
                        block = self.__wrong.copy()
                    elif tag == "w":
                        block = self.__wrong_place.copy()

                    draw_block = ImageDraw.Draw(block)

                    w1, h1 = block.size
                    w2, h2 = draw_block.textsize(letter, font=self.__font)
                    letter_coord = ((w1 - w2)/2, (h1 - h2 - 17)/2)

                    draw_block.text(letter_coord, letter,
                                    font=self.__font, fill="white")
                    display.paste(block, (x, y), mask=block)

                x += 114

            y += 122

        display.save(r"display.png")
