import requests
import json

#Current final item id in the game
max = 446

itemMap = {}

for i in range(max):
	req = requests.get("https://playbtn.com/api/items/by-type/"+str(i)).json()
	itemMap.update({str(i): req['name']})

json = json.dumps(itemMap)
f = open("../rotfAPI/dict.json", "w")
f.write(json)
f.close()
