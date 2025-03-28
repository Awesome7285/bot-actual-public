import nextcord
from nextcord.ext import commands
import os
from .func.funcs import random_weighted, text_image, plat_gif
from random import randint
from configparser import ConfigParser
from PIL import Image, ImageDraw
from datetime import datetime
import json

#SCPOS Stuff
rarity_chances = [3500, 2500, 1500, 1000, 500, 200, 10]
rarity_messages = ['You got a common card', 'Oh, you got a blue card', 'Nice, a cyan card', 'Cool, cool, a green card', 'Yo, a red card, POG', 'NO WAYY, GOLD CARD??', 'HOLY SHIT YOU GOT A SPECIAL CARD YOU LUCKY FUCKER']
special_chances = [10, 5, 10, 1, 10]
colour_ids = [0, "black", "blue", "cyan", "green", "red", "gold", "plat"]
colour_values = [0, 0.25, 0.5, 0.75, 1, 1.5, 2]

class SCPOSOLD(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    # Ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("SCPOS is online.")

    # Test
    @commands.command(aliases=['scposping', 'scposcheck'])
    async def scpos_ping(self, ctx):
        """
        Pings back to the channel if scpos bot is online.
        """
        await ctx.send(f"SCPOS is online")

    # Debug
    @commands.command(aliases=[])
    async def animate_card(self, ctx, file):
        """
        Debug Command. Do not use.
        """
        if ctx.author.id == 244616599443603456:
            plat_gif(f'cards/{file}.png')
            await ctx.send(file=nextcord.File('./scpos/temp/platout.gif'))

    # Roll
    @commands.command(aliases=['pack_open', 'roll_card', 'r', 'roll', 'rollcard',])
    async def scpos_roll(self, ctx, pack='default'):
        """
        Rolls a card in a specified pack for the Student Card Collector game.
        Can only be rolled once per hour.
        """
        f = open('./scpos/playerdata/time_data.json')
        times = json.load(f)
        f.close()
        user = str(ctx.author.id)
        t = datetime.utcnow()
        # User is in the file?
        if user in times.keys():
            # User has to wait an hour
            if times[user] == [t.year, t.month, t.day, t.hour]:
                await ctx.send(f"You must wait {60-t.minute} minutes before rolling again.")
                return
        # Can successfully roll after this point

        if pack in ['default', 'special']:
            await ctx.send("You must specify a pack.")
        elif pack in os.listdir('./scpos/cards'):
            # Choose Rarity
            card_colour = random_weighted([i+1 for i in range(7)], rarity_chances)
            card_number = randint(0, 3)
            if card_colour == 7:
                card_number = random_weighted(range(len(special_chances)), special_chances)
                _set = 'special'
                msg = rarity_messages[6]
                plat_gif(f'cards/special/special_{card_number}.png')
                file = nextcord.File(f'./scpos/temp/platout.gif')
            else:
                _set = pack
                msg = rarity_messages[card_colour-1]
                file = nextcord.File(f'./scpos/cards/{_set}/{_set}_{card_colour}_{card_number}.png')
            card_key = f'{card_colour}-{card_number}'
            # Read file
            player_file = ConfigParser()
            player_file.read(f'./scpos/playerdata/{ctx.author.id}.ini')
            # Add pack section if player doesn't have it yet
            if not player_file.has_section(_set):
                player_file.add_section(_set)
            # Add card key if player doesn't have it yet
            if not player_file.has_option(_set, card_key):
                player_file.set(_set, card_key, '1')
                msg = "NEW CARD! "+msg
            # Add one card to total
            else:
                player_file[_set][card_key] = str(int(player_file[_set][card_key])+1)
            # Write to file
            with open(f'./scpos/playerdata/{ctx.author.id}.ini', 'w') as c:
                player_file.write(c)
            # Save new time file
            f = open('./scpos/playerdata/time_data.json', 'w')
            times[user] = [t.year, t.month, t.day, t.hour-1]
            json.dump(times, f, indent=3)
            # Send Message
            await ctx.send(file=file)
            await ctx.send(msg)
        else:
            await ctx.send("That is not a pack.")
    
    # Inventory
    @commands.command(aliases=['inv', 'inventory'])
    async def scpos_inventory(self, ctx, pack='all'):
        """
        Displays the inventory of a user for the Student Card Collector game.
        By default will display all unlocked packs, write only one pack name to show just one pack image.
        Mention a user to show that user's inventory, must be done after pack is specified (if any).
        """
        # Fix up parameters
        if ctx.message.mentions.__len__() == 1:
            player = ctx.message.mentions[0].id
        else:
            player = ctx.author.id
        if pack.startswith('<'): # If user only mentions someone, re-set the pack var
            pack = 'all'

        # Load Player File
        player_file = ConfigParser()
        player_file.read(f'./scpos/playerdata/{player}.ini')

        # Files to output
        files = []

        # Special pack
        if pack == 'special' and player_file.has_section(pack):
            inv_img = Image.new("RGB", (640, 480), (255, 0, 0, 255)) # Create Image with Red Background
            inv_img = text_image(inv_img, 'Special', (255, 255, 255, 255), 24, (0, 0)) # Pack Text in top left
            frames = []
            for i in range(34): # Loop for plat animation frames
                for x in range(1, 7): # Loop each rarity
                    for y in range(0, 4): # Loop each card within rarity
                        card_key = f'7-{(x-1)*4+y}'
                        if player_file.has_option(pack, card_key): # Check if player has this card
                            card_img = Image.open(f"./scpos/cards/special/special_{(x-1)*4+y}.png").resize((64, 96))
                            card_amount = player_file[pack][card_key]
                            inv_img.paste(card_img, (48+(x-1)*96, 32+y*112)) # Paste card image
                            inv_img = text_image(inv_img, f'x{card_amount}', (255, 255, 255, 255), 16, (48+(x-1)*96, 128+y*112)) # Write amount text
                            plat_img = Image.open(f"./scpos/card effects/plat_{i}.png").resize((64, 96)) # Load plat image
                            inv_img.paste(plat_img, (48+(x-1)*96, 32+y*112), plat_img) # Paste plat image
                frames.append(inv_img.copy()) # Copy the frame to the frame list
            frames[0].save(f"./scpos/temp/img{pack}.gif", save_all=True, append_images=frames[1:], optimize=True, duration=30, loop=0) # Save as temp image
            files.append(nextcord.File(f"./scpos/temp/img{pack}.gif"))

        # Single Pack
        elif pack in player_file.sections():
            # Create image
            inv_img = Image.new("RGB", (640, 480), (255, 0, 0, 255)) # Create Image with Red Background
            inv_img = text_image(inv_img, pack.title(), (255, 255, 255, 255), 24, (0, 0)) # Pack Text in top left
            for x in range(1, 7): # Loop each rarity
                for y in range(0, 4): # Loop each card within rarity
                    card_key = f'{x}-{y}'
                    if player_file.has_option(pack, card_key): # Check if player has this card
                        card_img = Image.open(f"./scpos/cards/{pack}/{pack}_{x}_{y}.png").resize((64, 96))
                        card_amount = player_file[pack][card_key]
                    else:
                        card_img = Image.open(f"./scpos/unowned/unowned{x}.png").resize((64, 96))
                        card_amount = 0
                    inv_img.paste(card_img, (48+(x-1)*96, 32+y*112)) # Paste card image
                    inv_img = text_image(inv_img, f'x{card_amount}', (255, 255, 255, 255), 16, (48+(x-1)*96, 128+y*112)) # Write amount text
            inv_img.save(f"./scpos/temp/img{pack}.png") # Save as temp image
            files.append(nextcord.File(f"./scpos/temp/img{pack}.png"))
        
        # Else cases
        elif pack in os.listdir('./scpos/cards'):
            await ctx.send("Player has no cards in this pack.")
        else:
            await ctx.send("Invalid pack name.")
        if files != []:
            await ctx.send(f'<@{player}>', files=files)

    # Sell
    @commands.command(aliases=['sellcard', 'sell_card'])
    async def scpos_sell(self, ctx, pack, colour, num, amount='selldupes'):
        """
        Sells an amount of cards from your inventory in the SCPOS game.
        Usage: 
        pack = any pack name
        colour = black, blue, cyan, green, red, gold
        num = 1, 2, 3, 4: the numbered spot going down the column in the inventory
        amount = 'all', 'selldupes' or any number less than the amount you own DEFAULT='selldupes'
        Example: ~~sellcard basic black 3 (sells all duplicates of the minecraft amongus card)
        There is no warning on the 'all' option so be careful!
        Use scpos_sad to sell all dupes from every pack.
        """
        # Load Player File
        player_file = ConfigParser()
        player_file.read(f'./scpos/playerdata/{ctx.author.id}.ini')
        # Set vars
        colour = colour_ids.index(colour)
        option = f"{colour}-{int(num)-1}"
        # Player has card
        if player_file.has_section(pack):
            if player_file.has_option(pack, option):
                # Options
                if amount == 'all':
                    # Sell ALL
                    selling = int(player_file[pack][option])
                    player_file.remove_option(pack, option) # Remove section from file
                elif player_file[pack][option] == "1":
                    await ctx.send("You only have 1 of this card. If you want to sell ALL of a card, write 'all' after the card id.")
                    return
                elif amount == 'selldupes':
                    # Sell all down to 1
                    selling = int(player_file[pack][option])-1
                    player_file[pack][option] = "1" # Set to 1
                elif amount.isdigit():
                    # Sell a number
                    if int(amount) < int(player_file[pack][option]):
                        selling = int(amount)
                        player_file[pack][option] = str(int(player_file[pack][option])-int(amount))
                    else:
                        await ctx.send("You don't have that many of this card. If you want to sell ALL of a card, write 'all' after the card id.")
                        return
                # Update gained points
                gain = selling * colour_values[colour] # Give points
                # Save to file
                if not player_file.has_section("data"):
                    player_file.add_section("data")
                    player_file['data']['rolls'] = '0'
                player_file["data"]["rolls"] = str(gain + float(player_file["data"]["rolls"]))
                with open(f'./scpos/playerdata/{ctx.author.id}.ini', 'w') as f:
                    player_file.write(f)
                await ctx.send(f"Sold {selling} card(s). You gained +{gain} roll points.")
            else:
                await ctx.send("You don't own this card.")
        else:
            await ctx.send("You don't have any cards in this pack.")

    # Sell All Dupes
    @commands.command(aliases=['scpossad', 'selldupes', 'scpos_sad', 'sellalldupes'])
    async def scpos_arl(self, ctx, rarity='3'):
        """
        Sell duplicates from every pack in your inventory in the SCPOS game.
        rarity = the maximum rarity card to auto-sell, DEFAULT=3
        (This means that every black, blue and cyan card will sell by default)
        """
        # Load Player File
        player_file = ConfigParser()
        player_file.read(f'./scpos/playerdata/{ctx.author.id}.ini')
        # Add the data section to not crash on the upcoming for loop
        if not player_file.has_section('data'):
            player_file.add_section('data')
            player_file['data']['rolls'] = '0'
        # Loop the file
        gain = 0
        total_sold = 0
        packs = player_file.sections()
        packs.remove('data')
        for pack in packs: # For each pack section
            for card in player_file[pack].keys(): # For each card in pack
                if int(card[0]) <= int(rarity): # Wants to sell? (plat is already 7 so no need to change for that)
                    # Sell all down to 1
                    selling = int(player_file[pack][card])-1
                    player_file[pack][card] = "1" # Set to 1
                    # Update gained points
                    gain += selling * colour_values[int(card[0])] # Give points
                    total_sold += selling
        # Save to file
        player_file["data"]["rolls"] = str(gain + float(player_file["data"]["rolls"]))
        with open(f'./scpos/playerdata/{ctx.author.id}.ini', 'w') as f:
            player_file.write(f)
        await ctx.send(f"Sold {total_sold} card(s). You gained +{gain} roll points.")



#TODO change font, trading??, achieves, background setting, 

# Setup Cog into main bot
def setup(client):
    client.add_cog(SCPOSOLD(client))