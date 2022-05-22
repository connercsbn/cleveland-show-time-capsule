from dotenv import load_dotenv
import logging
import asyncio, os
from pprint import pprint
import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get
import random
from clevelandshow import Clevelandshow
import time
import json


logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger('discord')
logger.setLevel(logging.CRITICAL)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


intents = discord.Intents()
intents.messages = True

bot = commands.Bot(
        command_prefix=commands.when_mentioned_or("!"),
        description='Get celebratory updates as we reach the 10th anniversary of every Cleveland Show episode',
        intents=intents
      )

channels = None
with open("./config.json", "r") as channel_file:
    channels = json.load(channel_file)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

bot.add_cog(Clevelandshow(bot))

@bot.event
async def on_message(message):
    print(message)
    if message.content.startswith('!'):
        await bot.process_commands(message)

@bot.command()
async def cleveland(ctx):
    current_channel = await ctx.bot.fetch_channel(int(ctx.channel.id))
    channel_id = ctx.channel.id
    if channel_id in channels['channels']:
        channels['channels'].remove(channel_id)
        with open("./config.json", "w") as file:
            json.dump(channels, file, indent=4)
        await ctx.send(f'Removed channel `{current_channel.name}`')
    else:
        channels['channels'].append(channel_id)
        with open("./config.json", "w") as file:
            json.dump(channels, file, indent=4)
        await ctx.send(f'Added channel `{current_channel.name}`')

load_dotenv()
bot.run(os.getenv('TOKEN'))
