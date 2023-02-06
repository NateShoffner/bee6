import asyncio
import discord
import logging
import sys
from cogs.luminewake import LumineWake
from cogs.tldr.tldr import Summurize
from config import load_config
from discord.ext import commands
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger()

user_config = load_config()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), intents=intents)

def init_logging():
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

    file_logger = TimedRotatingFileHandler('./logs/logfile.log', 
                                    when='midnight',
                                    backupCount=10)
    file_logger.setFormatter(formatter)
    logger.addHandler(file_logger)

    console_logger = logging.StreamHandler()
    console_logger.setFormatter(formatter)
    logger.addHandler(console_logger)

    # supress discord logging
    logging.getLogger('discord').setLevel(logging.WARNING)

    if user_config['debug']:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} is now running!')
    
# TODO doesn't work unless mentioned explicitly
@bot.command(name='sync')
@commands.is_owner()
async def sync(ctx):
    logger.info('Syncing commands')
    try:
        synced = await bot.tree.sync()
        logger.info(f'Synced {len(synced)} commands')
        await ctx.send(f'Synced {len(synced)} commands')
    except Exception as e:
        logger.error(e)

@bot.tree.command(name='ping')
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(title = 'Pong!', description=f'Latency: {round(bot.latency * 1000)}ms')
    await interaction.response.send_message(embed = embed)

async def main():
    init_logging()
    await bot.add_cog(Summurize(bot, user_config, logger))
    await bot.add_cog(LumineWake(bot, user_config, logger))
    await bot.start(user_config['bot_token'])

if __name__ == '__main__':
    asyncio.run(main())