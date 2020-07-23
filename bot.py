# this is a bot
# import os  # for importing env vars for the bot to use
import os
from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from twitchio.ext import commands

sp = None

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_secret=os.environ['CLIENT_SECRET'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']],
)


# bot.py, below bot object
@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f'{os.environ["BOT_NICK"]} is online!')
    # ws = bot._ws  # this is only needed to send messages within event_ready
    # await ws.send_privmsg(os.environ['CHANNEL'], f'/me has landed!')


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
    await ctx.send('Commands: !help, !ohai, !song, !artistslink')


@bot.command(name='so')
async def so(ctx):
    if ctx.author.is_mod:
        await ctx.send(f'You should go check out @{ctx.content[5:]}, \
        at https://www.twitch.tv/{ctx.content[5:]}')


@bot.command(name='followage')
async def followage(ctx):
    otherusers = await bot.get_users(ctx.content.split(' ')[1])
    followage = await bot.get_follow(otherusers[0].id, '29998625')
    converted = datetime.fromisoformat(followage['followed_at'][:-1])
    currtime = datetime.utcnow()
    result = currtime - converted
    print(result)
    numyears = result.days//365
    numdays = result.days % 365

    if numyears < 1 and numdays < 1 and result.total_seconds()//60//60 < 1:
        await ctx.send(f'{otherusers[0].display_name} has, \
        been following for {int(result.total_seconds()//60)} minutes.')
    elif numyears < 1 and numdays < 1:
        await ctx.send(f'{otherusers[0].display_name} has, \
        been following for {int(result.total_seconds()//60//60)} hours.')
    elif numyears < 1:
        await ctx.send(f'{otherusers[0].display_name} has, \
        been following for {numdays} days.')
    elif numyears == 1:
        await ctx.send(f'{otherusers[0].display_name} has, \
        been following for a year and {numdays} days.')
    elif numyears > 1:
        await ctx.send(f'{otherusers[0].display_name} has, \
        been following for {numyears} years and {numdays} days.')


@bot.command(name='slow')
async def slow(ctx):
    print(ctx.author.is_mod)
    if ctx.author.is_mod:
        await ctx.slow()


@bot.command(name='unslow')
async def unslow(ctx):
    print(ctx.author.is_mod)
    if ctx.author.is_mod:
        await ctx.unslow()


@bot.command(name='song')
async def song(ctx):

    result = sp.currently_playing()
    artists = ', '.join([x['name'] for x in result['item']['artists']])
    song = result['item']['name']

    await ctx.send(f'Artist: {artists} | Title: {song}')


@bot.command(name='artistslink')
async def artistslink(ctx):

    result = sp.currently_playing()
    links = ', '.join([
        x['external_urls']['spotify']
        for x in result['item']['artists']
    ])

    await ctx.send(f'Here\'s a link for the arsits[s]: {links}')


def main():
    global sp
    sp = spotipyinit()
    bot.run()


def spotipyinit():

    CLIENT = os.environ['SPOTIPY_CLIENT_ID']
    SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
    REDIRECT = os.environ['SPOTIPY_REDIRECT_URI']
    USERNAME = os.environ['SPOTIPY_USERNAME']

    scope = 'user-read-currently-playing'

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            username=USERNAME, client_id=CLIENT, client_secret=SECRET,
            redirect_uri=REDIRECT, scope=scope,
        ),
    )

    return sp


if __name__ == '__main__':
    exit(main())
