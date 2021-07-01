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

SQL 

SELECT lastLookup 
FROM characterLookup
WHERE accountName = {character}
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

SQL
UPDATE characterLookup
SET accountFame = {playerFame}, Characters = {chars}, lastLookup = {datetime} 
WHERE `characterLookup.accountName` = {character.capitalize()};
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

INSERT INTO characterLookup
VALUES (0, {'playerName'}, {accountFame}, {Characters}, {datetime}, {Rating});

'''


def insert_character_data(character: dict) -> None:

    mydb = client["rotfDataBase"]
    mycol = mydb["characterLookup"]

    newinsert = {"UUID": character['UID'], "accountName": character['playerName'],
                 "accountFame": character['playerFame'], "Characters": character['playerCharacters'],
                 "lastLookup": character['dateTime'], "Rating": character['rating']}

    mycol.insert_one(newinsert)


'''
Update a players rating in MongoDB

SQL
UPDATE characterLookup
SET `characterLookup.Rating' = {rating}
WHERE `characterLookup.accountName` = {character.capitalize()};
'''


def update_character_rating(character: str, rating: int) -> str:

    mydb = client["rotfDataBase"]
    mycol = mydb["characterLookup"]

    myquery = {"accountName": character.capitalize()}
    newvals = {"$set": {"Rating": rating}}
    mycol.update_one(myquery, newvals)

    return character + " rating set to: " + str(rating)


'''
Get a players rating in MongoDB

SQL

SELECT `characterLookup.rating` AS Rating
FROM characterLookup
WHERE characterLookup.name == {character.capitalize()};
'''


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


'''
View ALL loot in mongoDB
for testing mostly.

SQL

SELECT * 
FROM loots;
'''


def view_loots() -> dict:
    mydb = client["rotfDataBase"]
    mycol = mydb["loots"]
    return mycol.find()


'''
View ALL deaths in mongoDB
for testing mostly.

SQL

SELECT *
FROM deaths;
'''


def view_deaths() -> dict:
    mydb = client["rotfDataBase"]
    mycol = mydb["deaths"]
    return mycol.find()


'''
Return MongoDB Cursor containing an aggregate sum of monster kills. Sorted By Descending

SQL

SELECT COUNT(killed_by) as Kills 
GROUP BY killed_by.
Order By Kills DESC;
'''


def get_monster_counts() -> dict:
    mydb = client["rotfDataBase"]
    mycol = mydb["deaths"]
    agg_result = mycol.aggregate([{
        "$group": {"_id": "$killed_by", "Kills": {"$sum": 1}}}, {"$sort": {"Kills": -1}}])

    return agg_result


'''
Gets the aggregate count of each monsters "kill count" in the game

SQL

SELECT killed_by, count(killed_by) as Kills
FROM deaths
WHERE player_name != "mike"
GROUP BY killed_by
ORDER BY Kills DESC

'''


def get_player_deaths(name) -> dict:
    mydb = client["rotfDataBase"]
    mycol = mydb["deaths"]

    agg_result = mycol.count_documents({"player_name": {'$eq': name}})

    return agg_result


'''
Gets the aggregate count of each valuable item drop, excluding admin

SQL 

SELECT item_name, count(item_name) as Dropped
FROM loots
WHERE player_name != "mike"
GROUP BY item_name
ORDER BY Dropped DESC
'''


def get_item_counts() -> dict:
    mydb = client["rotfDataBase"]
    mycol = mydb["loots"]
    agg_result = mycol.aggregate([{"$match": {"player_name": {"$ne": "mike"}}},
                                  {"$group": {"_id": "$item_name", "Dropped": {"$sum": 1}}},
                                  {"$sort": {"Dropped": -1}}])

    return agg_result


'''
gets the aggregate count of each item_rang (Legendary & Primal)

SQL

SELECT item_rank, count(item_rank) as Dropped
FROM loots
GROUP BY item_rank
ORDER BY Dropped DESC
'''


def get_item_rank_counts() -> dict:
    mydb = client["rotfDataBase"]
    mycol = mydb["loots"]
    agg_result = mycol.aggregate([{"$match": {"player_name": {"$ne": "mike"}}},
                                  {"$group": {"_id": "$item_rank", "Dropped": {"$sum": 1}, }},
                                  {"$sort": {"Dropped": -1}}])

    return agg_result


