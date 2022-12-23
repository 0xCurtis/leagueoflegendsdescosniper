import requests
from datetime import timedelta
from datetime import datetime
import pytz
import time
import discord
from discord.ext import tasks
import random

class lolSniper():
    def __init__(self):
        self.API_KEY = "RGAPI-33ccdc25-6a4a-4e06-a61e-3002ce16ad96"
        self.SPOT_PUUID = "64c8Bnqtzo4JZX7OMpHKOCVoxlTi9KSwNEBxj9c710XnLDVPgYG4tw8ddb5AaEW_q9xOOgckB0Bjfg"
        self.base_url = "https://europe.api.riotgames.com/lol/match/v5/matches/"

    def get_day_history(self, day_timestamp, retries=2):
        if retries > 0:
            url = f"{self.base_url}by-puuid/{self.SPOT_PUUID}/ids?startTime={day_timestamp}&start=0&count=50&api_key={self.API_KEY}"
            res = requests.get(url)
            if res.status_code == 200:
                return res.json()
            else:
                time.sleep(120)
                return self.get_day_history(day_timestamp, retries - 1)

    def get_daily_play_time(self):
        tz = pytz.timezone('Europe/Paris')
        timestamp = int(datetime.now(tz=tz).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        historic = self.get_day_history(timestamp)
        match_duration_total = 0
        for match in historic:
            url = f"{self.base_url}{match}?api_key={self.API_KEY}"
            match_data = requests.get(url)
            match_duration_total += match_data.json()['info']['gameDuration']
        return match_duration_total / 3600

class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.debug = 0
        self.triggered = False
        self.humiliation_channel = None
        self.play_time = float
        self.snipper = lolSniper()
        self.DISCORD_TOKEN = "MTA1NTU4NTA3ODc0ODY2MzgxOA.GbBDYa.dV9TqC_Ro4YBnHOo2wPBeGGTdDJ_ToetsVYDVM"

    async def setup_hook(self) -> None:
        self.my_background_task.start()

    async def on_ready(self):
        self.humiliation_channel = self.get_guild(908448072730837139).get_channel(1055585865541353564)
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(seconds = 30)
    async def my_background_task(self):
        #self.debug = self.debug + 1
        await loop(self)

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()

def get_embed_message(play_time :float):
    embedVar = discord.Embed(title="Doc a encore fraudé", color=0xFF0000)
    embedVar.add_field(name="Durée du préjudice ?", value=f"{timedelta(hours=play_time)}", inline=False)
    embedVar.add_field(name="Piece a conviction", value="https://www.op.gg/summoners/euw/Larry444")
    embedVar.set_footer(text="Made by 0xCurtis & Coach")
    return embedVar

def get_random_messages(play_time):
    time = str(timedelta(hours=play_time)).rsplit(':', 1)[0]
    array = [
        f":pensive: {time}",
        f"Il continue ... il joue depuis maintenant {time} heures",
        f"https://tenor.com/view/fortnite-aura-take-the-l-dancing-loss-gif-21664886 {time} heures",
        f"Il aurait pu passer {time} heures a se contruire un futur mais il a préféré relancé une game de lol",
        f"Doc est bloqué sur la faille depuis {time} heures",
    ]
    return array[random.randint(0, len(array) - 1)]

async def set_presence(client :DiscordClient):
    if client.play_time == 0:
        await client.change_presence(activity=discord.Game(name=f"Doc n'a pas (encore) joué aujourd'hui. Bon toutou"))
    else:
        await client.change_presence(activity=discord.Game(name=f"Doc a joué {str(timedelta(hours=client.play_time)).rsplit(':', 1)[0]} aujourd'hui"))
    
async def post_message(client :DiscordClient):
    if client.play_time > 3 and client.triggered == False:
        await client.humiliation_channel.send(embed=get_embed_message(client.play_time))
        client.triggered = True
    elif client.play_time > 3 and client.triggered == True:
        await client.humiliation_channel.send(str(get_random_messages(client.play_time)))

async def loop (client :DiscordClient):
    client.play_time = client.snipper.get_daily_play_time()
    #client.play_time = client.debug
    print(client.play_time)
    await set_presence(client)
    await post_message(client)

client = DiscordClient(intents=discord.Intents.default())
client.run(client.DISCORD_TOKEN)