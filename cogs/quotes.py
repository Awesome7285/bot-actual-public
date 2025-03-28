import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import os
import shutil
from configparser import ConfigParser
from random import randint
from .func.funcs import squash_text, IncorrectInputError

# Initialize File
QUOTE_SERVERS = {}
for file in os.listdir('./quotes'):
    server_quotes = {}
    server_quotes["LOCATION"] = f'quotes/{file}'
    server_quotes["QUOTES"] = ConfigParser()
    server_quotes["QUOTES"].read(server_quotes["LOCATION"], encoding='utf-8')
    try:
        server_quotes["TOTAL"] = int(server_quotes["QUOTES"].sections()[-1])
    except ValueError:
        server_quotes["TOTAL"] = 0
    names = []
    for i in range(1, server_quotes["TOTAL"]+1):
        if server_quotes["QUOTES"].has_option(str(i), 'name'):
            for n in server_quotes["QUOTES"][str(i)]['name'].split(", "):
                if n not in names:
                    names.append(n)
    names.sort()
    server_quotes["NAMES"] = names
    QUOTE_SERVERS[int(file[:-4])] = server_quotes
# print(QUOTE_SERVERS)
# QUOTES = ConfigParser()
# QUOTES.read(QUOTES_LOCATION, encoding='utf-8')
# TOTAL_QUOTES = int(QUOTES.sections()[-1])

# Gets a list of all names in the quotes DB
# def get_all_names():
#     """
#     Gets a list of all names in the quotes DB
#     Taken directly from old quotesbot.py
#     """
#     names = []
#     for i in range(1, TOTAL_QUOTES+1):
#         if QUOTES.has_option(str(i), 'name'):
#             for n in QUOTES[str(i)]['name'].split(", "):
#                 if n not in names:
#                     names.append(n)
#     names.sort()
#     return names
# QUOTE_NAMES = get_all_names()

