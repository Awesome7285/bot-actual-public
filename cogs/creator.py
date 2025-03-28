import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import os
from .func.funcs import plat_gif
from configparser import ConfigParser
from PIL import Image, ImageDraw

# Create class
class Creator(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @nextcord.slash_command(description="Upload an image")
    async def image_upload(self, interaction: Interaction, image:nextcord.Attachment = SlashOption(required=True)):
        await interaction.response.defer()
        await image.save(f"scpos/temp/{interaction.user.id}.png") # Save Image
        file = f"scpos/temp/{interaction.user.id}.png"
        if image.width//2*3 != image.height: # Check Card Ratio 2:3
            text = "This image will not fit into a card's dimentions. The resizer tool may help."
        elif image.width < 512: # Min width 512 (min height 768)
            text = "This image may be too small for a card."
        else:
            text = "This image will fit into a card. Good on you!"
        await interaction.send(f"Uploaded! Image Dimentions: {image.width}x{image.height}. "+text, file=nextcord.File(file))

    @nextcord.slash_command(description="Resize an image to card size, or other size")
    async def image_resize(self, interaction: Interaction, fit:str = SlashOption(choices=['left', 'up', 'right', 'down', 'lrcenter', 'udmiddle', 'auto'], required=True), size:int = SlashOption(required=False)):
        img = Image.open(f'./scpos/temp/{interaction.user.id}.png')
        _height = img.height - img.height % 3
        _width = img.width - img.width % 3
        if fit == 'left':
            img = img.crop((0, 0, _height//3*2, _height))
        if fit == 'lrcenter':
            padding = _width-_height//3*2
            img = img.crop((padding//2, 0, _height//3*2+padding//2, _height))
        if fit == 'right':
            img = img.crop((_width-_height//3*2, 0, _width, _height))
        if fit == 'up':
            img = img.crop((0, 0, _width, _width//2*3))
        if fit == 'down':
            img = img.crop((0, _height-_width//2*3, _width, _height))
        if fit == 'auto':
            img = img.resize((512, 768))
        img.save(f'./scpos/temp/{interaction.user.id}.png')
        await interaction.send(f'Edited! Image Dimentions: {img.width}x{img.height}', file=nextcord.File(f"scpos/temp/{interaction.user.id}.png"))

    @nextcord.slash_command(description="Add effects to a card")
    async def image_border(self, interaction: Interaction, 
    colour:str = SlashOption(choices=["black", "blue", "cyan", "green", "red", "gold", "plat", "achievement"])):
        img = Image.open(f'./scpos/temp/{interaction.user.id}.png')
        if img.width//2*3 == img.height: # Check Card Ratio 2:3
            await interaction.response.defer()
            img = img.resize((512, 768))
            border = Image.open(f'./scpos/borders/{colour}.png')
            mask = Image.open(f'./scpos/borders/black.png')
            img.paste(border, mask=mask)
            img.save(f'./scpos/temp/{interaction.user.id}.png')
            await interaction.send('Added Border!', file=nextcord.File(f"scpos/temp/{interaction.user.id}.png"))
        else:
            await interaction.send("Your current image is not in a 2:3 ratio")

    @nextcord.slash_command(description="Add effects to a card")
    async def image_effect(self, interaction: Interaction, 
    pack:str = SlashOption(choices=[pack for pack in os.listdir('./scpos/cards')]), 
    colour:str = SlashOption(choices=["1", "2", "3", "4", "5", "6"]), 
    num:str = SlashOption(choices=['0', '1', '2', '3']),
    effect:str = SlashOption(choices=['plat','sparkle']),
    amount:int = SlashOption(required=False, default=0)):
        await interaction.response.defer()
        plat_gif(f'cards/{pack}/{pack}_{colour}_{num}.png', effect, amount)
        await interaction.send(file=nextcord.File(f'./scpos/temp/platout.gif'))

def setup(client):
    client.add_cog(Creator(client))