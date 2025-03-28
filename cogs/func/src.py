import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import srcomapi
import srcomapi.datatypes as dt

api = srcomapi.SpeedrunCom()

class SRC(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @nextcord.slash_command(description="Validates a runner to MMG on SRC")
    async def srcvalid(self, interaction: Interaction, user:str = SlashOption(required=True)):
        
        await interaction.response.defer()
        help(self.client.fetch_user(interaction.user.id))
        return

        games = api.search(dt.Game, {"name": "Multiple Mario Games"})
        runs_dict = {}
        for game in games:
            runs_dict[game] = game.categories
        # Loop cats
        for game, categories in runs_dict.items():
            for category in categories:
                runs_db = dt.Leaderboard(api, data=api.get(f"leaderboards/{game.id}/category/{category.id}?embed=variables")).runs
                


def setup(client):
    client.add_cog(SRC(client))