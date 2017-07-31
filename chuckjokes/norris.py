import os
import random

from PIL import Image
from bisect import bisect

def ascii_art():
    """
    Inspiration from:
    https://stevendkay.wordpress.com/2009/09/08/generating-ascii-art-from-photographs-in-python/
    """

    greyscale = [
             " ",
            " ",
            ".,-",
            "_ivc=!/|\\~",
            "gjez2]/(YL)t[+T7Vf",
            "mdK4ZGbNDXY5P*Q",
            "W8KMA",
            "#%$"
            ]

    zonebounds= [36, 72, 108, 144, 180, 216, 252]

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "norris.jpg")
    img = Image.open(filepath)
    img = img.resize((80, 35), Image.BILINEAR)
    img = img.convert("L")

    ascii_str = ""

    for y in range(0, img.size[1]):
        for x in range(0, img.size[0]):
            lum = 255 - img.getpixel((x,y))
            row = bisect(zonebounds,lum)
            possibles= greyscale[row]
            ascii_str = ascii_str + possibles[random.randint(0,len(possibles)-1)]

        ascii_str = ascii_str + "\n"

    return ascii_str
