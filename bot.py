#this is a bot

import os # for importing env vars for the bot to use
import requests
import json
import re
from datetime import date
from datetime import datetime
from twitchio.ext import commands

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_secret=os.environ['CLIENT_SECRET'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)


# bot.py, below bot object
@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f'{os.environ["BOT_NICK"]} is online!')
    ws = bot._ws  # this is only needed to send messages within event_ready
    #await ws.send_privmsg(os.environ['CHANNEL'], f'/me has landed!')

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'

    # make sure the bot ignores itself
    if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
        return

    await bot.handle_commands(ctx)

@bot.command(name='ohai')
async def greeting(ctx):
    await ctx.send(f'Oh hey there @{ctx.author.name}')

@bot.command(name='help')
async def help(ctx):
    await ctx.send(f'Commands: !help, !ohai')

@bot.command(name='so')
async def so(ctx):
    if ctx.author.is_mod == False:
        return
    else:
        await ctx.send(f'You should go check out @{ctx.content[5:]} at https://www.twitch.tv/{ctx.content[5:]}')

@bot.command(name='followage')
async def followage(ctx):
    otherusers = await bot.get_users(ctx.content.split(" ")[1])
    followage = await bot.get_follow(otherusers[0].id, '29998625')
    converted = datetime.fromisoformat(followage['followed_at'][:-1])
    currtime = datetime.today()
    result = currtime - converted
    numyears = result.days//365
    numdays = result.days % 365

    if numyears < 1:
        await ctx.send(f'{otherusers[0].display_name} has been following for {numdays} days.')
    elif numyears == 1:
        await ctx.send(f'{otherusers[0].display_name} has been following for a year and {numdays} days.')
    elif numyears > 1:
        await ctx.send(f'{otherusers[0].display_name} has been following for {numyears} years and {numdays} days.')

@bot.command(name='slow')
async def slow(ctx):
    print(ctx.author.is_mod)
    if ctx.author.is_mod == False:
        return
    else:
        await ctx.slow()

@bot.command(name='unslow')
async def unslow(ctx):
    print(ctx.author.is_mod)
    if ctx.author.is_mod == False:
        return
    else:
        await ctx.unslow()

#@bot.command(name='song')
#async def song(ctx):

    # headers = {
    # 'Accept': 'application/json',
    # 'Content-Type': 'application/json',
    # 'Authorization': 'Bearer ' + str(os.environ['SPOTIFY_TOKEN']),
    # }

    # response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    # print(response)
    # song = response.json()['item']['name']
    # artists = ", ".join([x['name'] for x in response.json()['item']['artists']])

    #await ctx.send(f'Artist: {artists} | Title: {song}')
    #The way I got this to work before was to grab client secret
    #and add to env seperatly. Expires in 1 hour though

def main():

    bot.run()

if __name__ == '__main__':
    exit(main())
