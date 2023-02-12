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
    async def on_typing(self, channel: discord.TextChannel, user: discord.User, when: datetime.datetime):
        if self.config['detect_typing']:
            await self.wake_if_needed(user, channel)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild.id != 553590545801281541:
            return

        if message.content.startswith('!wake'):
            await self.send_wake(message.author, message.channel)
            return

        await self.wake_if_needed(message)

    async def wake_if_needed(self, user: discord.User, channel: discord.TextChannel):
        babe_config = self.get_babe_config(user)

        # got ourselves a babe to wake up
        if babe_config:
            now = self.get_weirdo_time()
            last_wake_val = babe_config['last_wake']
            needs_woke = last_wake_val is None or (now.date() != datetime.fromisoformat(last_wake_val).date())

            if needs_woke:
                self.logger.info(f'Waking {user.display_name} at {now}')

                fixed_channel_id = babe_config['channel']
                channel = self.bot.get_channel(fixed_channel_id) if fixed_channel_id else channel

                await self.send_wake(user, channel)
                babe_config['last_wake'] = now.isoformat()
                save_config(self.config)

    async def send_wake(self, user: discord.User, channel: discord.TextChannel):
        await channel.typing()

        if self.cog_config['use_local_gifs']:
            await channel.send(f'{user.mention}', file=discord.File(self.get_local_gif()))
        else:
            bucket_base = 'https://pub-07202295b49f458a8b84424511fa2a13.r2.dev/'
            url = f'{bucket_base}{datetime.today():%A}.gif'.lower()
            await channel.send(f'{user.mention} {url}')

    def get_babe_config(self, user: discord.User) -> str:
        for babe in self.cog_config['babes']:
            if user.id == babe['id']:
                return babe

    def get_weirdo_time(self) -> datetime:
        date = datetime.now(tz=pytz.utc)
        PST = pytz.timezone('US/Pacific')
        return date.astimezone(PST)

    def get_local_gif(self):
        today = datetime.today().strftime('%A')
        cwd = os.path.dirname(os.path.realpath(__file__))
        assets = os.path.join(cwd, 'assets')
        path = os.path.join(assets, today.lower()) + '.gif'
        return path