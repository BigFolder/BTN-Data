import pymongo
from dotenv import load_dotenv
import os
import datetime

# Used to load out mongoDB credentials outside of this file.
load_dotenv()
MONGODB = os.getenv("MONGO_DATABASE")

# Open cluster & travel to my Database -> Collection

client = pymongo.MongoClient(MONGODB)

'''
Checks to see the last time (If ever) a character name was looked up
If it was greater than 5 minutes since the last request, a fresh request is made.
Otherwise you'll get the character Data from less than  5 minutes ago.
'''


def check_character_last_update(character: str) -> str or bool:

    mydb = client["rotfDataBase"]
    mycol = mydb["characterLookup"]
    search = mycol.find({"accountName": character.capitalize()})

    if search.count() >= 1:
        lastlookup = search[0]['lastLookup']
        # Check if the last lookup was greater than 5 minutes ago confirm the need for another request.
        if datetime.datetime.now() - datetime.timedelta(minutes=5) > lastlookup:

            return True
        # If it isn't return the last call that was less than 5 minutes ago.
        else:

            return search[0]
    else:

        return "New"


'''
Updates a character in the database.

Return is not necessary
'''


def update_character_data(character: dict) -> None:

    mydb = client["rotfDataBase"]
    mycol = mydb["characterLookup"]

    myquery = {"accountName": character['playerName']}
    newvals = {"$set": {"accountFame": character['playerFame'], "Characters": character['playerCharacters'],
                        "lastLookup": character['dateTime']}}

    mycol.update_one(myquery, newvals)


'''
Inserts a NEW player account into the database.
Return is not necessary
'''


def insert_character_data(character: dict) -> None:

    mydb = client["rotfDataBase"]
    mycol = mydb["characterLookup"]

    newinsert = {"UUID": character['UID'], "accountName": character['playerName'],
                 "accountFame": character['playerFame'], "Characters": character['playerCharacters'],
                 "lastLookup": character['dateTime'], "Rating": character['rating']}

    mycol.insert_one(newinsert)


def update_character_rating(character: str, rating: int) -> str:

    mydb = client["rotfDataBase"]
    mycol = mydb["characterLookup"]

    myquery = {"accountName": character.capitalize()}
    newvals = {"$set": {"Rating": rating}}
    mycol.update_one(myquery, newvals)

    return character + " rating set to: " + str(rating)


def get_rating(character: str) -> int or str:

    mydb = client["rotfDataBase"]
    mycol = mydb["characterLookup"]

    myquery = {"accountName": character.capitalize()}
    char = mycol.find(myquery)

    if char.count() == 1:
        for i in char:
            return i["Rating"]
    else:
        return "Character Undiscovered"
