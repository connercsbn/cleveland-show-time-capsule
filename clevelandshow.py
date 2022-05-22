import discord
import asyncio
from discord.ext import tasks, commands
from imdb import IMDb
import time
import json
from datetime import date, datetime, timedelta, time
from pprint import pprint

WHEN = time(20, 30, 0)
def build_message(episode):
    if episode:
        message = episode
        season = episode['season']
        episode_num = episode['episode']
        title = episode['title']
        air_date = episode['original air date']
        plot = episode['plot']
        rating = episode['rating']
        message = f">>> \nTonight we mark the 10th anniversary of __**The Cleveland Show's**__ Season {season} episode, ***\"{title}\"***! In this episode, with a {rating:.1f} rating on IMDb, {plot.strip()} \n*This episode originally aired on {air_date}.*"
        return message
#    return 'The finale of The Cleveland Show ended over 10 years ago. There are no more 10 year anniversaries to celebrate from this series.'
    return None

def get_next_ep_key(all_dates):
    todays_ep, next_ep = None, None
    today = date.today() - timedelta(weeks=52*10, days=13)
    for d in sorted(all_dates):
        if d == today:
            todays_ep = d.toordinal()
        if d > today:
            next_ep = d.toordinal()
            break
    return todays_ep, next_ep

def generate_hashed_eps():
    ia = IMDb()
    clevelandshow = ia.get_movie('1195935', info=['episodes'])
    date_hash = {}
    for season in clevelandshow['episodes']:
        for episode in clevelandshow['episodes'][season]:
            date = clevelandshow['episodes'][season][episode]['original air date']
            date = date.replace('.', '')
            date = datetime.strptime(date, "%d %b %Y").date().toordinal()
            date_hash[date] = clevelandshow['episodes'][season][episode]
    return date_hash

class Clevelandshow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hashed_eps = generate_hashed_eps()
        self.ep_dates = list(map(lambda x: date.fromordinal(x), self.hashed_eps.keys()))
        self.check_anniversary.start()

    def cog_unload(self):
        self.check_anniversary.cancel()

    @tasks.loop(hours=24)
    async def check_anniversary(self):
        # check next ep key just for debugging
        today_ep_key, next_ep_key = get_next_ep_key(self.ep_dates)
        todays_ep = self.hashed_eps.get(today_ep_key)
        print('today\'s ep (if any):', todays_ep)
        # start waiting until 8:30PM
        now = datetime.now()
        target_time = datetime.combine(now.date(), WHEN)
        seconds_until_target = (target_time - now).total_seconds()
        print(seconds_until_target)
        # wait
        await asyncio.sleep(seconds_until_target)
        # time to act. get episode info for message
        today_ep_key, next_ep_key = get_next_ep_key(self.ep_dates)
        todays_ep = self.hashed_eps.get(today_ep_key)
        if todays_ep:
            # schnoz chat
            message = build_message(todays_ep)
            channels = []
            with open('config.json', 'r') as file:
                channels = json.load(file)['channels']
            for channel in channels:
                current_channel = await self.bot.fetch_channel(int(channel))
                await current_channel.send(message)
        else:
            print(f"No cleveland show episodes aired on this day. Next episode will be on {next_ep_key}")
            return
