import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
from random import choice

# Create matches class
class Chaos(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @nextcord.slash_command(description="Roll in chaos pool")
    async def chaospool(self, interaction: Interaction):

        # Open File
        with open('./chaos/chaos_pool.txt') as file:
            rules = file.read().split('\n')
            rule = choice(rules)
            await interaction.send(rule)
    
    @nextcord.slash_command(description="Roll in chaos chess")
    async def chaoschess(self, interaction: Interaction):

        # Open File
        with open('./chaos/chaos_chess.txt') as file:
            rules = file.read().split('\n')
            rule = choice(rules)
            await interaction.send(rule)


def setup(client):
    client.add_cog(Chaos(client))