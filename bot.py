#this is a bot

import os # for importing env vars for the bot to use
import requests
import json
from twitchio.ext import commands

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
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

@bot.command(name='song')
async def song(ctx):
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + str(os.environ['SPOTIFY_TOKEN']),
    }

    response = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    song = response.json()['item']['name']
    artists = ", ".join([x['name'] for x in response.json()['item']['artists']])

    await ctx.send(f'Artist: {artists} | Title: {song}')

def main():

    bot.run()

if __name__ == '__main__':
    exit(main())
