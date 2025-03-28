import discord
from discord.ext import commands
import os
import shutil
from configparser import ConfigParser
from random import randint
from .func.funcs import squash_text, IncorrectInputError

client = commands.Bot(command_prefix='~~')

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

    def __init__(self, client):
        self.client = client
    
    # Ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Quotes is online.")

    # Test
    @commands.command(aliases=['quotesping', 'quotescheck'])
    async def quotes_ping(self, ctx):
        """
        Pings back to the channel if quotes bot is online.
        """
        await ctx.send(f"Quotes is online")

    # Get Quote
    @commands.command(aliases=['getquote', 'q'])
    async def quote(self, ctx, q_num='None', context=None):
        
        """
        Gets a random quote, or quote with specified number.
        Use "context" after the number to show the quote's context as well. (Does not work for random quotes)
        """

        # No Quotes for server
        if ctx.guild.id not in QUOTE_SERVERS.keys():
            await ctx.send("Your server must enable quotes first. Use ~~setupquotes")
            return
        # Quote from number
        if q_num.isdigit():
            try:
                # Checks if quote is deleted, but also checks QUOTES[q_num] exists (i.e out of range)
                if QUOTE_SERVERS[ctx.guild.id]["QUOTES"][q_num]['quote'] == 'DEL':
                    raise KeyError
            except KeyError:
                await ctx.send("Invalid Quote Number")
                return
            quote_string = self.format_quote(q_num, ctx.guild.id, context)
            await ctx.send(quote_string)
        
        # Random Quote
        elif q_num == 'None':
            while QUOTE_SERVERS[ctx.guild.id]["QUOTES"][q_num]['quote'] == 'DEL' and q_num == 'None': 
                q_num = str(randint(1, QUOTE_SERVERS[ctx.guild.id]["TOTAL"]))
            quote_string = self.format_quote(q_num, ctx.guild.id, context)
            await ctx.send(quote_string)
    
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
    @commands.command(aliases=['quotenames', 'qname', 'qnames'])
    async def quotename(self, ctx, *names):

        """
        Gets a list of all names in the quote database.
        Include a name in the command to show all quotes from this person.
        """

        # First Quote for server
        if ctx.guild.id not in QUOTE_SERVERS.keys():
            await ctx.send("Your server must enable quotes first. Use ~~setupquotes")
            return
        # Combine names variable
        names = ' '.join(names)
        if names == '':
            [await ctx.send('```\n'+msg+'\n```') for msg in squash_text('\n'.join(QUOTE_SERVERS[ctx.guild.id]["NAMES"]))]
        else:
            if names.lower() in [n.lower() for n in QUOTE_SERVERS[ctx.guild.id]["NAMES"]]:
                quote_msg= ''
                for quote in range(1, QUOTE_SERVERS[ctx.guild.id]["TOTAL"]): # Loop all quotes
                    if QUOTE_SERVERS[ctx.guild.id]["QUOTES"].has_option(str(quote), 'name'): # Checks if section exists, because some deleted quotes have no name
                        if names in QUOTE_SERVERS[ctx.guild.id]["QUOTES"][str(quote)]["name"].split(', '): # Check the name
                            quote_msg += self.format_quote(str(quote), ctx.guild.id, None)+'\n'
                [await ctx.send('```\n'+msg+'\n```') for msg in squash_text(quote_msg)]
            else:
                await ctx.send("No quotes by person with this name.")

    # Add Quote
    @commands.command(aliases=["addq"])
    async def addquote(self, ctx, *quote):
        """
        Adds a quote to the quote database.
        To add a quote, use this syntax:
        \"Quote\" - Name of Person, YYYY
        \"Quote 1\" - Name of Person 1, \"Quote 2\" - Name of Person 2, YYYY
        """
        global QUOTE_SERVERS
        quote = list(quote)
        # First Quote for server
        if ctx.guild.id not in QUOTE_SERVERS.keys():
            await ctx.send("Your server must enable quotes first. Use `~~setupquotes`")
            return
        try:
            # Message Loop
            new_quote = {"quote": [], "name": []}
            while len(quote) > 0:
                # Find quote part
                new_quote["quote"].append(f'"{quote[0]}"')
                quote.pop(0)
                if quote[0] != '-':
                    raise IncorrectInputError
                else:
                    quote.pop(0)
                # Find name part
                current_name = ''
                for name in range(len(quote)):
                    current_name += quote[name]+' '
                    if ',' in quote[name]:
                        quote = quote[name+1:]
                        new_quote["name"].append(current_name[:-2])
                        break
                else:
                    raise IncorrectInputError
                # Find year
                if len(quote) == 1:
                    new_quote["year"] = quote[0]
                    quote.pop(0)
                else:
                    continue
        # Input Error
        except (IncorrectInputError, IndexError):
            await ctx.send("An error occured. Check you have formatted your command correctly, use `~~help addquote` for more information.")
        # Add to quotes
        QUOTE_SERVERS[ctx.guild.id]["QUOTES"][str(QUOTE_SERVERS[ctx.guild.id]["TOTAL"]+1)] = {'quote': ',,'.join(new_quote['quote']),
                                       'name': ', '.join(new_quote['name']),
                                       'year': new_quote['year'],
                                       'list': '',
                                       'context': ''}
        with open(QUOTE_SERVERS[ctx.guild.id]["LOCATION"], 'w', encoding='utf-8') as configfile:
            QUOTE_SERVERS[ctx.guild.id]["QUOTES"].write(configfile)
        await ctx.send(f'Added Quote Entry #{str(QUOTE_SERVERS[ctx.guild.id]["TOTAL"]+1)}:\n{self.format_quote(str(QUOTE_SERVERS[ctx.guild.id]["TOTAL"]+1), ctx.guild.id, False)}')
        QUOTE_SERVERS[ctx.guild.id]["TOTAL"] += 1

    # Delete Quote
    @commands.command(aliases=['deletequote', 'deleteq', 'delq'])
    async def delquote(self, ctx, num):
        """
        Not Implemented.
        """
        pass
        #ctx.author.roles

    # Setup Quotes for new servers
    @commands.command(aliases=['quote_setup'])
    async def setupquotes(self, ctx):
        """
        Sets up the quotes bot for this server.
        """
        if ctx.guild.id not in QUOTE_SERVERS.keys():
            shutil.copyfile('./quotes/0.ini', f'./quotes/{ctx.guild.id}.ini')
            await ctx.send("Quotes has been successfully setup. Please reload quotes to start using quotes bot.")

# Setup Cog into main bot
def setup(client):
    client.add_cog(Quotes(client))