import requests
from datetime import datetime
from rotfDatabase import RotfDatabase as RDB
import socket
import requests.packages.urllib3.util.connection as urllib3_cn
import json
from quickchart import QuickChart, QuickChartFunction

'''
Used to force IPV4 as IPV6 has issues right now requests defaults to ipv6 causing LARGE time delays in requests
'''


def allowed_gai_family():
    """
     https://github.com/shazow/urllib3/blob/master/urllib3/util/connection.py
    """
    family = socket.AF_INET
    return family


urllib3_cn.allowed_gai_family = allowed_gai_family

'''
Creates request to api for market Data
Not in-game yet.

'''


def get_market() -> dict:
    data = requests.get("https://playbtn.com/api/market/listings").json()

    return {"WIP": "WIP"}


'''
Cleans a characters inventory
Currently there are ID's in place for the items and no list yet.
-1 = empty slot

Returns a Dict.
    equipped: The items equipped on your character
    inventory: the items in the player's inventory (temporary?)
'''


def clean_items(inv: dict) -> dict:
    # Inventory length currently capped at 12 (No Backpacks, Equips still 4 (weapon,armor,ability,jewelry)
    equipped = 3
    count = 0
    charEquips = {}
    charInventory = {}
    dump = []
    ITEM_DICT = "C:/Users/19787/PycharmProjects/rotfDiscord/rotfAPI/dict.json"
    with open(ITEM_DICT) as f:
        data = json.load(f)

        for i in inv['items']:
            # Filler IDK what data they will add.
            item = i['itemType']
            if count <= equipped:
                charEquips.update({data[str(item)]: str(count)})
                dump.append(data[str(item)])
                count += 1
            else:
                if data[str(item)] not in charInventory.keys():
                    charInventory.update({data[str(item)]: 1})
                    dump.append(data[str(item)])
                else:
                    charInventory[data[str(item)]] += 1
                    dump.append(data[str(item)])


        return {"equipped": charEquips, "inventory": charInventory, "dump": dump}


'''
Use: Cleans up each character in the character Dict given by  the API
Gets you the stats, class, skin and items for each Char.

Params: playerCharacter Data from the Request to API.

returns: a Dict.
    INT class: The class ID (convert to name & sprite when we known)
    INT skin: The skin ID being used by that class (Convert to name or sprite when known)
    DICT stats: A Dict of the stats for the character (Final stats undetermined so max is unknown).
    DICT items: A Dict of the items the player has "equipped" and in their "inventory".
'''


def get_stats(charData: dict, classID: str) -> dict:
    MAXSTATS = {"Hunter": {'maxHP': 700, 'maxMP': 252, 'attack': 75, 'defense': 25, 'speed': 50,
                           'vitality': 40, 'wisdom': 50, 'dexterity': 50, 'haste': 300},
                "Cleric": {'maxHP': 670, 'maxMP': 385, 'attack': 60, 'defense': 25, 'speed': 55,
                           'vitality': 40, 'wisdom': 75, 'dexterity': 60, 'haste': 300},
                "Warrior": {'maxHP': 855, 'maxMP': 252, 'attack': 55, 'defense': 30, 'speed': 50,
                            'vitality': 60, 'wisdom': 50, 'dexterity': 65, 'haste': 300},
                "Wizard": {'maxHP': 670, 'maxMP': 385, 'attack': 75, 'defense': 25, 'speed': 50,
                           'vitality': 40, 'wisdom': 60, 'dexterity': 75, 'haste': 300},
                "PH": {'maxHP': 670, 'maxMP': 385, 'attack': 75, 'defense': 25, 'speed': 50,
                       'vitality': 40, 'wisdom': 60, 'dexterity': 75, 'haste': 300}}

    CLMAX = MAXSTATS[classID]
    stats = {}
    current = 0
    for stat in CLMAX:
        if charData[stat] == CLMAX[stat]:
            stats.update({stat: "MAX"})
            current += 1
        else:
            stats.update({stat: str(charData[stat]) + "/" + str(CLMAX[stat])})

    stats.update({"statsMaxed": str(current) + "/9"})
    return stats


'''
Returns the unique characters an account has
'''


def get_characters(account: dict) -> list:
    characters = []
    classNames = {2: "Hunter", 3: "Cleric",
                  0: "Wizard", 1: "Warrior",
                  4: "PH", 5: "PH",
                  6: "PH", 7: "PH"}
    for char in account:
        className = classNames[char['classType']]
        skinType = char['skinType']
        stats = get_stats(char, className)
        items = clean_items(char['inventory'])
        fame = char['fame']
        characters.append({"class": className, "skin": skinType, "stats": stats, "items": items, 'fame': fame})

    return characters


