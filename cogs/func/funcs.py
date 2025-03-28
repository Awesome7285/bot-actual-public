import random
from PIL import Image, ImageDraw, ImageFont
import os

# Cog Functions
def squash_text(msg: str, split: str = '\n'):
    """
    Squishes long messages into under 2000 character segments.
    """
    msgs = []
    start = 0
    end = 1980
    while end < len(msg):
        end = msg.rfind(split, start, end)
        msgs.append(msg[start:end])
        start = end+1
        end = start + 1980
    msgs.append(msg[start:])
    return msgs

class IncorrectInputError(Exception):
    """Incorrect Input"""

def random_weighted(items: list, weights: list):
    """
    Picks a random item, with a given weight for each item in a list.
    Re-write of Tom's scr_random_weighted used in SCPOS into Python.
    """
    num = random.randint(1, sum(weights))
    weight = 0
    for i in range(len(items)):
        weight += weights[i]
        if num <= weight:
            return items[i]

#Text on Image Function
def text_image(img, text, text_col, font_size, text_pos, align='la', font='arial') -> Image:
    txt = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    font = ImageFont.truetype(f'c:/Windows/Fonts/{font}.ttf', font_size) #ARLRDBD.TTF
    d.text(text_pos, text, font=font, fill=text_col, anchor=align)
    img.paste(txt, (0, 0), txt)
    return img

# Create gif
def plat_gif(file, effect, amount=1):
    file = 'scpos/'+file
    frames = []
    length = len(os.listdir(f'scpos/card effects/{effect}'))
    # PLAT
    if effect == 'plat':
        # List all items in folder
        for i in range(length):
            im = Image.open(file)
            im_effect = Image.open(f'scpos/card effects/{effect}/{effect}_{i}.png')
            im.paste(im_effect, (0, 0), im_effect) # Paste
            frames.append(im.copy()) # Add to gif
        for i in range(3):
            frames.append(Image.open(file).copy()) # Add no effect at end of gif x3
    elif effect == 'sparkle':
        frames = [Image.open(file).copy() for _ in range(12)] # List of the base image for 12 frames
        for _ in range(amount):
            frames = add_sparkle(frames) # Add sparkles at varying locations, and timings
    frames[0].save(f'scpos/temp/platout.gif', save_all=True, append_images=frames[1:], optimize=True, duration=50, loop=0)

# Add sparkle
def add_sparkle(image_list):
    start_index = random.randint(0, len(image_list))
    pos_x = random.randint(32, 512-64)
    pos_y = random.randint(32, 704)
    indexes = {0:'', 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:'', 11:''}
    # Loop each image
    for image in range(len(image_list)):
        index = indexes[(start_index+image) % 12]
        if index != '':
            img_sprk = Image.open(f'scpos/card effects/sparkle/SCPOS_sparkle{index}.png')
            image_list[image].paste(img_sprk, [pos_x, pos_y], img_sprk)
    return image_list

if __name__ == '__main__':
    #os.chdir("../../")
    plat_gif('cards/special/special_1_2.png', 'plat')
    # gif = add_sparkle([Image.open(f'scpos/cards/special/special_2.png').copy() for _ in range(12)])
    # gif = add_sparkle(gif)
    # gif[0].save(f'scpos/temp/platout.gif', save_all=True, append_images=gif[1:], optimize=False, duration=len(gif), loop=0)
