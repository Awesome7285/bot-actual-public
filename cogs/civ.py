import json
import nextcord
from nextcord.ext import commands, menus
from nextcord import Interaction, SlashOption
from random import sample
from re import sub as regex_sub
from bs4 import BeautifulSoup
import requests
from .func.page_menu import MyPageSource
from .func.funcs import squash_text

with open('./civ/players.json', encoding='utf-8') as player_file:
    PLAYER_DB = json.load(player_file)

with open('./civ/civs.json', encoding='utf-8') as civs_file:
    CIVS = json.load(civs_file)

with open('./civ/civ_mods.json', encoding='utf-8') as civs_file:
    CIV_MODS = json.load(civs_file)

with open('./civ/mod_ids.json', encoding='utf-8') as civs_file:
    MOD_IDS = json.load(civs_file)


# Create civ class
class Civ(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    # Ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Civ is online.")

    # Add player
    @nextcord.slash_command(description="Add yourself into the civ player database")
    async def civaddplayer(self, interaction: Interaction, 
                           pack0: bool = SlashOption(name=CIVS[0]['name'].replace(' ', '_')),
                           pack1: bool = SlashOption(name=CIVS[1]['name'].replace(' ', '_')),
                           pack2: bool = SlashOption(name=CIVS[2]['name'].replace(' ', '_')),
                           pack3: bool = SlashOption(name=CIVS[3]['name'].replace(' ', '_')),
                           pack4: bool = SlashOption(name=CIVS[4]['name'].replace(' ', '_')),
                           pack5: bool = SlashOption(name=CIVS[5]['name'].replace(' ', '_')),
                           pack6: bool = SlashOption(name=CIVS[6]['name'].replace(' ', '_')),
                           pack7: bool = SlashOption(name=CIVS[7]['name'].replace(' ', '_')),
                           pack8: bool = SlashOption(name=CIVS[8]['name'].replace(' ', '_')),
                           pack9: bool = SlashOption(name=CIVS[9]['name'].replace(' ', '_')),
                           pack10: bool = SlashOption(name=CIVS[10]['name'].replace(' ', '_')),
                           pack11: bool = SlashOption(name=CIVS[11]['name'].replace(' ', '_')),
                           pack12: bool = SlashOption(name=CIVS[12]['name'].replace(' ', '_')),
                           pack13: bool = SlashOption(name=CIVS[13]['name'].replace(' ', '_')),
                           pack14: bool = SlashOption(name=CIVS[14]['name'].replace(' ', '_')),
                           pack15: bool = SlashOption(name=CIVS[15]['name'].replace(' ', '_')),
                           pack16: bool = SlashOption(name=CIVS[16]['name'].replace(' ', '_')),
                           pack17: bool = SlashOption(name=CIVS[17]['name'].replace(' ', '_')),
                           user: nextcord.User = SlashOption(required=False, default=None)
                           ):
        # The Funny List
        packs = [pack0, pack1, pack2, pack3, pack4, pack5, pack6, pack7, pack8, pack9, pack10, pack11, pack12, pack13, pack14, pack15, pack16, pack17]
        
        # Mod Check
        if user:
            if interaction.user.id != user and interaction.user.id != 244616599443603456:
                await interaction.send("You may not change the owned packs of another user.", delete_after=5)
                return
        else:    
            user = interaction.user
        
        PLAYER_DB[str(user.id)] = [int(owned) for owned in packs]

        with open('./civ/players.json', 'w', encoding='utf=8') as player_file:
            json.dump(PLAYER_DB, player_file, indent='\t')

        await interaction.send("Added " + user.mention + ":\n" +
                               '\n'.join([CIVS[pack]['name'] + ': ' + str(owned) for (pack, owned) in enumerate(packs)]))

    def get_available_civs(self, player, mods, unplayed_only):
        # Check player exists
        try:
            player_data = PLAYER_DB[str(player.id)]
        except KeyError:
            return None

        possible_playables = []
        # Add Vanilla CIVS
        if mods == 'vanilla' or mods == 'everything':
            # Loop DLC Packs
            for pack_num, pack in enumerate(CIVS):
                # Check if Player matches Pack and Pack is not a mod (just the final item)
                if player_data[pack_num] == 1 and pack["mod"] == False:
                    # Loop leaders in DLC Pack
                    for leader in pack["civs"]:
                        # Add leader to possibles
                        c = {"leader": leader[0], "civ": leader[-1]}
                        if len(leader) == 3:
                            c["persona"] = leader[1]

                        possible_playables.append(c)
        
        # Add Vanilla + Monkey CIVS
        if mods == 'vanilla + monkey boys':
            # Loop DLC Packs
            for pack_num, pack in enumerate(CIVS):
                # Check if Player matches Pack
                if player_data[pack_num] == 1:
                    # Loop leaders in DLC Pack
                    for leader in pack["civs"]:
                        # Add leader to possibles
                        c = {"leader": leader[0], "civ": leader[-1]}
                        if len(leader) == 3:
                            c["persona"] = leader[1]

                        possible_playables.append(c)

        # Add Mods
        if mods == 'everything' or mods == 'mods only':
            # Loop leaders in Mods
            for leader in CIV_MODS["mods"]:
                # Add leader to possibles
                c = {"leader": leader[0], "civ": leader[1], "modid": leader[2]}

                # Only get unplayed leaders
                if (unplayed_only == 'unplayed only') and (leader[0] not in [l[0] for l in CIV_MODS["plays"]]):
                    possible_playables.append(c)
                # Only get played leaders
                elif (unplayed_only == 'played only') and (leader[0] in [l[0] for l in CIV_MODS["plays"]]):
                    possible_playables.append(c)
                # No restrictions
                elif unplayed_only == 'any':
                    possible_playables.append(c)

        return possible_playables

    def choices_to_text(self, playable_choices):
        # Convert choice to text to add to output
        choice_text = []
        for choice in playable_choices:
            if 'persona' in choice.keys():
                choice_text.append(f"{choice['leader']} ({choice['persona']}) ({choice['civ']})")
            else:
                choice_text.append(f"{choice['leader']} ({choice['civ']})")
            if 'modid' in choice.keys():
                choice_text[-1] = f"[{choice_text[-1]}](<https://steamcommunity.com/sharedfiles/filedetails/?id={choice['modid']}>)"
        return choice_text

    # create game
    @nextcord.slash_command(description="Create a CIV 6 game with specified members *YOU DON'T NEED TO ADD YOURSELF*")
    async def civcreategame(self, interaction: Interaction, 
                            player2: nextcord.User = SlashOption(required=False),
                            player3: nextcord.User = SlashOption(required=False),
                            player4: nextcord.User = SlashOption(required=False),
                            player5: nextcord.User = SlashOption(required=False),
                            player6: nextcord.User = SlashOption(required=False),
                            player7: nextcord.User = SlashOption(required=False),
                            player8: nextcord.User = SlashOption(required=False),
                            mods: str = SlashOption(required=False, default='vanilla + monkey boys', choices=['vanilla', 'vanilla + monkey boys', 'everything', 'mods only']),
                            allow_dupe_civs: bool = SlashOption(required=False, default=False),
                            allow_dupe_leaders: bool = SlashOption(required=False, default=False),
                            civs_per_player: int = SlashOption(required=False, default=3),
                            unplayed_only: str = SlashOption(required=False, default='any', choices=['unplayed only', 'played only', 'any'])
                            ):
    
        players = [interaction.user, player2, player3, player4, player5, player6, player7, player8]

        used_civs = []
        used_leaders = []
        enabled_mod_ids = []

        output = ''

        # Loop Players
        for player in [player for player in players if player != None]:

            # Get possible playables
            possible_playables = self.get_available_civs(player, mods, unplayed_only)

            # Check player exists
            if possible_playables == None:
                await interaction.send(f"Player {player.mention} has not set up their owned DLCs yet!")
                return
            
            # Remove duplicate leaders if option checked
            if not allow_dupe_leaders:
                # Create new list of possible leaders (untaken)
                possible_leaders = [civ['leader'] for civ in possible_playables if civ['leader'] not in used_leaders]
                updated_possible_playables = []

                # Add to new possibles if leader is in the possible leaders
                for playable in possible_playables:
                    if playable['leader'] in possible_leaders:
                        updated_possible_playables.append(playable)

                # Re assign the playables
                possible_playables = updated_possible_playables

            # Remove duplicate civs if option checked
            if not allow_dupe_civs:
                # Create new list of possible civs (untaken)
                possible_civs = [civ['civ'] for civ in possible_playables if civ['civ'] not in used_civs]
                updated_possible_playables = []

                # Add to new possibles if civ is in the possible civs
                for playable in possible_playables:
                    if playable['civ'] in possible_civs:
                        updated_possible_playables.append(playable)

                # Re assign the playables
                possible_playables = updated_possible_playables
                             
            # Randomize the player's Civ Options
            try:
                playable_choices = sample(possible_playables, k=civs_per_player)
            except ValueError:
                await interaction.send("An error occurred. There are not enough available civs to fulfill this game setup. Try lowering the `civs per player` or allow duplicate civs/leaders.", delete_after=5)
                return

            # Get mod IDs
            enabled_mod_ids += [choice['modid'] for choice in playable_choices if 'modid' in choice.keys()]

            # Get text to output
            output += player.mention + ' ' + ', '.join(self.choices_to_text(playable_choices)) + '\n'

            # Add playables civs to the used list so they won't get picked again
            if not allow_dupe_civs:
                for playable in playable_choices:
                    used_civs.append(playable['civ'])
            
            # Add playables leaders to the used list so they won't get picked again
            if not allow_dupe_leaders:
                for playable in playable_choices:
                    used_leaders.append(playable['leader'])
        
        # Send main text body
        [await interaction.send(o) for o in squash_text(output, '\n')]

        # Skip next part if playing vanilla
        if mods == 'vanilla + monkey boys' or mods == 'vanilla':
            return

        # Create Filter
        with open("./civ/CustomFilters.xml", 'w+', encoding='utf-8') as file:
            file.write(self.create_filter_xml(enabled_mod_ids))

        await interaction.send("HOST ONLY: Send this file to \Steam\steamapps\workshop\content\\289070\\1601259406", file=nextcord.File("./civ/CustomFilters.xml"))
        
            
    def create_filter_xml(self, enabled_mod_ids):

        # Delete duplicates
        enabled_mod_ids = list(dict.fromkeys(enabled_mod_ids))

        text = """<?xml version="1.0" encoding="utf-8"?>

<GameData>
    <LocalizedText>
        <Row Tag="LOC_FF16_NUMOF_CUSTOM_FILTERS" Language="en_US">
            <Text>1</Text> 
        </Row>

        <Row Tag="LOC_FF16_CUSTOM_FILTER_1" Language="en_US">
            <Text>GENERATED FILTER;
            c6477d9f-6bad-4d24-9e76-49cda4f0a966, -- Better Builder Charges Tracking,
            13E8BCDF-98EC-4C03-3641-72D519B0047C, -- Better City States (UI),
            07D5DFAB-44CE-8F63-8344-93E427E9376E, -- Better Espionage Screen (UI),
            8d4fa23a-ef43-440c-8422-2bec11f8f5d7, -- Better Trade Screen,
            4ecfcc62-5471-4435-b295-590df213e8d8, -- Detailed Map Tacks,
            47dccacd-f1d0-4f25-bb02-deb2b528c833, -- Enhanced Mod Manager,
            1b4953d4-423c-11e9-b210-d663bd873d93, -- Gift It To Me,
            bcdbbbea-984f-474c-b921-6ea0be143600, -- Great Works [COLOR_Culture]Viewer[ENDCOLOR],
            fba4a935-06f0-414b-973d-5ffcd80c6d0e, -- Happiness and Growth Indicators,
            39da9e0f-c9ed-46e6-9aa9-842223b5da60, -- [COLOR:OperationChance_Green]Hillier Hills[ENDCOLOR],
            35f33319-ad93-4d6b-bf27-406fac382d06, -- More Lenses,
            619ac86e-d99d-4bf3-b8f0-8c5b8c402176, -- Multiplayer Helper 1.6.7,
            d3375ed7-abb2-4480-be4c-33e61161b6d3, -- Sukritact's Global Relations Panel,
            805cc499-c534-4e0a-bdce-32fb3c53ba38, -- Sukritact's Simple UI Adjustments,
            847dc17e-2042-4f28-a2dd-5a4b18625a71, -- Sukritact's Tourism Overview Screen,
            c8f09ba6-b9e9-4a37-b91e-b692831d4871, -- CTC - [ICON_WHISPER] Computer Translated Civilizations,
            4cf0475d-a85f-4984-ad55-8acb75afcba3, -- Mod Leaders Only,
"""
        
        for mod in enabled_mod_ids:
            text += f"            {MOD_IDS[str(mod)][0]}, -- {MOD_IDS[str(mod)][1]},\n"
        
        text += """		    </Text>
	    </Row>
    </LocalizedText>
</GameData>"""

        return text
        # c88cba8b-8311-4d35-90c3-51a4a5d66542, -- Better Balanced Map 1.00,

    # civ roll (declan) (5)
    @nextcord.slash_command(description="Roll an amount of random CIV 6 leaders for a user")
    async def civrandom(self, interaction: Interaction, 
                        player:nextcord.Member = SlashOption(), 
                        civs:int = SlashOption(default=3, required=False), 
                        mods: str = SlashOption(required=False, default='vanilla + monkey boys', choices=['vanilla', 'vanilla + monkey boys', 'everything', 'mods only']),
                        unplayed_only: str = SlashOption(required=False, default='any', choices=['unplayed only', 'played only', 'any'])
                        ):
        
        # Get possible playables
        possible_playables = self.get_available_civs(player, mods, unplayed_only)

        # Check player exists
        if possible_playables == None:
            await interaction.send(f"Player {player.mention} has not set up their owned DLCs yet!")
            return
        
        # Randomize the player's Civ Options
        playable_choices = sample(possible_playables, k=civs)

        # Send back to user
        output = player.mention + '\n' + '\n'.join(self.choices_to_text(playable_choices))
        [await interaction.send(o) for o in squash_text(output, '\n')]

    @nextcord.slash_command(description="Lists all mods currently on the randomizer")
    async def civlistmods(self, interaction: Interaction, show_banned:int = SlashOption(default=False, required=False, choices=[True, False])):

        # Get the list and add to dicts
        if not show_banned:
            header = "Mod List: [(Steam Collection)](<https://steamcommunity.com/sharedfiles/filedetails/?id=3387086764>)"
            data = []
            for mod in CIV_MODS["mods"]:
                data.append(f"[{mod[0]} ({mod[1]})](<https://steamcommunity.com/sharedfiles/filedetails/?id={mod[2]}>)")
        else:
            header = "Banned List: "
            data = []
            for mod in CIV_MODS["banned"]:
                data.append(f"[{mod[0]} ({mod[1]})](<https://steamcommunity.com/sharedfiles/filedetails/?id={mod[2]}>) Reason: {mod[3]}")
        
        pages = menus.ButtonMenuPages(source=MyPageSource(data, per_page=10, header=header))
        await pages.start(interaction=interaction)

    @nextcord.slash_command(description="Search for a mod in the mod list")
    async def civsearchmod(self, interaction: Interaction, id_text: str = SlashOption(name="search", description="Enter a Steam ID, Steam URL, Leader Name or Civilization Name to search")):
        
        await interaction.response.defer()

        # Data validation
        if 'steamcommunity.com/sharedfiles/filedetails' in id_text:
            id_text = id_text[id_text.find('=')+1:]
        
        if len(id_text) < 3:
            await interaction.send("Search text cannot be less than 3 characters.", delete_after=5)
            return

        ids = []
        data = []

        # SEARCH VIA ID
        if id_text.isdigit():
            ids.append(int(id_text))

        # SEARCH VIA TEXT
        else:
            for leader in CIV_MODS['mods'] + CIV_MODS['banned']:
                if id_text.lower() in leader[0].lower() or id_text.lower() in leader[1].lower():
                    if leader[2] not in ids:
                        ids.append(leader[2])

        if ids == []:
            await interaction.send("Search text did not match anything in the Mod List.", delete_after=5)
            return
        
        for id in ids:
            # Create Data Structure
            output = {
                "id": 0,
                "name": "",
                "ingameid": "",
                "civs": {},
                "colour": 0,
                "plays": 0
            }

            # Get things with the ID
            output["id"] = id

            # Get positions in the list of leaders from the mod
            modlist_hits = [n for n, l in enumerate(CIV_MODS['mods']) if l[2] == id]
            banlist_hits = [n for n, l in enumerate(CIV_MODS['banned']) if l[2] == id]
            
            # Civs
            for leader in modlist_hits:
                civ = CIV_MODS['mods'][leader][1]
                lead = CIV_MODS['mods'][leader][0]
                output['colour'] |= 0x00ff00
                if civ not in output["civs"]:
                    # Add Civilization name and leader name
                    output["civs"][civ] = [(lead, None)]
                else:
                    # Add Leader name to existing Civilization name
                    output["civs"][civ].append((lead, None))

            # Banned
            for leader in banlist_hits:
                civ = CIV_MODS['banned'][leader][1]
                lead = CIV_MODS['banned'][leader][0]
                reason = CIV_MODS['banned'][leader][3]
                output['colour'] |= 0xff0000
                if civ not in output["civs"]:
                    # Add Civilization name and leader name
                    output["civs"][civ] = [(lead, reason)]
                else:
                    # Add Leader name to existing Civilization name
                    output["civs"][civ].append((lead, reason))

            # Name
            try:
                id_info = MOD_IDS[str(id)]
                output["ingameid"] = id_info[0]
                output["name"] = regex_sub(r"\[.*?\]", "", id_info[1])
            except KeyError:
                output["ingameid"] = None
                output["name"] = "Name Unknown"

            # Plays
            for civ in output['civs']:
                for leader in output['civs'][civ]:
                    if [leader, civ, id] in CIV_MODS["plays"]:
                        output["plays"] += 1
            
            # Could not find ID
            if output['civs'] == {}:
                await interaction.send("ID was not found in Mod List", delete_after=5)
                return

                
            # Format Output
            embed = nextcord.Embed(title=f"{output['name']}", color=output['colour'])
            embed.add_field(name="Steam ID", value=output['id'])
            embed.add_field(name="In-game ID", value=output['ingameid'])
            embed.add_field(name="Plays", value=output['plays'])

            for civ in output['civs']:
                good_civs = []
                for leader in output['civs'][civ]:
                    if leader[1] == None:
                        good_civs.append(leader[0])
                    else:
                        good_civs.append(leader[0] + " (BANNED) Reason: " + leader[1])
                embed.add_field(name="CIV: "+civ, value='\n'.join(good_civs), inline=False)

            # Request the workshop item's thumbnail
            img = BeautifulSoup(requests.get(f"https://steamcommunity.com/sharedfiles/filedetails/?id={output['id']}").content, 'html.parser').find("link", attrs={"rel": "image_src"})['href']

            embed.set_thumbnail(img)
            embed.url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={output['id']}"

            data.append(embed)

        pages = menus.ButtonMenuPages(source=MyPageSource(data, per_page=1))
        await pages.start(interaction=interaction)

        #await interaction.send(embed=embed)


def setup(client):
    client.add_cog(Civ(client))