'''
Create api request for the account specified by Name
Returns UID: UserID
        playerName: The name tied to the account
        playerFame: Total fame the player has
        playerCharacters: List of Dict of characters for the account
        dateTime: The current time of this request
'''


def get_account(name: str) -> dict or str:
    isOutdated = RDB.check_character_last_update(name)

    if isOutdated:
        try:
            data = requests.get("https://playbtn.com/api/account/info/by-name/" + name).json()
        except ValueError:
            return "The name does not exist. Or the API is down."

        UID = data['id']
        playerName = data['name']
        playerFame = data['fame']
        playerChars = get_characters(data['characters'])
        rating = RDB.get_rating(playerName)
        total_deaths = RDB.get_player_deaths(playerName)
        # Make Dictionary of the account data
        if rating == "Character Undiscovered":
            accountData = {"UID": UID, "playerName": playerName, "playerFame": playerFame,
                           "playerCharacters": playerChars, "dateTime": datetime.now(),
                           "rating": 0, "total_deaths": total_deaths}
        else:
            accountData = {"UID": UID, "playerName": playerName, "playerFame": playerFame,
                           "playerCharacters": playerChars, "dateTime": datetime.now(),
                           "rating": rating, "total_deaths": total_deaths}

        # Update the account data in MongoDB
        if isOutdated == "New":
            RDB.insert_character_data(accountData)
        else:
            RDB.update_character_data(accountData)

        return accountData


'''
Updates a users rating, will be used later to help find matching/similar users.
'''


def update_rating(name: str, rating: int) -> int or str:
    # Determine username viability (Is the name real?)
    try:
        requests.get("https://playbtn.com/api/account/info/by-name/" + name).json()
    except ValueError:
        return "The name does not exist. Or the API is down."

    existing_char = RDB.get_rating(name)

    if type(existing_char) == int:

        # Determine rating viability (Is the rating legit?)
        if type(rating) is int or type(rating) is float:
            if rating <= 0:
                RDB.update_character_rating(name, int(0))
                return name + " Rating has been updated"
            elif rating >= 5:
                RDB.update_character_rating(name, int(5))
                return name + " Rating has been updated"
            else:
                RDB.update_character_rating(name, int(rating))
                return name + " Rating has been updated"
        else:
            return "This rating is invalid."
    else:
        return existing_char


