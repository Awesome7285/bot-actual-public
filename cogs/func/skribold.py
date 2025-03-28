#TODO
# full list, parameters
# FIND PREVIOUS DRAWINGS FROM FOLDER

import discord
from discord.ext import commands
import random
from configparser import ConfigParser

client = commands.Bot(command_prefix='~~')

class Skrib(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    # Ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Skrib is online.")
    
    # Test
    @commands.command(aliases=['skribping', 'skribcheck'])
    async def skrib_ping(self, ctx):
        """
        Pings back to the channel if skrib bot is online.
        """
        await ctx.send(f"Skrib is online")

    # Create a new file for server
    def create_new_file(self, guild_id):
        f = open(f'./skrib/{guild_id}.txt', 'a')
        f.write("CURRENT=DOC1\n")
        f.close()
        # Word Authors List
        user_fetch = ConfigParser() #Configparser
        user_fetch.read('./skrib/namematch.ini', encoding='utf-8')
        user_fetch.add_section(str(guild_id))
        with open('./skrib/namematch.ini', 'w', encoding='utf-8') as configfile:
            user_fetch.write(configfile)

    # Get Words
    @commands.command(aliases=['skrib'])
    async def get_words(self, ctx, num=200):
        """
        Gets an amount of randomized skrib words from the servers list.
        Num: Number of words to show, default = 200, 0 = all
        """
        # Open wordlist for the server
        try:
            wordlist = open(f'./skrib/{ctx.guild.id}.txt').read().split('\n')[1:]
        except FileNotFoundError:
            self.create_new_file(ctx.guild.id)
            await ctx.send("This server has no word list. A new file has just been created.")
        if len(wordlist) < 2:
            await ctx.send("Not enough words in the list yet. Create some new words with `~~addword`")
        # All words
        if num == 0:
            words = range(len(wordlist))
        else:
            # Randomize a numbered list
            try:
                words = random.sample(range(len(wordlist)), num)
            except ValueError:
                await ctx.send("Invalid Word Quantity.")
                return
        # Get Words from numbers
        send_list = []
        for word in words:
            send_list.append(wordlist[word].split(', ')[0])
        await ctx.send(f"```\n{', '.join(send_list)}\n```")

    # Add Word
    @commands.command(aliases=['addw'])
    async def addword(self, ctx, *word):
        """
        Adds a word to the current wordlist.
        """
        try:
            current_list = open(f'./skrib/{ctx.guild.id}.txt').readline()
        except FileNotFoundError:
            self.create_new_file(ctx.guild.id)
            await ctx.send("This server has no word list. A new file has just been created.")
            current_list = 'CURRENT=DOC1\n'
        wordlist = open(f'./skrib/{ctx.guild.id}.txt', 'a')
        wordlist.write(f'{" ".join(word)}, {ctx.author.id}, {current_list[8:]}')
        wordlist.close()
        # Add User to match list
        user_fetch = ConfigParser() #Configparser
        user_fetch.read('./skrib/namematch.ini', encoding='utf-8')
        if str(ctx.author.id) not in user_fetch[str(ctx.guild.id)].keys(): # If user isnt in list
            if ctx.author.nick != None: # Set to nickname
                user_fetch[str(ctx.guild.id)][str(ctx.author.id)] = ctx.author.nick
            else:
                user_fetch[str(ctx.guild.id)][str(ctx.author.id)] = ctx.author.name
            with open('./skrib/namematch.ini', 'w', encoding='utf-8') as configfile:
                user_fetch.write(configfile)
        # Confirm to discord
        await ctx.send(f'Added word! Word: {" ".join(word)}, Author: <@{ctx.author.id}>, DOC: {current_list[8:]}')
    
    # Change Wordlist
    @commands.command(aliases=['change_list', 'change_skrib_list', 'changelist'])
    async def changeskriblist(self, ctx, _list=''):
        """
        Changes the current skrib list name. Leave blank to display the current list
        """
        if _list == '':
            # Get and show current list
            current_list = open(f'./skrib/{ctx.guild.id}.txt', 'r').readline()
            await ctx.send(f'Current list is: "{current_list}"')
        else:
            # Read List from file
            file = open(f'./skrib/{ctx.guild.id}.txt', 'r').read()
            file = "CURRENT="+_list+file[file.find('\n'):]
            # Write full doc over file
            rewrite = open(f'./skrib/{ctx.guild.id}.txt', 'w')
            rewrite.write(file)
            rewrite.close()
            await ctx.send(f'Skribble list changed to: "{_list}"')

    @commands.command(aliases=['skribword', 'wd', 'word'])
    async def worddata(self, ctx, *word):
        """
        Gets the word data for a word in the server's skrib list.
        """
        # Server has file?
        try:
            wordlist = open(f'./skrib/{ctx.guild.id}.txt')
        except FileNotFoundError:
            await ctx.send("There is no skrib file for this server yet.")
        # Go through each line in file
        for line in wordlist:
            data = line.split(', ')
            if ' '.join(word).lower() == data[0].lower():
                # Format Message
                user_fetch = ConfigParser() #Configparser
                user_fetch.read('./skrib/namematch.ini', encoding='utf-8')
                author = user_fetch[str(ctx.guild.id)][str(data[1])] # await client.fetch_user(int(data[1]))
                await ctx.send("```\nWord: "+data[0]+"\nAuthor: "+str(author)+"\nIn Doc: "+data[2]+"\n```")
                return
        await ctx.send("Not in the word list!")
    
    @commands.command()
    async def skribnames(self, ctx):
        """
        Gets all names in server's list.
        """
        # Server has file?
        try:
            wordlist = open(f'./skrib/{ctx.guild.id}.txt')
        except FileNotFoundError:
            await ctx.send("There is no skrib file for this server yet.")
        # Do thing
        names = []
        for line in wordlist:
            data = line.split(', ')
            if len(data) == 3:
                if data[1] not in names:
                    names.append(data[1])
        await ctx.send(names)

# Setup Cog into main bot
def setup(client):
    client.add_cog(Skrib(client))