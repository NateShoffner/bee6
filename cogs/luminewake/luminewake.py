import typing
import discord
import logging
import os
from datetime import datetime
from discord.ext import commands
import pytz

from config import save_config

class LumineWake(commands.Cog):
    
    def __init__(self, bot, config, logger):
        self.bot = bot
        self.config = config
        self.cog_config = config['cogs']['luminewake']
        self.logger = logger

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('LumineWake ready')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild.id != 699424562017730622:
            return

        if message.content.startswith('!wake'):
            await self.send_wake(message.author, message.channel)
            return

        babe_config = self.get_babe_config(message.author)
        # got ourselves a babe to wakeup
        if babe_config:
            now = self.get_weirdo_time()
            last_wake_val = babe_config['last_wake']
            needs_woke = last_wake_val is None or (now.date() != datetime.fromisoformat(last_wake_val).date())

            if needs_woke:
                self.logger.info(f'Waking {message.author.display_name} at {now}')
                await self.send_wake(message.author, message.channel)
                babe_config['last_wake'] = now.isoformat()
                save_config(self.config)


    async def send_wake(self, user: discord.User, channel: discord.TextChannel):
        await channel.typing()
        # TODO host gifs on a CDN
        await channel.send(f'{user.mention}', file=discord.File(self.get_gif()))

    def get_babe_config(self, user: discord.User) -> str:
        for babe in self.cog_config['babes']:
            if user.id == babe['id']:
                return babe

    def get_weirdo_time(self) -> datetime:
        date = datetime.now(tz=pytz.utc)
        PST = pytz.timezone('US/Pacific')
        return date.astimezone(PST)

    def get_gif(self):
        today = datetime.today().strftime('%A')
        cwd = os.path.dirname(os.path.realpath(__file__))
        assets = os.path.join(cwd, 'assets')
        path = os.path.join(assets, today.lower()) + '.gif'
        return path