class Quotes(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client
    
    # Ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Quotes is online.")

    # Test
    # @nextcord.slash_command(description="Pings the quotes bot")
    # async def quotes_ping(self, interaction: Interaction):
    #     await interaction.response.send_message("Quotes is online.")

    # Get Quote
    @nextcord.slash_command(description="Gets a random quote, or quote with specified number")
    async def quote(self, interaction: Interaction, q_num:str = SlashOption(required=False, default='None', name='number'), context:str = SlashOption(required=False, default="none", choices=["none", "context"])):

        # No Quotes for server
        if interaction.guild_id not in QUOTE_SERVERS.keys():
            await interaction.send("Your server must enable quotes first. Use ~~setupquotes")
            return
        # Quote from number
        if q_num.isdigit():
            try:
                # Checks if quote is deleted, but also checks QUOTES[q_num] exists (i.e out of range)
                if QUOTE_SERVERS[interaction.guild_id]["QUOTES"][q_num]['quote'] == 'DEL':
                    raise KeyError
            except KeyError:
                await interaction.send("Invalid Quote Number")
                return
            quote_string = self.format_quote(q_num, interaction.guild_id, context)
            await interaction.send(quote_string)
        
        # Random Quote
        elif q_num == 'None':
            while QUOTE_SERVERS[interaction.guild_id]["QUOTES"][q_num]['quote'] == 'DEL' and q_num == 'None': 
                q_num = str(randint(1, QUOTE_SERVERS[interaction.guild_id]["TOTAL"]))
            quote_string = self.format_quote(q_num, interaction.guild_id, context)
            await interaction.send(quote_string)
    
    # Format Quote to String
    def format_quote(self, q_num, guild_id, context):
        quote = QUOTE_SERVERS[guild_id]["QUOTES"][q_num]
        quote_string = f'Quote #{q_num}: '
        segments = quote['quote'].split(',,')
        names = quote['name'].split(', ')
        for segment in range(len(segments)):
            quote_string += f'{segments[segment]} - {names[segment]}, '
        quote_string += quote['year']
        if context == "context":
            if quote["context"] == "":
                quote_string += '\n\nNo context provided for this quote.'
            else:
                quote_string += f'\n\nContext: {quote["context"]}'
        return quote_string

    # Get Quote Names
    @nextcord.slash_command(description="Gets a list of all names in the quote database")
    async def quotename(self, interaction: Interaction, names:str = SlashOption(required=False, default='', name='name')):

        # First Quote for server
        if interaction.guild_id not in QUOTE_SERVERS.keys():
            await interaction.send("Your server must enable quotes first. Use ~~setupquotes")
            return
        # Combine names variable
        if names == '':
            [await interaction.send('```\n'+msg+'\n```') for msg in squash_text('\n'.join(QUOTE_SERVERS[interaction.guild_id]["NAMES"]), '\n')]
        else:
            if names.lower() in [n.lower() for n in QUOTE_SERVERS[interaction.guild_id]["NAMES"]]:
                quote_msg= ''
                for quote in range(1, QUOTE_SERVERS[interaction.guild_id]["TOTAL"]): # Loop all quotes
                    if QUOTE_SERVERS[interaction.guild_id]["QUOTES"].has_option(str(quote), 'name'): # Checks if section exists, because some deleted quotes have no name
                        if names in QUOTE_SERVERS[interaction.guild_id]["QUOTES"][str(quote)]["name"].split(', '): # Check the name
                            quote_msg += self.format_quote(str(quote), interaction.guild_id, None)+'\n'
                [await interaction.send('```\n'+msg+'\n```') for msg in squash_text(quote_msg, '\n')]
            else:
                await interaction.send("No quotes by person with this name.")

    # Add Quote
    @nextcord.slash_command(description="Adds a quote to the quote database")
    async def addquote(self, interaction: Interaction, quote:str, name:str, year:int,
        quote2: str = SlashOption(required=False, default=None),
        name2: str = SlashOption(required=False, default=None),
        quote3: str = SlashOption(required=False, default=None),
        name3: str = SlashOption(required=False, default=None),
        quote4: str = SlashOption(required=False, default=None),
        name4: str = SlashOption(required=False, default=None)):

        global QUOTE_SERVERS

        # First Quote for server
        if interaction.guild_id not in QUOTE_SERVERS.keys():
            await interaction.send("Your server must enable quotes first. Use `~~setupquotes`")
            return
        new_quote = {"quote": [quote for quote in [quote, quote2, quote3, quote4] if quote != None], "name": [name for name in [name, name2, name3, name4] if name != None]}
       # Add to quotes
        QUOTE_SERVERS[interaction.guild_id]["QUOTES"][str(QUOTE_SERVERS[interaction.guild_id]["TOTAL"]+1)] = {'quote': ',,'.join(new_quote['quote']),
                                       'name': ', '.join(new_quote['name']),
                                       'year': year,
                                       'list': '',
                                       'context': ''}
        with open(QUOTE_SERVERS[interaction.guild_id]["LOCATION"], 'w', encoding='utf-8') as configfile:
            QUOTE_SERVERS[interaction.guild_id]["QUOTES"].write(configfile)
        await interaction.send(f'Added Quote Entry #{str(QUOTE_SERVERS[interaction.guild_id]["TOTAL"]+1)}:\n{self.format_quote(str(QUOTE_SERVERS[interaction.guild_id]["TOTAL"]+1), interaction.guild_id, False)}')
        QUOTE_SERVERS[interaction.guild_id]["TOTAL"] += 1

    # Delete Quote
    @nextcord.slash_command(description="Not Implemented")
    async def delquote(self, interaction: Interaction):
        """
        Not Implemented.
        """
        pass
        #ctx.author.roles

    # Setup Quotes for new servers
    @nextcord.slash_command(description="Sets up the quotes bot for this server")
    async def setupquotes(self, interaction: Interaction):
        if interaction.guild_id not in QUOTE_SERVERS.keys():
            shutil.copyfile('./quotes/0.ini', f'./quotes/{interaction.guild_id}.ini')
            await interaction.send("Quotes has been successfully setup. Please reload quotes to start using quotes bot.")

# Setup Cog into main bot
def setup(client):
    client.add_cog(Quotes(client))