import discord
from discord.ext import commands
from BTNAPI import BTNWrapper as RW
import os
from dotenv import load_dotenv


load_dotenv()
# Load important stuff from .env DO NOT HACK MY KINDLE FIRE.
DISCORD_TOKEN = os.getenv("TOKEN")
client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print("Ready")


'''
Lookup by player name
'''


@client.command()
async def lookup(ctx, name: str):

    account = RW.get_account(str.capitalize(name))
    if type(account) == str:
        await ctx.send(account)
    else:
        embed = discord.Embed(
            title=account['playerName'] + "\nRating: " + str(account['rating']),
            description="Account Fame: " + str(account['playerFame']) + "\nTotal Deaths: " + str(account['total_deaths']),
            colour=discord.Colour.blue()
        )

        embed.set_footer(text='Squiddy WIP')
        embed.set_author(name="Account Lookup")
        for char in account['playerCharacters']:
            embed.add_field(name="Class: " + str(char['class']) + "| Stats: " + char['stats']['statsMaxed'] +
                                 "| Fame: " + str(char['fame']),
                            value="Equipped" + str(
                                char['items']['equipped']) + "\n" + "Inventory" + str(char['items']['inventory']),
                            inline=False)

        await ctx.send(embed=embed, delete_after=300)


'''
Give a player a rating preferred (0-5)
'''


@client.command()
async def rate(ctx, name, rating):
    response = RW.update_rating(name, int(rating))
    if response == "Character Undiscovered":
        await ctx.send(response)
    else:
        await ctx.send(response)


'''
Do a BULK update of players given a list [player1, player2, ...]
finicky, will fix later
'''


@client.command(pass_context=True)
async def bulk(ctx, *args):
    args = list(args)

    for k in args:

        name = k[1:-2]
        if "'" in name:
            get_ind = name.index("'")
            if get_ind == 0:
                name = name[1:]
            else:
                name = name[:-2]

        RW.get_account(str.capitalize(name))

    await ctx.message.delete()
    await ctx.send("Player List Updated")


'''
Returns a quickchart.io graph depending on parameter given
!graph loots -> Returns a bar chart of the agg.count of each legendary/primal item (showing top 10)
!graph deaths -> Returns a bar chart of the agg.count of each Monsters kill count (showing top 10)
!graph ratio_flat -> Returns a pie chart of the agg.count of TOTAL Deaths, Primal and Legendary Drops
!graph ratio_perc -> Returns a pie chart of the agg.count of the PERCENT TOTAL Deaths, Primal and Legendary Drop
!graph players -> WIP will return total drops, deaths of each player graph-type undetermined.
'''


@client.command(pass_context=True)
async def graph(ctx, req):

    chart = RW.get_chart(req)
    await ctx.message.delete()
    await ctx.send(chart, delete_after=300)


@client.command(pass_context=True)
async def dump(ctx, name):
    account = RW.get_account(str.capitalize(name))
    await ctx.message.delete()
    if type(account) == str:
        await ctx.send(account)
    else:
        accountDump = RW.get_dump(account['playerCharacters'])

        embed = discord.Embed(
            title=account['playerName'] + "\nRating: " + str(account['rating']),
            description="Account Fame: " + str(account['playerFame']) +
                                               "\nTotal Deaths: " + str(account['total_deaths']),
            colour=discord.Colour.blue()
        )
        lege_str = "```"
        #Legendary_Embed = embed.add_field(name="Legendaries")
        for item in accountDump:
            if accountDump[item][0] == "Legendary" or accountDump[item][0] == "Primal":
                lege_str += item+" x"+str(accountDump[item][1]) +"\n"

        embed.add_field(name="Notable Items", value=lege_str+"```")

        await ctx.send(embed=embed, delete_after=300)



client.run(DISCORD_TOKEN)
