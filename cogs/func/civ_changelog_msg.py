import json


leaders = [

]
now_banned = [
    
]
bans = [

]

def create_changelog_message():
    

    output = "# Added Leaders\n\n"

    for leader in leaders:
        output += f"[{leader[0]} ({leader[1]})](<https://steamcommunity.com/sharedfiles/filedetails/?id={leader[2]}>)\n"

    output += "\n# Now Banned\n\n"

    for leader in now_banned:
        output += f"[{leader[0]} ({leader[1]})](<https://steamcommunity.com/sharedfiles/filedetails/?id={leader[2]}>) Reason: {leader[3]}\n"

    output += "\n# Added Bans\n\n"

    for leader in bans:
        output += f"[{leader[0]} ({leader[1]})](<https://steamcommunity.com/sharedfiles/filedetails/?id={leader[2]}>) Reason: {leader[3]}\n"

    return output

def create_filter_xml(enabled_mod_ids):
        
        with open('./civ/mod_ids.json', encoding='utf=8') as civs_file:
            MOD_IDS = json.load(civs_file)

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
            47dccacd-f1d0-4f25-bb02-deb2b528c833, -- Enhanced Mod Manager,
            619ac86e-d99d-4bf3-b8f0-8c5b8c402176, -- Multiplayer Helper 1.6.7,
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

with open('civ_changelog.txt', 'w+', encoding='utf-8') as f:
    f.write(create_changelog_message())

# with open('CustomFilters.xml', 'w+', encoding='utf-8') as f:
#     f.write(create_filter_xml([l[2] for l in leaders]))
