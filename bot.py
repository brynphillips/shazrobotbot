# this is a bot
# import os  # for importing env vars for the bot to use
import os
from datetime import datetime
from time import perf_counter

import httpx
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from twitchio.ext import commands


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            # set up the bot
            irc_token=os.environ['TMI_TOKEN'],
            client_secret=os.environ['CLIENT_SECRET'],
            client_id=os.environ['CLIENT_ID'],
            nick=os.environ['BOT_NICK'],
            prefix=os.environ['BOT_PREFIX'],
            initial_channels=[os.environ['CHANNEL']],
        )
        self.sp = spotipyinit()
        self.counter = 0

    # bot.py, below bot objects

    async def event_ready(self):
        'Called once when the bot goes online.'
        print(f'{os.environ["BOT_NICK"]} is online!')
        # ws = bot._ws  # this is only needed to
        # send messages within event_ready
        # await ws.send_privmsg(os.environ['CHANNEL'], f'/me has landed!')

    async def event_message(self, ctx):
        'Runs every time a message is sent in chat.'

        # make sure the bot ignores itself
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            return

        await self.handle_commands(ctx)

    @commands.command(name='ohai')
    async def greeting(self, ctx):
        await ctx.send(f'Oh hey there @{ctx.author.name}')

    @commands.command(name='help')
    async def help(self, ctx):
        await ctx.send('Commands: !help, !ohai, !song, !artistslink')

    @commands.command(name='so')
    async def so(self, ctx):
        if ctx.author.is_mod:
            await ctx.send(f'You should go check out @{ctx.content[5:]}, \
            at https://www.twitch.tv/{ctx.content[5:]}')

    @commands.command(name='followage')
    async def followage(self, ctx):
        part = ctx.content.partition(' ')[2].replace('@', '')
        if part == '':
            followage = await self.get_follow(ctx.author.id, '29998625')
            otherusers = [ctx.author]
        else:
            otherusers = await self.get_users(part)
            followage = await self.get_follow(otherusers[0].id, '29998625')
        # print(followage['followed_at'])
        if followage is None:
            await ctx.send(f'{otherusers[0].display_name} isn\'t \
            following the channel!')
            return
        else:
            converted = datetime.fromisoformat(followage['followed_at'][:-1])
        currtime = datetime.utcnow()
        result = currtime - converted
        numyears = result.days//365
        numdays = result.days % 365

        if numyears < 1 and numdays < 1 and result.total_seconds()//60//60 < 1:
            await ctx.send(f'{otherusers[0].display_name} has \
            been following for {int(result.total_seconds()//60)} minutes.')
        elif numyears < 1 and numdays < 1:
            await ctx.send(f'{otherusers[0].display_name} has \
            been following for {int(result.total_seconds()//60//60)} hours.')
        elif numyears < 1:
            await ctx.send(f'{otherusers[0].display_name} has \
            been following for {numdays} days.')
        elif numyears == 1:
            await ctx.send(f'{otherusers[0].display_name} has \
            been following for a year and {numdays} days.')
        elif numyears > 1:
            await ctx.send(f'{otherusers[0].display_name} has \
            been following for {numyears} years and {numdays} days.')

    @commands.command(name='slow')
    async def slow(self, ctx):
        print(ctx.author.is_mod)
        if ctx.author.is_mod:
            await ctx.slow()

    @commands.command(name='unslow')
    async def unslow(self, ctx):
        print(ctx.author.is_mod)
        if ctx.author.is_mod:
            await ctx.unslow()

    @commands.command(name='song')
    async def song(self, ctx):

        result = self.sp.currently_playing()
        artists = ', '.join([x['name'] for x in result['item']['artists']])
        song = result['item']['name']

        await ctx.send(f'Artist: {artists} | Title: {song}')

    @commands.command(name='artist')
    async def artist(self, ctx):

        result = self.sp.currently_playing()
        links = ', '.join([
            x['external_urls']['spotify']
            for x in result['item']['artists']
        ])

        await ctx.send(f'Here\'s a link for the artist(s): {links}')

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send(f'pong {ctx.content[5:]}')

    @commands.command(name='title')
    async def title(self, ctx):
        if ctx.author.is_mod:
            async with httpx.AsyncClient() as client:

                headers = {
                    'Authorization': 'Bearer ' + os.environ['OAUTH'],
                    'client-id': os.environ['EDITOR_ID'],
                }

                await client.patch(
                    'https://api.twitch.tv/helix/channels/\
                    ?broadcaster_id=29998625',
                    headers=headers,
                    data={'title': ctx.content.split(' ', 1)[1]},
                )

    @commands.command(name='nextsong')
    async def nextsong(self, ctx):
        starttime = perf_counter()
        if ctx.content == '!nextsong':
            self.counter += 1
        while self.counter >= 2 and perf_counter()-starttime <= 5:
            self.sp.next_track()
            self.counter = 0


def main():
    # change this global variable to something else
    bot = Bot()
    bot.run()


def spotipyinit():

    CLIENT = os.environ['SPOTIPY_CLIENT_ID']
    SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
    REDIRECT = os.environ['SPOTIPY_REDIRECT_URI']
    USERNAME = os.environ['SPOTIPY_USERNAME']

    scope = 'user-read-currently-playing, user-modify-playback-state'

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            username=USERNAME, client_id=CLIENT, client_secret=SECRET,
            redirect_uri=REDIRECT, scope=scope,
        ),
    )

    return sp


if __name__ == '__main__':
    exit(main())
