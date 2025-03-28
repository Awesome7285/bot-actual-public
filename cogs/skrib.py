#TODO
# full list, parameters
# FIND PREVIOUS DRAWINGS FROM FOLDER

import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import random
from configparser import ConfigParser
from .func.funcs import squash_text

class Skrib(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    # Ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Skrib is online.")
    
    # Test
    # @nextcord.slash_command(description="Pings the skrib bot")
    # async def skrib_ping(self, interaction: Interaction):
    #     await interaction.response.send_message("Skrib is online.")

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
    @nextcord.slash_command(description="Gets random words from the skrib list")
    async def skribwords(self, interaction: Interaction, 
                         num: int = SlashOption(required=False, default=200, name='words'),
                         name: str = SlashOption(required=False),
                         search: str = SlashOption(required=False)):

        # Open wordlist for the server
        try:
            wordlist = open(f'./skrib/{interaction.guild_id}.txt').read().split('\n')[1:-1]
        except FileNotFoundError:
            self.create_new_file(interaction.guild_id)
            await interaction.send("This server has no word list. A new file has just been created.")
            return
        if len(wordlist) < 2:
            await interaction.send("Not enough words in the list yet. Create some new words with /addword")
            return
        # Adjust wordlist
        if name:
            if name.startswith('<'):
                name_id = name[2:-1] # Cut off the <@>
            else:
                try:
                    user_fetch = ConfigParser() #Configparser
                    user_fetch.read('./skrib/namematch.ini', encoding='utf-8')
                    name_user_match = {name.lower(): id for id, name in user_fetch[str(interaction.guild_id)].items()}
                    name_id = name_user_match[name.lower()]
                except KeyError:
                    await interaction.send("There are no words in the wordlist under this name.")
                    return
            wordlist = [word for word in wordlist if word.split(', ')[1] == name_id]

        # Adjust Wordlist for search
        if search:
            if len(search) < 3:
                await interaction.send("Search text cannot be less than 3 characters.", delete_after=5)
                return
            wordlist = [word for word in wordlist if search in word.split(', ')[0].lower()]
        
        # All words
        if num == 0 or search:
            words = range(len(wordlist))
        else:
            # Randomize a numbered list
            try:
                words = random.sample(range(len(wordlist)), num)
            except ValueError:
                await interaction.send(f"Invalid Word Quantity. There are {len(wordlist)} words in this list.")
                return
        # Get Words from numbers
        send_list = []
        for word in words:
            send_list.append(wordlist[word].split(', ')[0])
        
        output = ', '.join(send_list)
        if search:
            output += "\n\nResults: " + str(len(wordlist))
        [await interaction.send('```\n'+msg+'\n```') for msg in squash_text(output, ' ')]
        #await interaction.send(f"```\n{', '.join(send_list)}\n```")

    # Add Word
    @nextcord.slash_command(description="Adds a word to the current wordlist")
    async def addword(self, interaction: Interaction, word: str):
        try:
            current_list = open(f'./skrib/{interaction.guild_id}.txt').readline()
        except FileNotFoundError:
            self.create_new_file(interaction.guild_id)
            await interaction.send("This server has no word list. A new file has just been created.")
            current_list = 'CURRENT=DOC1\n'
        wordlist = open(f'./skrib/{interaction.guild_id}.txt', 'a')
        wordlist.write(f'{word}, {interaction.user.id}, {current_list[8:]}')
        wordlist.close()
        # Add User to match list
        user_fetch = ConfigParser() #Configparser
        user_fetch.read('./skrib/namematch.ini', encoding='utf-8')
        if str(interaction.user.id) not in user_fetch[str(interaction.guild_id)].keys(): # If user isnt in list
            if interaction.user.nick != None: # Set to nickname
                user_fetch[str(interaction.guild_id)][str(interaction.user.id)] = interaction.user.nick
            else:
                user_fetch[str(interaction.guild_id)][str(interaction.user.id)] = interaction.user.name
            with open('./skrib/namematch.ini', 'w', encoding='utf-8') as configfile:
                user_fetch.write(configfile)
        # Confirm to discord
        await interaction.send(f'Added word! Word: {word}, Author: <@{interaction.user.id}>, DOC: {current_list[8:]}')
    
    # Change Wordlist
    @nextcord.slash_command(description="Changes/Shows the current skrib list name")
    async def changeskriblist(self, interaction: Interaction, _list: str = SlashOption(required=False, default='', name='list')):

        if _list == '':
            # Get and show current list
            current_list = open(f'./skrib/{interaction.guild_id}.txt', 'r').readline()
            await interaction.send(f'Current list is: "{current_list[8:-1]}"')
        else:
            # Read List from file
            file = open(f'./skrib/{interaction.guild_id}.txt', 'r').read()
            file = "CURRENT="+_list+file[file.find('\n'):]
            # Write full doc over file
            rewrite = open(f'./skrib/{interaction.guild_id}.txt', 'w')
            rewrite.write(file)
            rewrite.close()
            await interaction.send(f'Skribble list changed to: "{_list}"')

    @nextcord.slash_command(description="Gets the word data for a word in the server's skrib list")
    async def worddata(self, interaction: Interaction, word: str):

        # Server has file?
        try:
            wordlist = open(f'./skrib/{interaction.guild_id}.txt')
        except FileNotFoundError:
            await interaction.send("There is no skrib file for this server yet.")
            return
        # Go through each line in file
        for line in wordlist:
            data = line.split(', ')
            if word.lower() == data[0].lower():
                # Format Message
                user_fetch = ConfigParser() #Configparser
                user_fetch.read('./skrib/namematch.ini', encoding='utf-8')
                author = user_fetch[str(interaction.guild_id)][str(data[1])] # await client.fetch_user(int(data[1]))
                await interaction.send("```\nWord: "+data[0]+"\nAuthor: "+str(author)+"\nIn Doc: "+data[2]+"\n```")
                return
        await interaction.send("Not in the word list!")
    
    @nextcord.slash_command(description="Gets the names of users submitted to the skrib list")
    async def skribnames(self, interaction: Interaction):
        # Server has file?
        try:
            wordlist = open(f'./skrib/{interaction.guild_id}.txt')
        except FileNotFoundError:
            await interaction.send("There is no skrib file for this server yet.")
        # Do thing
        user_fetch = ConfigParser() #Configparser
        user_fetch.read('./skrib/namematch.ini', encoding='utf-8')
        names = []
        for line in wordlist:
            data = line.split(', ')
            if len(data) == 3:
                author = user_fetch[str(interaction.guild_id)][str(data[1])]
                if author not in names:
                    names.append(author)
        await interaction.send(', '.join(names))

# Setup Cog into main bot
def setup(client):
    client.add_cog(Skrib(client))