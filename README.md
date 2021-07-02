# BTN (Beneath the Nexus) Repository
### Intended use is to showcase and give clear documentation in regards to Extraction, Transformation & Loading of data from both the Beneath The Nexus REST API & Google PubSub live event feed
### While this documentation is in regards to a MongoDB Cluster approach to data storage, I've added relatively simple SQL code into the python file docstrings for you to follow along if necessary.


- **.env file**
  - This file should contain your sensitive information (Cluster Database connection, Discord Bot Token, anything else you decide to add on)
  
- **BTNAPI**
  - BTNWrapper.py is a python3 wrapper for the BTN Rest API, see [BTN Swagger API](https://playbtn.com/swagger/index.html)
  - apiLogging.py was/is used to check for network issues when making a request, All Libraries currently switch default family from IPV6 TO IPV4 for the time being.
  - dict.json is a json file that holds all of the item data from the game Formatted [Key:Value -> ItemID:ItemName]
  - builditemmap.py some code to quickly update your item dict.json file with new items if they are added.
  
- **BTNDatabase**
    - BTNDatabase.py is a python file that interacts with your MongoDB Cluster, it contains all MongoDB Functionality, Excluding the pubsub insertions.
    - BTNpubsub.py is a quick example of how to connect to the paybtn websocket, subscribe to a specific event and receive new data as it is collected as well as shows basic MongoDB Insertion.
    - testing.py is where I place any use case testing I wish to run if I ever do updates to the BTNDatabase file.
    
- **BTNDiscord**
   - A Discord Bot that will Data about specific players and global data as well.
   - !lookup name Showcases all players on that account, their fame, items and total deaths
   - !rate name amount will give a player a rating, currently not much use until release, but will assist in recruitment processing.
   - !bulk ["name1", "name2", ...] Used to do a bulk update of characters that may or not be currently inside of the database.
   - !dump name Used to remove the clutter of !lookup, showcases player name, fame, rating, total deaths and Valuable items they own.
   - !graph GraphType A neat addition that will visualize data in a global sense, current commands below.
     - !graph loots Shows a barchart of the *top 10 most dropped* items in the game currently.
     - !graph deaths Shows a barchart of the *top 10 monsters* with the most player kills.
     - !graph ratio_flat Shows a pie chart of the *total*  Legendary,Primal drops and total player deaths.
     - !graph ratio_perc Shows a pie chart of the *% total* Legendary,Primal drops and total player deaths.
     
   
       
     
  
