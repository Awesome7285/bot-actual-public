import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import os
import sys
import subprocess
#import pyuac
from cogs.func.funcs import squash_text, IncorrectInputError
from datetime import datetime
import mouse as m
import time

# Run as Admin
# if not pyuac.isUserAdmin():
    
#     print("Re-launching as admin!")
#     os.popen('/cogs/func/startup.py')
#     pyuac.runAsAdmin()
#     exit()


# Bot Setup
intents = nextcord.Intents.default()
client = commands.Bot(intents=intents)
TOKEN = open('TOKEN').read()

# On Ready
@client.event
async def on_ready():
    try:
        await client.get_channel(1039883119936929832).send("Bot Actual Online!")
    except nextcord.errors.Forbidden:
        await client.get_channel(1039899242711490670).send("Bot Actual Betas Online!")
    print("Main Bot Online")

# Ping command
@client.slash_command(description="replies with pong")
async def ping(interaction: Interaction):
    await interaction.response.send_message("Pong!")

# # Reload Extentions
# @client.slash_command(description='Reloads a module', guild_ids=[1039880876982546504])
# async def reload(interaction: Interaction, extension: str):
#     if interaction.user.id == 244616599443603456:
#         try:
#             client.unload_extension(f'cogs.{extension}')
#             client.load_extension(f'cogs.{extension}')
#             await interaction.send(f"Reloaded {extension}", ephemeral=True)
#         except commands.errors.ExtensionNotLoaded:
#             await interaction.send("Unknown Extension", ephemeral=True)

# Exit Bot
@client.slash_command(description='Aborts the bot (Admin Only)', guild_ids=[1039880876982546504])
async def abort(interaction: Interaction):
    if interaction.user.id == 244616599443603456:
        try:
            ping_channel = await client.fetch_channel(1039883119936929832)
            await ping_channel.send("Bot Going Offline!")
            await interaction.send("Message Posted", ephemeral=True, delete_after=3)
            exit()
        except nextcord.errors.Forbidden:
            await interaction.send("Betas must be restarted manually", ephemeral=True, delete_after=3)
    else:
        await interaction.send("You do not have the permission to do this.")

# Help
@client.slash_command(description='Shows help')
async def help(interaction: Interaction):
    scpos_message = 'In the card collector game, users get to use /rollcard every hour to obtain a random card and a drop-down will appear for a Pack to choose. All packs have 24 cards, with black being the most common and gold being the rarest. Use /inventory to view your cards in a pack. If you\'re really lucky, you may even find yourself a very special card...'
    gif_message = 'Use the gifs utility to create your own memes with /creatememe. A list of preset of images are in the drop down for you to use, image uploading and GIF creating is still in development.'
    civ_message = "Use the CIV utility to easily create multiplayer games for Civilization VI. All players must use the one-time /civaddplayer command to add their owned DLCs, then games can be ran with /civcreategame (multiplayer) or /civrandom (singleplayer). Both vanilla and modded options are available"
    quotes_message = 'Use the quotes utility for your server to create your own quote list. Use /addquote to add a quote to the list, and /quote will show a random quote from the list.'
    skrib_message = 'Use the skrib utility for your server to create your own words list. Use /addword to add a word to the list, and /skribwords to get a number of random words from the list. (Designed to be used with skribbl.io\'s custom words option).'
    embed = nextcord.Embed(title=f"Help for Bot Actual", color=0xc0c000)
    embed.add_field(name="Card Collector", value=scpos_message)
    embed.add_field(name="GIFs", value=gif_message, inline=False)
    embed.add_field(name="CIV", value=civ_message, inline=False)
    embed.add_field(name="Quotes", value=quotes_message, inline=False)
    embed.add_field(name="Skribbl.io Words", value=skrib_message, inline=False)
    await interaction.send(embed=embed)

# Update 
@client.slash_command(description='Updates the bot (Admin only)', guild_ids=[1039880876982546504])
async def update(interaction: Interaction):
    if interaction.user.id == 244616599443603456:
        await interaction.response.defer()
        # Run git fetch
        subprocess.call(['git', 'pull'])
        await interaction.send("Git has been fetched.")
    else:
        await interaction.send("You do not have the permission to do this.")


# Restart
@client.slash_command(description='Restarts the bot (Admin only)', guild_ids=[1039880876982546504])
async def restart(interaction: Interaction, shutdown: bool = SlashOption(required=False, default=False)):
    if interaction.user.id == 244616599443603456:
        try:
            ping_channel = await client.fetch_channel(1039883119936929832)
            await ping_channel.send("Bot Restarting...!")
            await interaction.send("Message Posted", ephemeral=True, delete_after=3)
            if shutdown:
                # Restart the PC on Windows
                os.system('shutdown /r /t 0')
            else:
                os.popen('bot.py')
                exit()
        except nextcord.errors.Forbidden:
            await interaction.send("Betas must be restarted manually", ephemeral=True, delete_after=3)
    else:
        await interaction.send("You do not have the permission to do this.")

# Update message
@client.slash_command(description='Announces a new update (Admin only)', guild_ids=[1039880876982546504])
async def announce(interaction: Interaction):
    if interaction.user.id == 244616599443603456:
        pass
    else:
        await interaction.send("You do not have the permission to do this.")

# Load Extentions
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

# Run Bot
client.run(TOKEN)