def get_chart(req):
    if req == "deaths":
        death_counts = RDB.get_monster_counts()
        monsters = []
        kills = []
        count = 0
        for k in death_counts:
            if count <= 9:
                if k['_id'] != "mike":
                    monsters.append(k['_id'])
                    kills.append(k['Kills'])
                    count += 1
            else:
                break

        qc = QuickChart()
        qc.width = 500
        qc.height = 300
        qc.device_pixel_ratio = 2.0
        qc.config = {
            "type": "bar",
            "data": {
                "labels": monsters,
                "datasets": [{
                    "label": "Monster Kills",
                    "data": kills,
                    "backgroundColor": ['#996600', '#b37700', '#cc8800', '#e69900', '#ffaa00',
                                        '#ffb31a', '#ffbb33', '#ffc34d', '#ffcc66', '#ffd480']

                }]
            }
        }

        return qc.get_short_url()

    elif req == "loots":
        loot_counts = RDB.get_item_counts()
        name = []
        dropped = []
        count = 0
        for k in loot_counts:
            if count <= 9:
                if k['_id'] != "mike":

                    name.append(k['_id'])
                    dropped.append(k['Dropped'])
                    count += 1
            else:
                break

        qc = QuickChart()
        qc.width = 500
        qc.height = 300
        qc.device_pixel_ratio = 2.0
        qc.config = {
            "type": "bar",
            "data": {
                "labels": name,
                "datasets": [{
                    "label": "Loots Dropped",
                    "data": dropped,
                    "backgroundColor": ['#996600', '#b37700', '#cc8800', '#e69900', '#ffaa00',
                                        '#ffb31a', '#ffbb33', '#ffc34d', '#ffcc66', '#ffd480']

                }]
            }
        }

        return qc.get_short_url()

    elif req == "players":
        player_counts = RDB.get_player_deaths()
        name = []
        count = []
        for k in player_counts:
            if k['_id'] != "mike":
                name.append(k['_id'])
                count.append(k['Deaths'])

        qc = QuickChart()
        qc.width = 500
        qc.height = 300
        qc.device_pixel_ratio = 2.0
        qc.config = {
            "type": "violin",
            "data": {
                "labels": name,
                "datasets": [{
                    "label": "Player Deaths",
                    "data": count

                }]
            }
        }
        return qc.get_short_url()

    elif req == "ratio_flat":
        death_counts = RDB.get_monster_counts()
        loot_counts = list(RDB.get_item_rank_counts())
        total_deaths = 0
        for k in death_counts:
            total_deaths += k['Kills']

        total_legendaries = loot_counts[0]['Dropped']
        total_primals = loot_counts[1]['Dropped']

        tot = total_deaths + total_primals + total_legendaries

        lege_perc = round(total_legendaries / tot * 100)
        primal_perc = round(total_primals / tot * 100)
        death_perc = round(total_deaths / tot * 100)

        qc = QuickChart()
        qc.width = 500
        qc.height = 300
        qc.device_pixel_ratio = 2.0
        qc.config = {
            "type": "pie",
            "data": {
                "labels": ["Legendaries", "Primals", "Deaths"],
                "datasets": [{
                    "label": "Game Ratios",
                    "data": [total_legendaries, total_primals, total_deaths],
                    "backgroundColor": ['rgb(54, 162, 235)', 'rgb(255, 159, 64)', 'rgb(255, 99, 132)'],

                }]
            },
            "options": {
                    "title": {
                      "display": True,
                      "text": 'Current BTN Loot & Death Ratios'
                    },  "plugins": {
                      "datalabels": {
                        "display": True,
                        "font": {
                          "size": 15,
                          "color": "#000"
                        }
                                    }
                            }
            }
        }
        return qc.get_short_url()
    elif req == "ratio_perc":
        death_counts = RDB.get_monster_counts()
        loot_counts = list(RDB.get_item_rank_counts())
        total_deaths = 0
        for k in death_counts:
            total_deaths += k['Kills']

        total_legendaries = loot_counts[0]['Dropped']
        total_primals = loot_counts[1]['Dropped']

        tot = total_deaths + total_primals + total_legendaries

        lege_perc = round(total_legendaries / tot * 100)
        primal_perc = round(total_primals / tot * 100)
        death_perc = round(total_deaths / tot * 100)

        qc = QuickChart()
        qc.width = 500
        qc.height = 300
        qc.device_pixel_ratio = 2.0
        qc.config = {
            "type": "pie",
            "data": {
                "labels": ["Legendaries", "Primals", "Deaths"],
                "datasets": [{
                    "label": "Game Ratios",
                    "data": [lege_perc, primal_perc, death_perc],
                    "backgroundColor": ['rgb(54, 162, 235)', 'rgb(255, 159, 64)', 'rgb(255, 99, 132)'],

                }]
            },
            "options": {
                    "title": {
                      "display": True,
                      "text": 'Current BTN Loot & Death Ratios'
                    },  "plugins": {
                      "datalabels": {
                        "display": True,

                        "font": {
                          "size": 18,
                          "color": "#000"
                        },
                         "formatter": QuickChartFunction('(val) => val + "%"')

                      }
                }
            }
        }
        return qc.get_short_url()

    else:
        return "Invalid input (deaths, loots, ratio_flat, ratio_perc)"


def get_dump(account):
    dump_sum = {}
    legendary = ['Aegis of War', 'Aegishjalmur', "Anubis' Ankh", 'Asgardian Aegis',
                 'Band of Truth', 'Cane of Trickery', 'Ceremonial Robes', 'Daylight Mantle',
                 'Divine Authority', "Farmer's Belt", "Farmer's Hat", "Farmer's Overalls", 'Feather of Image',
                 'Feather of the Scales', 'Gjallarhorn', "Grid's Pole", "Harvester's Medallion", 'Hay-Covered Needle',
                 "Hela's Garments", "Heretic's Helm", 'Icy Baton', "Loki's Garbs", 'Mace of Heresy',
                 'Mantle of Concept', 'Megingjarpar', 'Optic Occlusion', 'Perfect Truth', "Phantom's Bane",
                 'Sagacity', "Scarecrow's Gown", 'Seaweed Brew', 'Staff of Ra', 'Sunlight Circlet', 'Tentacular Ring',
                 'The Amalgamate', 'Unholy Disk', 'Wings of Fire']

    primal = ['Draupner', 'Farmyard Candle', "Harvester's Affliction", "Hel's Massacre",
              "Hela's Power", 'Mace of Heresy', "Sun's Devastation", 'Tainted Pitchfork',
              'The Encephalon', 'Wall of Gore']


    for char in account:
        for item in char["items"]['dump']:
            if item not in dump_sum:
                if item in legendary:
                    dump_sum.update({item: ["Legendary", 1]})
                elif item in primal:
                    dump_sum.update({item: ["Primal", 1]})
                else:
                    dump_sum.update({item: ["Meh", 1]})

            else:
                dump_sum[item][1] += 1

    return dump_sum