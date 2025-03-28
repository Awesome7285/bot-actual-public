import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption, InteractionType, ButtonStyle
from nextcord.ui import Button
import os
from .func.funcs import random_weighted, text_image, plat_gif, IncorrectInputError, squash_text
from random import randint, choice
from configparser import ConfigParser
from PIL import Image, ImageDraw
from datetime import datetime
import json
import pickle
from math import log

#SCPOS Stuff
rarity_chances = [3500, 2500, 1500, 1000, 500, 200, 10]
RARITY_MESSAGES = ['You got a common card!', 'Oh, you got a blue card!', 'Nice, a cyan card!', 'Cool, cool, a green card!', 'Yo, a red card, POG!', 'NO WAY! A GOLD CARD!?', 'HOLY SHIT YOU GOT A SPECIAL CARD YOU LUCKY FUCKER!!', 'ACHIEVEMENT GET!']
colour_ids = [0, "black", "blue", "cyan", "green", "red", "gold", "plat"]
COLOUR_VALUES = [0, 0.25, 0.5, 0.75, 1, 1.5, 2, 10]
SPECIAL_CHANCES = [10, 5, 10, 10,
                   10, 10, 10, 10,
                   10, 10, 10, 10,
                   10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
sparkle_messages = ['Oh, this card is sparkly!', 'Oh, this card is extra sparkly!', 'Oh, this card is extremely sparkly!!']
TOTAL_ACHIEVES = len(os.listdir('./scpos/cards/achievement')) + len(os.listdir('./scpos/cards/achievement2'))
trades = {}

# Create matches class
class SCPOS(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    # Ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("SCPOS is online.")

    # Load File
    def load_player_file(self, player_id: int) -> dict:
        # Check if file exists
        if not f'{player_id}.pickle' in os.listdir(f'./scpos/playerdata/'):
            player_id = 'DEFAULT'
        # Open file
        with open(f'./scpos/playerdata/{player_id}.pickle', 'rb') as f:
            return pickle.load(f)
            #data = player_file.read().strip().split('\n') # Read the data
            #return [i.split(',') for i in data[0:3]] + [{i.split(':')[0]: [int(j) for j in i.split(':')[1].split(',')] for i in data[3:]}] # Split data into lists

    def save_player_file(self, player_id: int, data: dict) -> None:
        # Save File
        with open(f'./scpos/playerdata/{player_id}.pickle', 'wb+') as f:
            pickle.dump(data, f)
        # with open(f'./scpos/playerdata/{player_id}.txt', mode='w+') as player_file:
        #     data = [','.join([str(j) for j in i]) for i in data[0:3]] + [':'.join([i, ','.join([str(k) for k in j])]) for i, j in data[3].items()]
        #     player_file.write('\n'.join(data)) # Write the data

    @nextcord.slash_command(description="Rolls a card in the SCPOS game")
    async def rollcard(self, interaction: Interaction, pack:str = SlashOption(choices=["random"]+[pack for pack in os.listdir('./scpos/cards') if pack not in ['special', 'achievement', 'achievement2']])):

        # The bug that fails /rollcard timeouts
        await interaction.response.defer()
        
        # Load data from file using pickle
        player_file = self.load_player_file(interaction.user.id)
        
        t = datetime.utcnow()
        time_text = f"{t.year},{t.month},{t.day},{t.hour}" # Format current time
        bought_card = False
        # Check if player can roll
        if player_file['datetime'] == time_text:
            if player_file['rolls'] >= 1:
                bought_card = True
            else:
                await interaction.send(f"You must wait {60-t.minute} minutes before rolling again.", delete_after=3.0)
                return
            
        # Calculate days since last roll
        prev_year, prev_month, prev_day, _ = player_file['datetime'].split(',')
        days_since = (datetime.utcnow() - datetime(int(prev_year), int(prev_month), int(prev_day))).days

        # Can successfully roll after this point

        if pack == 'random':
            pack = choice([pack for pack in os.listdir('./scpos/cards') if pack not in ['special', 'achievement', 'achievement2']])

        if pack in ['default', 'special', 'achievement', 'achievement2']:
            await interaction.send("You must specify a pack.")
        elif pack in os.listdir('./scpos/cards'):

            # Apply Modifiers
            modified_chances = [
                rarity_chances[0] - 40*len(player_file['achievements']), # 3500 - 40 per achieve
                rarity_chances[1] - 20*len(player_file['achievements']), # 2500 - 20 per achieve
                rarity_chances[2] - 10*len(player_file['achievements']), # 1500 - 10 per achieve
            ] + rarity_chances[3:7]
            # modified_chances = rarity_chances[0:4] + [int(i+(i/20*len(player_file['achievements']))) for i in rarity_chances[4:7]] # Only works well until ~25 achieves
            modified_chances[6] += int(player_file['stat_rolls_since_last_special']/10) # Pity Boost
            # if player_file['achievements'] != 0:
            #     boost = 10 ** (TOTAL_ACHIEVES/player_file['achievements'])
            #     modified_chances = [int(weight * log(1 + boost*(sum(rarity_chances)/weight -1))) for weight in rarity_chances]
            # else:
            #     modified_chances = rarity_chances
            #achieve_multiplier = 1.01 ** (player_file['achievements']/TOTAL_ACHIEVES*100)
            #achieve_multiplier_neg = 1.01 ** (player_file['achievements']/TOTAL_ACHIEVES*100*-1)
            #modified_chances = [val*achieve_multiplier_neg*1000 for val in rarity_chances[0:3]] + [rarity_chances[3]*1000] + [val*achieve_multiplier*1000 for val in rarity_chances[4:7]]
            print(modified_chances)

            # Choose Rarity
            card_colour = random_weighted([i+1 for i in range(7)], modified_chances)
            card_number = randint(0, 3)
            card_value = (card_colour-1)*4+card_number

            # Specials/Achievements
            achieve_value = -1
            # Pig Wig
            if 'achievement' in player_file['packs']:
                if "*DMS Speedrunner" not in player_file['achievements'] and player_file["packs"]["achievement_s"][19] == -1:
                    achieve_value = 19
                    achieve_name = "*DMS Speedrunner"
            # Sell 1
            if "Sell a Card" not in player_file['achievements'] and player_file['stat_sold'] != 0:
                achieve_value = 10
                achieve_name = "Sell a Card"
            # Use Stored Roll
            if "Use a Stored Roll" not in player_file['achievements'] and bought_card == True:
                achieve_value = 11
                achieve_name = "Use a Stored Roll"
            # Triple Sparkle
            if "Obtain an Extremely Sparkly Card" not in player_file['achievements']:
                if 3 in [num for pack, nums in player_file['packs'].items() if pack.endswith('_s') for num in nums]:
                    achieve_value = 14
                    achieve_name = "Obtain an Extremely Sparkly Card"
            # Full deck of sparkles
            if "Obtain a Sparkly variant of all Cards in a Pack" not in player_file['achievements']:
                if True in [True for pack in [pack for pack in player_file['packs'] if pack.endswith('_s')] if 0 not in player_file['packs'][pack]]:
                    achieve_value = 18
                    achieve_name = "Obtain a Sparkly variant of all Cards in a Pack"
            # 100 of a card
            if "Obtain 100 of any Card" not in player_file['achievements']:
                if 100 in [num for pack, nums in player_file['packs'].items() if not pack.endswith('_s') for num in nums]:
                    achieve_value = 15
                    achieve_name = "Obtain 100 of any Card"
            # Basic Pack
            if 'basic' in player_file['packs']:
                if "Complete the Basic Pack" not in player_file['achievements'] and 0 not in player_file['packs']['basic']:
                    achieve_value = 4
                    achieve_name = "Complete the Basic Pack"
            # Extended Pack
            if 'extended' in player_file['packs']:
                if "Complete the Extended Pack" not in player_file['achievements'] and 0 not in player_file['packs']['extended']:
                    achieve_value = 5
                    achieve_name = "Complete the Extended Pack"
            # Gacha Pack
            if 'gacha' in player_file['packs']:
                if "Complete the Gacha Pack" not in player_file['achievements'] and 0 not in player_file['packs']['gacha']:
                    achieve_value = 8
                    achieve_name = "Complete the Gacha Pack"
            # Trap Pack
            if 'trap' in player_file['packs']:
                if "Complete the Trap Pack" not in player_file['achievements'] and 0 not in player_file['packs']['trap']:
                    achieve_value = 9
                    achieve_name = "Complete the Trap Pack"
            # Speedrun Pack
            if 'speedrun' in player_file['packs']:
                if "Complete the Speedrun Pack" not in player_file['achievements'] and 0 not in player_file['packs']['speedrun']:
                    achieve_value = 12
                    achieve_name = "Complete the Speedrun Pack"
            # Sport Pack
            if 'sport' in player_file['packs']:
                if "Complete the Sport Pack" not in player_file['achievements'] and 0 not in player_file['packs']['sport']:
                    achieve_value = 13
                    achieve_name = "Complete the Sport Pack"
            # TCG Pack
            if 'tcg' in player_file['packs']:
                if "Complete the TCG Pack" not in player_file['achievements'] and 0 not in player_file['packs']['tcg']:
                    achieve_value = 16
                    achieve_name = "Complete the TCG Pack"
            # Starters Pack
            if 'starters' in player_file['packs']:
                if "Complete the Starters Pack" not in player_file['achievements'] and 0 not in player_file['packs']['starters']:
                    achieve_value = 17
                    achieve_name = "Complete the Starters Pack"
            # Powerful Men Pack
            if 'powerfulmen' in player_file['packs']:
                if "Complete the Powerful Men Pack" not in player_file['achievements'] and 0 not in player_file['packs']['powerfulmen']:
                    achieve_value = 20
                    achieve_name = "Complete the Powerful Men Pack"
            # Scott Pack
            if 'scott' in player_file['packs']:
                if "Complete the Scott Pack" not in player_file['achievements'] and 0 not in player_file['packs']['scott']:
                    achieve_value = 21
                    achieve_name = "Complete the Scott Pack"
            # Scott Pack
            if 'indie' in player_file['packs']:
                if "Complete the Indie Pack" not in player_file['achievements'] and 0 not in player_file['packs']['indie']:
                    achieve_value = 22
                    achieve_name = "Complete the Indie Pack"
            # Iden Pack
            if 'identification' in player_file['packs']:
                if "Complete the Identification Pack" not in player_file['achievements'] and 0 not in player_file['packs']['identification']:
                    achieve_value = 24
                    achieve_name = "Complete the Identification Pack"
            # NotIden Pack
            if 'notidentification' in player_file['packs']:
                if "Complete the Not Identification Pack" not in player_file['achievements'] and 0 not in player_file['packs']['notidentification']:
                    achieve_value = 25
                    achieve_name = "Complete the Not Identification Pack"
            # 10000 Rolls
            if "Roll Ten Thousand Times" not in player_file['achievements'] and player_file['stat_rolls'] >= 10000:
                achieve_value = 3
                achieve_name = "Roll Ten Thousand Times"
            # 1000 Rolls
            if "Roll One Thousand Times" not in player_file['achievements'] and player_file['stat_rolls'] >= 1000:
                achieve_value = 2
                achieve_name = "Roll One Thousand Times"
            # 100 Rolls 
            if "Roll One Hundred Times" not in player_file['achievements'] and player_file['stat_rolls'] >= 100:
                achieve_value = 1
                achieve_name = "Roll One Hundred Times"
            # 1st Roll
            if "Roll One Time" not in player_file['achievements'] and player_file['stat_rolls'] >= 1:
                achieve_value = 0
                achieve_name = "Roll One Time"
            # 7 day streak
            if "Reach a Week Long Streak" not in player_file['achievements'] and player_file['stat_streak_current'] == 6 and days_since == 1:
                achieve_value = 6
                achieve_name = "Reach a Week Long Streak"
            # 31 day streak
            if "Reach a Month Long Streak" not in player_file['achievements'] and player_file['stat_streak_current'] == 30 and days_since == 1:
                achieve_value = 7
                achieve_name = "Reach a Month Long Streak"
            # Tom's Birthday
            if "*Tom's Birthday" not in player_file['achievements'] and t.month == 8 and t.day == 26:
                achieve_value = 23
                achieve_name = "*Tom's Birthday"

            # Check if player can earn the achievement
            if achieve_value != -1:
                if achieve_name not in player_file['achievements']:
                    achieve_pack = str(achieve_value // 24 + 1)
                    card_value = achieve_value % 24
                    card_colour = 8
                    if achieve_pack == '1':
                        achieve_pack = ''
                    pack = 'achievement' + achieve_pack
            
            spoiler = False

            # Achievement spawns
            if card_colour == 8:
                card_colour = (card_value // 4) + 1 # Set the colour 1-6
                card_number = card_value % 4 # Set the number 1-4
                sparkles = 0 # Required for when the variable is called later
                player_file['achievements'].append(achieve_name) # Add Achievement to list
                msg = RARITY_MESSAGES[7]
                file = f'./scpos/cards/{pack}/{pack}_{card_colour}_{card_number}.png'

            # Special spawns
            elif card_colour == 7:
                card_number = random_weighted(list(range(24)), SPECIAL_CHANCES)
                card_value = card_number
                card_colour = (card_number // 4) + 1 # Set the colour 1-6
                card_number = card_number % 4 # Set the number 1-4
                pack = 'special'
                sparkles = 0 # Required for when the variable is called later
                msg = RARITY_MESSAGES[6]
                player_file["stat_rolls_since_last_special"] = 0 # Update rolls since special
                plat_gif(f'cards/special/special_{card_colour}_{card_number}.png', 'plat')
                file = f'./scpos/temp/platout.gif'
                spoiler = True

            # Regular spawns
            else:
                msg = RARITY_MESSAGES[card_colour-1]
                # Add a sparkle amount
                sparkles = random_weighted([0, 1, 2, 3], [75, 15, 9, 1]) # Choose sparkles
                player_file["stat_rolls_since_last_special"] += 1 # Update rolls since special
                if sparkles > 0:
                    msg = sparkle_messages[sparkles-1] + ' ' + msg
                    plat_gif(f'cards/{pack}/{pack}_{card_colour}_{card_number}.png', 'sparkle', sparkles*3)
                    file = f'./scpos/temp/platout.gif' # Set to plat out
                else:
                    file = f'./scpos/cards/{pack}/{pack}_{card_colour}_{card_number}.png'

            # Add pack section if player doesn't have it yet
            if pack not in player_file['packs'].keys():
                player_file['packs'][pack] = [0 for _ in range(24)]
                player_file['packs'][pack+'_s'] = [0 for _ in range(24)]

            # Remove 1 roll if card was bought
            if bought_card == True:
                player_file['rolls'] -= 1
                msg = msg + f" You have used one of your stored rolls, you have {player_file['rolls']} rolls remaining."
            else:
                # Save new time to file
                player_file['datetime'] = time_text

            # Add extra text to message if it's a new card
            if player_file['packs'][pack][card_value] == 0:
                msg = "NEW CARD! " + msg + self.show_bio(pack, card_colour, card_number)
            
            # Add 1 to streak
            if days_since == 1:
                player_file['stat_streak_current'] += 1
                player_file['stat_streak_longest'] = max(player_file['stat_streak_current'], player_file['stat_streak_longest'])
                msg = f"DAILY STREAK! Current Streak: {player_file['stat_streak_current']}. {msg}" 
            # Reset streak
            elif 10000 > days_since > 1:
                player_file['stat_streak_current'] = 0
                msg = f"DAILY STREAK LOST! Longest Streak: {player_file['stat_streak_longest']}. {msg}"

            # Add one card to total
            player_file['packs'][pack][card_value] += 1
            
            # Add sparkles to total
            if sparkles > 0: # Skip if no sparkles were rolled
                if sparkles > player_file['packs'][pack+'_s'][card_value]: # If you rolled a card with more sparkles than stored
                    player_file['packs'][pack+'_s'][card_value] = sparkles # Set new sparkles
            
            # Add 1 card to stat total
            player_file['stat_rolls'] += 1

            # Write to file
            self.save_player_file(interaction.user.id, player_file)
            
            # Send Message
            print(file)
            await interaction.send(file=nextcord.File(file, spoiler=spoiler))
            await interaction.send(msg)
        else:
            await interaction.send("That is not a pack.")

    @nextcord.slash_command(description="Show your inventory in the SCPOS game")
    async def inventory(self, interaction: Interaction, pack:str = SlashOption(choices=os.listdir('./scpos/cards')), player: nextcord.User = SlashOption(required=False, default=None)):
        
        # Image Creation takes a while
        await interaction.response.defer()
        # ID of selected user
        if player == None:
            player = interaction.user.id
        else:
            player = player.id
        # Load Player File
        player_file = self.load_player_file(player)

        # Colour
        bgr_col = player_file['set_bgr_col']
        try:
            Image.new("RGB", (1,1), bgr_col)
        except ValueError:
            await interaction.send("You have an invalid colour setting. Please change it with /settings bgr_col. (Accepted formats include: Any hex code with a # at the start or any english word for a colour)")
            return

        # Files to output
        files = []
        if pack in player_file['packs'].keys():
            if pack == 'special':
                # SPECIAL
                frames = []
                for i in range(len(os.listdir('./scpos/card effects/plat/'))): # Loop for plat animation frames
                    inv_img = self.inventory_image('special', player_file['packs'][pack] + player_file['packs'][pack+'_s'], False, bgr_col, 'plat', i)
                    frames.append(inv_img.copy()) # Copy the frame to the frame list
                frames[0].save(f"./scpos/temp/inventory.gif", save_all=True, append_images=frames[1:], optimize=True, duration=50, loop=0) # Save as temp image
                files.append(nextcord.File(f"./scpos/temp/inventory.gif"))
            elif 'achievement' in pack:
                # ACHIEVEMENT
                inv_img = self.inventory_image(pack, player_file['packs'][pack] + player_file['packs'][pack+'_s'], 'ach', bgr_col)
                inv_img.save(f"./scpos/temp/inventory.png") # Save as temp image
                files.append(nextcord.File(f"./scpos/temp/inventory.png"))
            else:
                # ANY PACK
                inv_img = self.inventory_image(pack, player_file['packs'][pack] + player_file['packs'][pack+'_s'], True, bgr_col)
                inv_img.save(f"./scpos/temp/inventory.png") # Save as temp image
                files.append(nextcord.File(f"./scpos/temp/inventory.png"))
        
        # Else cases
        elif pack in os.listdir('./scpos/cards'):
            await interaction.send("Player has no cards in this pack.")
        else:
            await interaction.send("Invalid pack name.")
        if files != []:
            await interaction.send(f'<@{player}>', files=files)   

    def inventory_image(self, pack:str, pack_dict:dict, unowned:bool, bgr_col:str='#ff0000', effect:str=None, effect_frame:int=None):
        inv_img = Image.new("RGB", (640, 480), bgr_col) # Create Image with Red Background
        #big_inv_test = Image.new("RGB", (720, 560), bgr_col)
        #big_inv_test = text_image(big_inv_test, pack.title(), (255, 255, 255, 255), 20, (0, 0)) # Pack Text in top left
        inv_img = text_image(inv_img, pack.title(), (255, 255, 255, 255), 20, (320, 0), 'ma') # Pack Text in top center
        for row in range(0, 4): # Add text for each row
            inv_img = text_image(inv_img, str(row+1), (255, 255, 255, 255), 20, (16, 72+(112*row)))
        for x in range(1, 7): # Loop each rarity
            # Add text for each column
            inv_img = text_image(inv_img, colour_ids[x].title(), colour_ids[x], 16, (-48+(x*96), 16))
            for y in range(0, 4): # Loop each card within rarity
                card_amount = pack_dict[(x-1)*4+y]
                if card_amount > 0: # Check if player has this card
                    card_img = Image.open(f"./scpos/cards/{pack}/{pack}_{x}_{y}.png").resize((64, 96)) 
                    if effect != None:
                        plat_img = Image.open(f"./scpos/card effects/{effect}/{effect}_{effect_frame}.png").resize((64, 96)) # Load plat image
                        card_img.paste(plat_img, None, plat_img) # Paste plat image
                elif unowned == 'ach': # Add Achievement Unowned Image
                    if f'{pack}_{x}_{y}.png' in os.listdir(f'./scpos/cards/{pack}/'): # If card exists in folder
                        card_img = Image.open(f"./scpos/unowned/unowned7.png").resize((64, 96))
                    else: # Otherwise do not paste any image
                        continue
                elif unowned == True: # Add Unowned Image
                    card_img = Image.open(f"./scpos/unowned/unowned{x}.png").resize((64, 96))
                else: # If unowned plat card, continue loop (Do not paste a card Image)
                    continue
                inv_img.paste(card_img, (48+(x-1)*96, 32+y*112)) # Paste card image
                inv_img = text_image(inv_img, f'x{card_amount}', (255, 255, 255, 255), 16, (112+(x-1)*96, 112+y*112)) # Write amount text
                # New Star Shit
                star_amount = pack_dict[(x-1)*4+y+24]
                if star_amount > 0:
                    for star in range(star_amount):
                        star_img = Image.open('./scpos/card effects/star_icon.png')
                        inv_img.paste(star_img, (48+(16*star)+(x-1)*96, 128+y*112), star_img)
        return inv_img

    @nextcord.slash_command(description="Sells an amount of cards from your inventory in the SCPOS game", guild_ids=[1039880876982546504])
    async def sellcard(self, interaction: Interaction, 
    pack:str = SlashOption(choices=[pack for pack in os.listdir('./scpos/cards') if pack not in ['achievement', 'achievement2']]), 
    colour:str = SlashOption(choices=["black", "blue", "cyan", "green", "red", "gold"]), 
    num:str = SlashOption(choices=['1', '2', '3', '4']), 
    amount:str = SlashOption(required=False, default='selldupes', choices=['all', 'selldupes', '1', '2', '3', '4', '5', '10'])):

        # Load Player File
        player_file = self.load_player_file(interaction.user.id)
        # Set vars
        colour = colour_ids.index(colour)
        card_id = (colour-1)*4+int(num)-1
        if pack == 'special':
            colour = colour_ids.index('plat')
        # Player has card
        if pack in player_file['packs'].keys():
            if player_file['packs'][pack][card_id] > 0:
                # Options
                if amount == 'all':
                    # Sell ALL
                    new_value = 0
                elif player_file['packs'][pack][card_id] == 1:
                    await interaction.send("WARNING: You only have 1 of this card. If you want to sell ALL of a card, write 'all' in the 'amount' section.")
                    return
                elif amount == 'selldupes':
                    # Sell all down to 1
                    new_value = 1
                elif amount.isdigit():
                    # Sell a number
                    if int(amount) < player_file['packs'][pack][card_id]:
                        new_value = player_file['packs'][pack][card_id] - int(amount)
                    else:
                        await interaction.send("You don't have that many of this card. If you want to sell ALL of a card, write 'all' in the 'amount' section.")
                        return
                selling = player_file['packs'][pack][card_id] - new_value
                player_file['packs'][pack][card_id] = new_value
                # Update gained points
                gain = selling * COLOUR_VALUES[colour] # Give points
                player_file['stat_sold'] += selling # Add stat
                player_file["rolls"] += gain
                # Save to file
                self.save_player_file(interaction.user.id, player_file)
                await interaction.send(f"Sold {selling} card(s). You gained +{gain} roll points.")
            else:
                await interaction.send("You don't own this card.")
        else:
            await interaction.send("You don't have any cards in this pack.")

    @nextcord.slash_command(description="Sells duplicates of cards from your inventory in the SCPOS game")
    async def selldupes(self, interaction: Interaction, 
    rarity:str = SlashOption(required=False, default=4, choices=['1', '2', '3', '4', '5', '6']), 
    pack_option:str = SlashOption(required=False, default='all', choices=[pack for pack in os.listdir('./scpos/cards') if pack not in ['special', 'achievement', 'achievement2']]+['all'], name='pack'),
    check:bool = SlashOption(required=False, default=False)):

        # Load Player File
        player_file = self.load_player_file(interaction.user.id)

        # Loop the file
        gain = 0
        total_sold = 0
        sell_list = []
        if pack_option == 'all':
            packs = [pack for pack in player_file['packs'].keys() if not pack.endswith('_s')] # Packs without stars
            if 'special' in packs:
                packs.remove('special')
            if 'achievement' in packs:
                packs.remove('achievement')
            if 'achievement2' in packs:
                packs.remove('achievement2')
        else:
            if pack_option not in player_file['packs'].keys():
                await interaction.send("You don't have any cards in this pack.")
                return
            packs = [pack_option]
        for pack in packs: # For each pack section
            for card, amount in enumerate(player_file['packs'][pack]): # For each card in pack 
                if card // 4 < int(rarity) and amount > 1: # Wants to sell?
                    # Sell all down to 1
                    selling = amount-1
                    player_file['packs'][pack][card] = 1 # Set to 1
                    # Update gained points
                    gain += selling * COLOUR_VALUES[(card // 4)+1] # Give points
                    total_sold += selling
                    # Sell List
                    if player_file['set_sell_list'] == True and selling > 0:
                        sell_list.append(f'{colour_ids[(card // 4)+1].title()} {(card % 4)+1}, {pack.title()} Pack (x{selling})')
        # Save to file
        player_file['stat_sold'] += total_sold # Add stat
        player_file["rolls"] += gain
        if check == False:
            self.save_player_file(interaction.user.id, player_file)
            await interaction.send(f"Sold {total_sold} card(s). You gained +{gain} roll points. Total: {player_file['rolls']} rolls.")
        else:
            await interaction.send(f"You would sell {total_sold} card(s), and gain +{gain} roll points by doing this.")
        # Send List
        if player_file['set_sell_list'] == True and sell_list != []:
            msgs = squash_text('\n'.join(sell_list) + '\nIf you do not wish to receive these messages, use /settings and set sell_list to false.', '\n')
            [await interaction.user.send(msg) for msg in msgs]

    @nextcord.slash_command(description="View how many roll points you have")
    async def rollpoints(self, interaction: Interaction):
        # Load Player File
        player_file = self.load_player_file(interaction.user.id)
        await interaction.send(f"You have {player_file['rolls']} rolls to use.")

    @nextcord.slash_command(description="Show information on a card")
    async def cardinfo(self, interaction: Interaction,
    pack:str = SlashOption(choices=[pack for pack in os.listdir('./scpos/cards')]), 
    colour:str = SlashOption(choices=["black", "blue", "cyan", "green", "red", "gold"]), 
    num:str = SlashOption(choices=['1', '2', '3', '4'])):

        # Load Player File
        player_file = self.load_player_file(interaction.user.id)
        # Set vars
        colour = colour_ids.index(colour)
        num = int(num)-1
        card_id = (colour-1)*4+num
        msg = ''
        # Player has card
        if pack in player_file['packs'].keys():
            if player_file['packs'][pack][card_id] > 0:
                if pack == 'special': # Animate Plat Card
                    await interaction.response.defer()
                    plat_gif(f'cards/special/special_{colour}_{num}.png', 'plat')
                    file = nextcord.File('./scpos/temp/platout.gif')
                elif player_file['packs'][pack+'_s'][card_id] > 0:
                    sparkles = player_file['packs'][pack+'_s'][card_id]
                    msg = '\n' + sparkle_messages[sparkles-1]
                    plat_gif(f'cards/{pack}/{pack}_{colour}_{num}.png', 'sparkle', sparkles*3)
                    file = nextcord.File(f'./scpos/temp/platout.gif') # Set to plat out
                else:
                    file = nextcord.File(f'./scpos/cards/{pack}/{pack}_{colour}_{num}.png')
                await interaction.send(self.show_bio(pack, colour, num) + msg, file=file)
                return
        await interaction.send("You don't own this card!")

    def show_bio(self, pack, colour, num):
        # Get Bio info
        with open('./scpos/bios.json', encoding='utf=8') as bios_file:
            bios = json.load(bios_file)
            try:
                bio_data = bios[pack][colour-1][num]
                text = '\n'
                for key, data in bio_data.items():
                    if key == 'name':
                        text += "Card Name: " + data
                    elif key == 'creator':
                        text += '\nSubmitted By: ' + data
                    elif key == 'meta':
                        text += '\n' + data
                    else:
                        text += '\n' + key.title() + ': ' + data
            except (KeyError, IndexError):
                text = "No Information Avaliable"
            return text

    @nextcord.slash_command(description="Search all users for a card")
    async def cardsearch(self, interaction: Interaction, 
    pack:str = SlashOption(choices=[pack for pack in os.listdir('./scpos/cards')]), 
    colour:str = SlashOption(choices=["black", "blue", "cyan", "green", "red", "gold"]), 
    num:str = SlashOption(choices=['1', '2', '3', '4'])):

        await interaction.response.defer()
        # Init Return Vars
        card_id = (colour_ids.index(colour)-1)*4 + int(num)-1
        msg = ""
        # Loop all files
        for player in os.listdir('./scpos/playerdata'):
            # Open file
            with open(f'./scpos/playerdata/{player}', 'rb') as f:
                player_file = pickle.load(f)
            # Check if they have the card
            if pack in player_file['packs'].keys():
                if player_file['packs'][pack][card_id]:
                    user = await self.client.fetch_user(player[:-7])
                    msg += f"{user.name}: owns {player_file['packs'][pack][card_id]} of this card."+'\n'
        if msg == '': # In no one owns
            msg = "Nobody owns this card yet!"
        msg = f"{colour.title()} {num}, {pack.title()} Pack:" + '\n' + msg # Add card text
        await interaction.send(msg)

    @nextcord.slash_command(description="Show your stats")
    async def showstat(self, interaction: Interaction, stat:str = SlashOption(choices=['rolls', 'sold', 'cards', 'specials', 'achievements', 'stars', '3-stars', 'streak_current', 'streak_longest', 'rolls_since_last_special'])):
        
        # Load Player File
        player_file = self.load_player_file(interaction.user.id)
        # Check stat search
        if stat == 'cards':
            await interaction.send(f"Total {stat.title()}: {sum([sum(player_file['packs'][pack]) for pack in player_file['packs'] if not pack.endswith('_s')])}")
        elif stat == 'stars':
            await interaction.send(f"Total {stat.title()}: {sum([sum(player_file['packs'][pack]) for pack in player_file['packs'] if pack.endswith('_s')])}")
        elif stat == '3-stars':
            await interaction.send(f"Total {stat.title()}: {sum([player_file['packs'][pack].count(3) for pack in player_file['packs'] if pack.endswith('_s')])}")
        elif stat == 'specials':
            if 'special' not in player_file['packs']:
                player_file['packs']['special'] = [0]
            await interaction.send(f"Total {stat.title()}: {sum(player_file['packs']['special'])}")
        elif stat == 'achievements':
            await interaction.send(f"Total {stat.title()}: {len(player_file['achievements'])}")
        else:
            await interaction.send(f"Total {stat.title().replace('_', ' ')}: {player_file['stat_'+stat]}")


    @nextcord.slash_command(description="Show the leaderboard for a stat")
    async def leaderboard(self, interaction: Interaction, 
    stat:str = SlashOption(choices=['rolls', 'sold', 'cards', 'specials', 'achievements', 'stars', '3-stars', 'streak_current', 'streak_longest', 'rolls_since_last_special'])):

        await interaction.response.defer()
        stats = {}
        embed = nextcord.Embed(title=f"Leaderboard", color=0x00c030)
        # Loop all files
        for player in [u for u in os.listdir('./scpos/playerdata') if u != 'DEFAULT.pickle']:
            # Open file
            with open(f'./scpos/playerdata/{player}', 'rb') as f:
                player_file = pickle.load(f)
            if stat == 'cards':
                # Calculate sum of cards
                key = sum([sum(player_file['packs'][pack]) for pack in player_file['packs'] if not pack.endswith('_s')])
            elif stat == 'stars':
                # Calculate sum of stars
                key = sum([sum(player_file['packs'][pack]) for pack in player_file['packs'] if pack.endswith('_s')])
            elif stat == '3-stars':
                # Number of extremely sparkly
                key = sum([player_file['packs'][pack].count(3) for pack in player_file['packs'] if pack.endswith('_s')])
            elif stat == 'specials':
                # Calculate sum of special cards
                if 'special' not in player_file['packs']:
                    continue
                key = sum(player_file['packs']['special'])
            elif stat == 'achievements':
                # Grab achievement count
                key = len(player_file['achievements'])
            else:
                key = player_file['stat_'+stat]
            if key not in stats.keys():
                stats[key] = [player[:-7]] # Set value key to the user id
            else:
                stats[key].append(player[:-7]) # Else append the value key with new user id (for ties)
        
        # Sort the board
        top10 = sorted(stats.keys(), reverse=True)[:10]
        msg = ''
        place = 1
        for stat_val in top10:
            if stat_val == 0:
                break
            for player in stats[stat_val]: # Loop players in key (ties)
                try:
                    user = await self.client.fetch_user(player) # Fetch user
                    user = user.name
                except nextcord.errors.NotFound:
                    user = "*Unknown*"
                msg += f"{place}: {user} - {stat_val}"+'\n' # Placement with colon because discord likes to change numbered lists
            place += len(stats[stat_val])

        embed.add_field(name=f"Total {stat.title().replace('_',' ')}", value=msg)
        await interaction.send(embed=embed)

    @nextcord.slash_command(description="Shows your achievement progress")
    async def achievementlist(self, interaction: Interaction):
        # Initialize the loop
        achievement_order = {"Rolling": ['Roll One Time', 'Roll One Hundred Times', "Roll One Thousand Times", "Roll Ten Thousand Times", "Use a Stored Roll", "Reach a Week Long Streak", "Reach a Month Long Streak"],
                             "Pack Completion": ["Complete the Basic Pack", "Complete the Extended Pack", "Complete the Gacha Pack", "Complete the Trap Pack", "Complete the Speedrun Pack", "Complete the Sport Pack", "Complete the TCG Pack", "Complete the Starters Pack", "Complete the Powerful Men Pack", "Complete the Scott Pack", "Complete the Indie Pack", "Complete the Identification Pack", "Complete the Not Identification Pack"],
                             "Collection Challenges": ["Obtain an Extremely Sparkly Card", "Obtain 100 of any Card", "Obtain a Sparkly variant of all Cards in a Pack"],
                             "Misc": ["Sell a Card", "*DMS Speedrunner", "*Tom's Birthday"]}
        embed = nextcord.Embed(title=f"Achievements List", color=240*0x10000 + 0x3000 + 240)
        player_file = self.load_player_file(interaction.user.id)
        for subtitle, achieves in achievement_order.items(): # Loop Categories
            output = ""
            for achieve in achieves: # Loop Achievements
                if achieve in player_file['achievements']:
                    if achieve.startswith("*"): # Hidden Achievements remove *
                        achieve = achieve[1:]
                    output += f"\n:white_check_mark: {achieve}"
                else:
                    if achieve.startswith("*"): # Hidden Achievements change text
                        achieve = "Hidden Achievement"
                    output += f"\n:x: {achieve}"
            embed.add_field(name=subtitle, value=output, inline=False) # Add Text to the embed
        await interaction.send(embed=embed)

    # @nextcord.slash_command(description="Inventory Testing")
    # async def new_inv(self, interaction: Interaction):
    #     embed = nextcord.Embed(title=f"Leaderboard", color=0xc0c000)
    #     f = nextcord.File('./scpos/temp/inventory.png')
    #     embed.set_image(f'attachment://{f.filename}')
    #     help_button = Button(custom_id="help_button", style=ButtonStyle.blurple, label="Click here")
    #     view = nextcord.ui.View()
    #     view.add_item(item=help_button)
    #     await interaction.send(embed=embed, file=f, view=view)

    # @nextcord.ui.button(style=ButtonStyle.blurple, label="Click here")
    # async def button_click(self, button: nextcord.ui.Button, interaction: Interaction):
    #     if interaction.component.custom_id == "help_button":
    #         f = nextcord.File('./scpos/temp/inventory.png')
    #         await interaction.message.edit(file=f, components=[])
    #     await interaction.respond(type=InteractionType.UpdateMessage)

    # @nextcord.slash_command(description="Roll Tests", guild_ids=[1039880876982546504])
    # async def rolltests(self, interaction: Interaction, tests:int = SlashOption(), achievements:int = SlashOption()):

    #     difference = [[],[],[],[],[],[],[]]
    #     await interaction.response.defer()
    #     for a in range(achievements+1):
    #         totals = [0,0,0,0,0,0,0]
    #         for _ in range(tests):
    #             # Apply Modifiers
    #             a=1
    #             if a != 0:
    #                 boost = 10 ** (a/achievements)
    #                 [print(1 + boost*(sum(rarity_chances)/weight -1)) for weight in rarity_chances]
    #                 modified_chances = [int(weight * log(100 - 1 + boost*(sum(rarity_chances)/weight -1))) for weight in rarity_chances]
    #                 #boost = (1 + (a/achievements) * 0.5) ** (weight/1000)
    #             else:
    #                 modified_chances = rarity_chances

    #             # Choose Rarity
    #             card_colour = random_weighted([i+1 for i in range(7)], modified_chances)
    #             totals[card_colour-1] += 1
    #             return
    #         [difference[v].append(totals[v]) for v in range(7)]
    #         #await interaction.send(f'With {a}/{achievements}:\n'+'\n'.join([f'{i}: {ii}' for i, ii in enumerate(totals)]))
    #     await interaction.send(f'Totals:\n'+'\n'.join([f'{i}: {ii}' for i, ii in enumerate(difference)]))

    @nextcord.slash_command(description="Change your settings")
    async def settings(self, interaction: Interaction, setting:str = SlashOption(choices=['sell_list', 'bgr_col'], required=True), choice:str = SlashOption(required=True)):
        # Open File
        player_file = self.load_player_file(interaction.user.id)
        save_choice = ''

        # I did this bad
        if setting == 'sell_list':
            if choice in ['true', 'True', 't', 'T']:
                save_choice = True
            if choice in ['false', 'False', 'f', 'F']:
                save_choice = False
        # DO THIS HERE
        elif setting == 'bgr_col':
            try:
                Image.new("RGB", (1,1), choice)
                save_choice = choice
            except ValueError:
                await interaction.send("This is an invalid colour setting. (Accepted formats include: Any hex code with a # at the start or any english word for a colour)")
                return
        
        # Set choice
        if save_choice != '':
            player_file['set_'+setting] = save_choice
        else:
            await interaction.send("This is an invalid setting")
            return

        # Write to file
        self.save_player_file(interaction.user.id, player_file)
        await interaction.send(f"Set preference *{setting}* to *{save_choice}*.")

    @nextcord.slash_command(guild_ids=[1039880876982546504])
    async def scpos_admin(self, interaction: Interaction, params:str = SlashOption()):
        if interaction.user.id == 244616599443603456:
            params = params.split(' ')
            if params[1] == 'me':
                params[1] = 244616599443603456
            # Add Roll Points to user
            if params[0] == 'rolls':
                # Load Player File
                player_file = self.load_player_file(params[1])
                player_file["rolls"] += float(params[2])
                self.save_player_file(params[1], player_file)
                await interaction.send(f"Added {params[2]} rolls to <@{params[1]}>", ephemeral=True)
            # Change Card Colour Rarities
            elif params[0] == 'rarity':
                rarity_chances[colour_ids.index(params[1])-1] = int(params[2])
                await interaction.send(f"Rarity chances now: {rarity_chances}", ephemeral=True)
            # Change Sell Prices
            elif params[0] == 'price':
                global COLOUR_VALUES
                if params[1] == 'all':
                    COLOUR_VALUES = [value*float(params[2]) for value in COLOUR_VALUES]
                else:
                    COLOUR_VALUES[colour_ids.index(params[1])] = float(params[2])
                await interaction.send(f"Sell prices now: {COLOUR_VALUES}", ephemeral=True)
            elif params[0] == 'cardadd':
                player_file = self.load_player_file(params[1])
                player_file['packs'][params[2]][int(params[3])] += int(params[4])
                self.save_player_file(params[1], player_file)
                await interaction.send(f"Added {params[4]} of card {params[3]} in pack {params[2]} to <@{params[1]}>", ephemeral=True)
            elif params[0] == 'packadd':
                player_file = self.load_player_file(params[1])
                if params[2] not in player_file['packs'].keys():
                    player_file['packs'][params[2]] = [int(params[3]) for _ in range(24)]
                    player_file['packs'][params[2]+'_s'] = [0 for _ in range(24)]
                    self.save_player_file(params[1], player_file)
                    await interaction.send("Add pack to user", ephemeral=True)
                else:
                    await interaction.send("User already has this pack", ephemeral=True)
            elif params[0] == 'viewfile':
                player_file = self.load_player_file(params[1])
                print(player_file)
                for msg in squash_text(str(player_file), " "):
                    await interaction.send(f'```{msg}```', ephemeral=True)
            elif params[0] == 'keyeditor':
                player_file = self.load_player_file(params[1])
                if params[3].isdigit():
                    player_file[params[2]] = int(params[3])
                else:
                    player_file[params[2]] = params[3]
                self.save_player_file(params[1], player_file)
                await interaction.send(f"Changed key {params[2]} to {params[3]}", ephemeral=True)
            else:
                await interaction.send(f"Options: 'rolls <user> <num>' 'rarity <colour> <value>' 'price <colour> <value>' 'cardadd <user> <pack> <cardid> <aount>' 'packadd <user> <pack>' 'viewfile <user>'", ephemeral=True)
        else:
            await interaction.send(file=nextcord.file('./scpos/card effects/ayo.png'))
            print("someone ayo'd")

class Trading(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client
    
    @nextcord.slash_command(description="Initialize a trade")
    async def tradestart(self, interaction: Interaction, user: nextcord.User = SlashOption(required=True)):

        # Define Shit
        starter_user = interaction.user.id
        partner_user = user.id

        # Check if a trade has started
        if starter_user in [user for users in trades for user in users]: # Yeah I got this one from the internet
            await interaction.send("A trade has already started between you and someone. Clear it with /tradecancel")
            return
        # Init Trade
        if starter_user == partner_user:
            await interaction.send("You cannot trade with yourself!")
            return
        elif f'{partner_user}.pickle' not in os.listdir('./scpos/playerdata/'):
            await interaction.send("This user has no cards!")
            return
        trades[(starter_user, partner_user)] = {}
        trades[(starter_user, partner_user)]["give"] = {}
        trades[(starter_user, partner_user)]["request"] = {}
        trades[(starter_user, partner_user)]["status"] = 'editing'
        await interaction.send("Initiated a trade. Use /tradegive to add cards to your offer, and /traderequest to add cards to your partner's offer.")

    def get_trade_partner(self, user_id):
        user_list = [user for users in trades for user in users]
        if user_id not in user_list:
            return None, None
        if user_list.index(user_id) % 2 == 0:
            # Starter User
            return user_id, user_list[user_list.index(user_id)+1]
        else:
            # Partner User
            return user_list[user_list.index(user_id)-1], user_id

    @nextcord.slash_command(description="Give a card to your trade offer")
    async def tradegive(self, interaction: Interaction, 
    pack:str = SlashOption(choices=[pack for pack in os.listdir('./scpos/cards')]), 
    colour:str = SlashOption(choices=["black", "blue", "cyan", "green", "red", "gold"]), 
    num:str = SlashOption(choices=['1', '2', '3', '4']),
    amount:str = SlashOption(required=False, default='1')):

        # Find the partner User
        starter_user, partner_user = self.get_trade_partner(interaction.user.id)

        # Run the other ting
        if amount.isdecimal():
            if int(amount) > 0:
                await interaction.send(self.trade_add_item(starter_user, partner_user, "give", pack, colour, num, int(amount)))
                return
        await interaction.send("Invalid Amount value")

    @nextcord.slash_command(description="Request a card to your trade offer")
    async def traderequest(self, interaction: Interaction, 
    pack:str = SlashOption(choices=[pack for pack in os.listdir('./scpos/cards')]), 
    colour:str = SlashOption(choices=["black", "blue", "cyan", "green", "red", "gold"]), 
    num:str = SlashOption(choices=['1', '2', '3', '4']),
    amount:str = SlashOption(required=False, default='1')):

        # Find the partner User
        starter_user, partner_user = self.get_trade_partner(interaction.user.id)

        # Run the other ting
        if amount.isdecimal():
            if int(amount) > 0:
                await interaction.send(self.trade_add_item(starter_user, partner_user, "request", pack, colour, num, int(amount)))
                return
        await interaction.send("Invalid Amount value")

    def trade_add_item(self, starter_user, partner_user, give:str, pack, colour, num, amount):
        
        trade_key = (starter_user, partner_user)

        # Check if a trade has started
        if starter_user not in [user for users in trades for user in users]:
            return "You have no current trade to edit! Start a trade offer with /tradestart"
        if starter_user in [users[1] for users in trades]:
            return "Someone else has started a trade with you, only they can edit the trade until it's sent"
        # Past Editing
        if trades[trade_key]['status'] != 'editing':
            return "Your trade is past editing status. You cannot continue editing your offer"

        # Open file
        if give == "give": # Open your file if you're giving
            player_file = SCPOS.load_player_file(SCPOS, starter_user)
        elif give == "request": # Open their file if you're receiving
            player_file = SCPOS.load_player_file(SCPOS, partner_user)
        # Check if user has card
        if pack in player_file['packs'].keys():
            if player_file['packs'][pack][(colour_ids.index(colour)-1)*4+int(num)-1] > 0:
                # Amount Check
                if player_file['packs'][pack][(colour_ids.index(colour)-1)*4+int(num)-1] < amount:
                    if give == "give":
                        return "You don't have that many of this card!"
                    elif give == "request":
                        return "They don't have that many of this card!"
                if (pack, colour, num) in trades[trade_key][give]:
                    if trades[trade_key][give][(pack, colour, num)] == amount:
                        trades[trade_key][give].pop((pack, colour, num))
                        return f"Removed Card: {colour.title()} {num}, {pack.title()} Pack"
                    else:
                        trades[trade_key][give][(pack, colour, num)] = amount
                        return f"Changed Card: {colour.title()} {num}, {pack.title()} Pack x{amount}"
                else:
                    trades[trade_key][give][(pack, colour, num)] = amount
                    return f"Added Card: {colour.title()} {num}, {pack.title()} Pack x{amount}"
        if give == "give":
            return "You don't own this card!"
        elif give == "request":
            return "They don't own this card!"

    @nextcord.slash_command(description="Cancel your current trade offer")
    async def tradecancel(self, interaction: Interaction):
        # Partner users are intended to be able to cancel the starter's trade (they cannot do anything else though)
        # Check if a trade has started
        if interaction.user.id in [user for users in trades for user in users]:

            # Find the partner User
            trade_key = self.get_trade_partner(interaction.user.id)
            # Delete the trade
            trades.pop(trade_key)
            await interaction.send("Trade cancelled.")
        else:
            await interaction.send("There was no trade to cancel.")

    @nextcord.slash_command(description="View your current trade offer")
    async def tradeview(self, interaction: Interaction):

        # Find the partner User
        trade_key = self.get_trade_partner(interaction.user.id)

        # Debug
        print(trades)

        # Stop if there is no trade
        if trade_key == (None, None):
            await interaction.send("You have no current trade to edit! Start a trade offer with /tradestart")
            return
        
        # Format the trade
        response = self.format_trade(trade_key[0], trade_key[1])
        response += "Trade Status: " + trades[trade_key]['status'].title()
        await interaction.send(response)

    def format_trade(self, starter_user, partner_user):
        trade = trades[(starter_user, partner_user)]
        response = f"<@{starter_user}> will give: " +'\n'
        for card, amount in trade["give"].items():
            response += f"- {card[1].title()} {card[2]}, {card[0].title()} Pack x{amount}" +'\n'
        response += f"<@{partner_user}> will give: " +'\n'
        for card, amount in trade["request"].items():
            response += f"- {card[1].title()} {card[2]}, {card[0].title()} Pack x{amount}" +'\n'
        return response

    @nextcord.slash_command(description="Send your current trade offer")
    async def tradesend(self, interaction: Interaction):
        # Find the partner User
        starter_user, partner_user = self.get_trade_partner(interaction.user.id)

        if partner_user == interaction.user.id:
            await interaction.send("Someone else has started a trade with you, they must send the trade for you to accept or deny")
            return
        if starter_user != interaction.user.id:
            await interaction.send("You have no current trade to edit! Start a trade offer with /tradestart")
            return
        if trades[(starter_user, partner_user)]['status'] == 'editing':
            # Format offer message
            offer_response = f"<@{partner_user}>: You have been given an offer from <@{starter_user}>" + '\n'
            offer_response += self.format_trade(starter_user, partner_user)
            offer_response += 'To accept this deal, type /tradeaccept. Or to decline this deal, type /tradecancel'
            # Send offer to other user
            trades[(starter_user, partner_user)]['status'] = 'awaiting response'
            await interaction.send(offer_response)
        
    @nextcord.slash_command(description="Accept a trade offer")
    async def tradeaccept(self, interaction: Interaction): 
        # Find the partner User
        starter_user, partner_user = self.get_trade_partner(interaction.user.id)

        # Use Cases
        if (starter_user, partner_user) not in trades:
            await interaction.send("You have no current trade to edit! Start a trade offer with /tradestart")
            return
        trade = trades[(starter_user, partner_user)]
        if trade['status'] != 'awaiting response':
            await interaction.send("This trade is still in the editing phase!")
            return
        if starter_user == interaction.user.id:
            await interaction.send("You have made this offer to your partner, only they can accept or deny the trade")
            return

        # Accept the deal
        # Init Files
        offerer_file = SCPOS.load_player_file(SCPOS, starter_user)
        offeree_file = SCPOS.load_player_file(SCPOS, partner_user)
        # Delete and add the cards for the users
        for card, amount in trade["give"].items():
            offerer_file = self.remove_card(offerer_file, card[0], card[1], card[2], amount)
            offeree_file = self.add_card(offeree_file, card[0], card[1], card[2], amount)
        for card, amount in trade["request"].items():
            offeree_file = self.remove_card(offeree_file, card[0], card[1], card[2], amount)
            offerer_file = self.add_card(offerer_file, card[0], card[1], card[2], amount)
        # Save files
        SCPOS.save_player_file(SCPOS, partner_user, offeree_file)
        SCPOS.save_player_file(SCPOS, starter_user, offerer_file)
        # Delete Trade
        trades.pop((starter_user, partner_user))
        await interaction.send("Trade Complete.")

    def remove_card(self, file, pack, colour, num, amount):
        # Change option
        card_id = (colour_ids.index(colour)-1)*4+int(num)-1
        print(pack)
        # Remove Amount
        file['packs'][pack][card_id] -= amount
        return file
    
    def add_card(self, file, pack, colour, num, amount):
        # Change option
        card_id = (colour_ids.index(colour)-1)*4+int(num)-1
        # Add pack section if player doesn't have it yet
        if pack not in file['packs'].keys():
            file['packs'][pack] = [0 for _ in range(24)]
            file['packs'][pack+'_s'] = [0 for _ in range(24)]
        # Add amount
        file['packs'][pack][card_id] += amount
        return file

def setup(client):
    client.add_cog(SCPOS(client))
    client.add_cog(Trading(client))

# Retro Pack + Alecs
# Events for free rolls
# Currency and Golden packs from OG
# Settings option more clear
"""
1-mine,rox,costiler,hypnoshark
2-/,juzockt,hag,fire
3-KingJ,flygon,blood,shm
4-/,hex,derek,connor
5-Midbro,odme,hammer,zl
6-/,jhay,nitrof,/
plat- duck

scavi- flamigo, meows, hawlucha, luc
x/y- hawlucha, lucario, chespin
sword- inteleon, candyfloss, ninetales, etern
plge- starmie, eevee
hgss- raikou, typhosion
oras- groudon, mudkip, latios,
bw- excadrill, stoutland
rby- blastoise, nidoking, bulbasaur, missingno
bdsp- 
sumo- primarina

1-brock, misty, blaine, giovanni
2-clair, falkner, whitney, jasmine
3-TnL, juan, roxanne, norman
4-roark, fantina, skyla, clay
5-clemont, korrina, mallow, suiren
6-nessa, raihan, iono, larry
Tee En El, as Shen would say

3500, 2500, 1500, 1000, 500, 200, 10 = 9210
38%, 27.14%, 16.29%, 10.86%, 5.23%, 2.17%, 0.11%
"""