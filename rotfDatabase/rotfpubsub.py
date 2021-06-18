import json
import asyncio
import websockets
import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
MONGODB = os.getenv("MONGO_DATABASE")

# Open cluster & travel to my Database -> Collection

client = pymongo.MongoClient(MONGODB)


def insert_loot(character):
    mydb = client["rotfDataBase"]
    mycol = mydb["loots"]

    newinsert = {"item_rank": character["item_rank"], "item_name": character['item_name'],
                 "player_name": character['player_name'], "damage_dealt_perc": character['damage_dealt_perc'],
                 "damage_dealt_exact": character['damage_dealt_exact'], "datetime": datetime.now()}

    mycol.insert_one(newinsert)


def insert_death(character):
    mydb = client["rotfDataBase"]
    mycol = mydb["deaths"]

    newinsert = {"player_name": character["player_name"],
                 "killed_by": character['killed_by'], "datetime": datetime.now()}

    mycol.insert_one(newinsert)


async def build_conns():

    async with websockets.connect("wss://playbtn.com:2096") as websocket:

        await websocket.send(json.dumps({"request": "subscribe", "event": "death"}))
        await websocket.send(json.dumps({"request": "subscribe", "event": "announce"}))
        await websocket.send(json.dumps({"request": "subscribe", "event": "loot"}))

        while True:
            result = await websocket.recv()
            result = json.loads(result)
            if result["event_type"] == "loot":
                insert_loot(result)
            elif result["event_type"] == "death":
                insert_death(result)
            else:
                print("We're here?", result)

try:
    asyncio.run(build_conns())
except:
    print("ERROR OCCURRED")
    asyncio.run(build_conns())



