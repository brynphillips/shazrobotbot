# this is a bot
# import os  # for importing env vars for the bot to use
import inspect
import logging.config
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from time import perf_counter

import httpx
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from twitchio.ext import commands


class Bot(commands.Bot):

    def __init__(self, logger):
        super().__init__(
            # set up the bot
            irc_token=os.environ['TMI_TOKEN'],
            client_secret=os.environ['CLIENT_SECRET'],
            client_id=os.environ['CLIENT_ID'],
            nick=os.environ['BOT_NICK'],
            prefix=os.environ['BOT_PREFIX'],
            initial_channels=[os.environ['CHANNEL']],
            scopes=[
                'user:edit:broadcast',
                'channel:moderate', 'channel_editor',
            ],
        )
        self.sp = spotipyinit()
        self.counter = 0
        self.motd = ''
        self.uptime = 0
        self.id = 29998625
        self.name = 'Shazrobot'
        self.logger = logger
        self.auth_check = validation()
        self.http.token = None
    # bot.py, below bot objects

    async def event_ready(self):
        'Called once when the bot goes online.'
        print(f'{os.environ["BOT_NICK"]} is online!')
        await self.http.generate_token()
        ws = self._ws  # this is only needed to
        # send messages within event_ready
        await ws.send_privmsg(os.environ['CHANNEL'], '/me has landed!')

    async def event_message(self, ctx):
        'Runs every time a message is sent in chat.'

        # make sure the bot ignores itself
        if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
            return

        await self.handle_commands(ctx)

    @commands.command(name='ohai')
    async def ohai(self, ctx):
        await ctx.send(f'Oh hey there @{ctx.author.name}')

    @commands.command(name='help')
    async def help(self, ctx):
        commands_list = list(inspect.getmembers(self)[2][1]['commands'].keys())
        commands_mod = ['so', 'slow', 'unslow']
        commands_semifinal = list(set(commands_list) - set(commands_mod))
        commands_final = ', '.join(commands_semifinal)
        self.logger.info(f'{ctx.author.display_name} used the command.')
        await ctx.send(f'Commands: {commands_final}')

    @commands.command(name='so')
    async def so(self, ctx):
        if ctx.author.is_mod:
            username = ctx.content.split()[1].lstrip('@')
            self.logger.info(f'{ctx.author.display_name} used the command.')
            await ctx.send(
                f'You should go check out {username}'
                f' at https://www.twitch.tv/{username} !',
            )
            # await ctx.send(f'You should go check out @{ctx.content[5:]}, \
            # at https://www.twitch.tv/{ctx.content[5:]}')

    @commands.command(name='bonk')
    async def bonk(self, ctx):
        username = ctx.content.split()[1].lstrip('@')
        self.logger.info(f'{ctx.author.display_name} used the command.')
        await ctx.send(
            f'@{username} '
            'https://i.fluffy.cc/DM4QqzjR7wCpkGPwTl6zr907X50XgtBL.png',
        )

    @commands.command(name='followage')
    async def followage(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        part = ctx.content.partition(' ')[2].replace('@', '')
        if part == '':
            followage = await self.get_follow(ctx.author.id, '29998625')
            users = [ctx.author]
        else:
            users = await self.get_users(part)
            if users:
                followage = await self.get_follow(users[0].id, '29998625')
            else:
                await ctx.send(f'{part} isn\'t following the channel!')
                return

        converted = datetime.fromisoformat(followage['followed_at'][:-1])
        currtime = datetime.utcnow()
        result = currtime - converted
        numyears = result.days//365
        numdays = result.days % 365

        if numyears < 1 and numdays < 1 and result.total_seconds()//60//60 < 1:
            await ctx.send(
                f'{users[0].display_name} has '
                f'been following for {int(result.total_seconds()//60)} '
                f'minutes.',
            )
        elif numyears < 1 and numdays < 1:
            await ctx.send(
                f'{users[0].display_name} has '
                f'been following for {int(result.total_seconds()//60//60)} '
                f'hours.',
            )
        elif numyears < 1:
            await ctx.send(
                f'{users[0].display_name} has '
                f'been following for {numdays} days.',
            )
        elif numyears == 1:
            await ctx.send(
                f'{users[0].display_name} has '
                f'been following for a year and {numdays} days.',
            )
        elif numyears > 1:
            await ctx.send(
                f'{users[0].display_name} has '
                f'been following for {numyears} years and {numdays} days.',
            )

    @commands.command(name='slow')
    async def slow(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        print(ctx.author.is_mod)
        if ctx.author.is_mod:
            await ctx.slow()

    @commands.command(name='unslow')
    async def unslow(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        print(ctx.author.is_mod)
        if ctx.author.is_mod:
            await ctx.unslow()

    @commands.command(name='ping')
    async def ping(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        await ctx.send(f'pong {ctx.content[5:]}')

    # @commands.command(name='title')
    # async def title(self, ctx):
    #     self.logger.info(f'{ctx.author.display_name} used the command.')
    #     if ctx.author.is_mod:
    #         response = await self.http.request(
    #             'PATCH',
    #             '/channels',
    #             params={'title': ctx.content.split(' ', 1)[1]},
    #         )

    @commands.command(name='motd')
    async def motd(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        if ctx.content.partition(' ')[2]:
            self.motd = ctx.content.partition(' ')[2]
            await ctx.send(
                f'{ctx.author.name} has set the !motd as '
                f'"{self.motd}"',
            )
        else:
            await ctx.send(f'{self.motd}')

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        uptime = await self.get_stream(self.id)
        timedelta = (
            datetime.utcnow()
            - datetime.fromisoformat(uptime['started_at'][:-1])
        )
        total_seconds = timedelta.total_seconds()
        hours = total_seconds//60//60
        if total_seconds//60//60 >= 1:
            await ctx.send(
                f'{self.name} has been live '
                f'for {int(total_seconds//60//60)} hours and '
                f'{int(total_seconds//60 - (60*hours))} minutes. PogChamp',
            )
        elif total_seconds//60//60 <= 1:
            await ctx.send(
                f'{self.name} has been live '
                f'for {total_seconds//60} minutes. PogChamp',
            )

    @commands.command(name='followers')
    async def followers(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        followers = await self.get_followers(self.id, count=True)
        await ctx.send(f'{self.name} has {followers} number of follows!')

    # Finish this command
    # @commands.command(name='ban')
    # async def ban(self, ctx):
        # self.logger.info(f'{ctx.author.display_name} used the command.')
        # part = ctx.content.partition(' ')[2].replace('@', '')
        # print(part)

# Spotify commands

    @commands.command(name='nextsong')
    async def nextsong(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        starttime = perf_counter()
        self.counter += 1
        if self.counter != 2:
            await ctx.send(f'Needs {2 - self.counter} more people to vote!')
        while self.counter >= 2 and perf_counter()-starttime <= 5:
            self.sp.next_track()
            self.counter = 0

    @commands.command(name='playlist')
    async def playlist(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        currplaylist = self.sp.current_user_playlists(1, 0)
        playlisturl = currplaylist['items'][0]['external_urls']['spotify']
        await ctx.send(f'Playlist: {playlisturl}')

    @commands.command(name='song')
    async def song(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        result = self.sp.currently_playing()
        artists = ', '.join([x['name'] for x in result['item']['artists']])
        song = result['item']['name']

        await ctx.send(f'Artist: {artists} | Title: {song}')

    @commands.command(name='artist')
    async def artist(self, ctx):
        self.logger.info(f'{ctx.author.display_name} used the command.')
        result = self.sp.currently_playing()
        links = ', '.join([
            x['external_urls']['spotify']
            for x in result['item']['artists']
        ])
        await ctx.send(f'Here\'s a link for the artist(s): {links}')

# Main


def main():

    # logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('shazrobotbot')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s|%(levelname)s|%(name)s|%(funcName)s|%(message)s',
    )
    file_handler = RotatingFileHandler('logging.log', maxBytes=1000*1000)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    bot = Bot(logger)
    bot.run()


def validation():
    headers = {
        'Authorization': 'OAuth ' + os.environ['OAUTH'],
    }

    validated_check = httpx.get(
        'https://id.twitch.tv/oauth2/validate',
        headers=headers,
    )

    return validated_check.text

    # async with httpx.AsyncClient() as client:
    # print('CHECK')
    # headers = {
    # 'Authorization': 'OAuth ' + os.environ['OAUTH'],
    # }

    # validated_check = await client.get(
    # 'https://id.twitch.tv/oauth2/validate',
    # headers=headers,
    # )
    # return validated_check


def spotipyinit():

    CLIENT = os.environ['SPOTIPY_CLIENT_ID']
    SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
    REDIRECT = os.environ['SPOTIPY_REDIRECT_URI']
    USERNAME = os.environ['SPOTIPY_USERNAME']

    scope = 'user-read-currently-playing, user-modify-playback-state, \
    playlist-read-collaborative'

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            username=USERNAME, client_id=CLIENT, client_secret=SECRET,
            redirect_uri=REDIRECT, scope=scope,
        ),
    )

    return sp


if __name__ == '__main__':
    exit(main())
