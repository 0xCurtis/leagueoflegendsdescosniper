import requests
from datetime import timedelta
from datetime import datetime
import pytz
import time
import discord
import asyncio
import random

def get_start_tmstp():
    tz = pytz.timezone('Europe/Paris')
    return int(datetime.now(tz=tz).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

def get_day_history(day_timestamp, retries=2):
    if retries > 0:
        BASE_URL = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{SPOT_PUUID}/ids?startTime={day_timestamp}&start=0&count=50&api_key={API_KEY}"
        res = requests.get(BASE_URL)
        if res.status_code == 200:
            return res.json()
        else:
            time.sleep(120)
            return get_day_history(day_timestamp, retries - 1)

def get_daily_play_time():
    historic = get_day_history(get_start_tmstp())
    match_duration_total = 0
    for match in historic:
        url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match}?api_key={API_KEY}"
        match_data = requests.get(url)
        match_duration_total += match_data.json()['info']['gameDuration']
    return 3.1, len(historic) #debug
    return match_duration_total / 3600, len(historic)

class MyClient(discord.Client):
    async def my_loop(self):
        debug = 0
        while True:
            play_time, match_played = get_daily_play_time()
            debug = debug + 1
            match_played = debug #debug
            print(play_time)
            print(match_played)
            embedVar = discord.Embed(title="Doc a encore fraudé", color=0xFF0000)
            embedVar.add_field(name="Durée du préjudice ?", value=f"{timedelta(hours=play_time)}", inline=False)
            embedVar.add_field(name="Piece a conviction", value="https://www.op.gg/summoners/euw/Larry444")
            embedVar.set_footer(text="Made by 0xCurtis & Coach")
            if play_time == 0:
                await self.change_presence(activity=discord.Game(name=f"Doc n'a pas (encore) joué aujourd'hui. Bon toutou"))
            else:
                await self.change_presence(activity=discord.Game(name=f"Doc a joué {str(timedelta(hours=play_time)).rsplit(':', 1)[0]} aujourd'hui"))
            if play_time > 3 and self.triggered == False:
                await self.humiliation_channel.send(embed=embedVar)
                self.triggered = True
            elif play_time > 3 and self.triggered == True and match_played > self.match_played:
                await self.humiliation_channel.send(str(get_random_messages(play_time)))
            self.match_played = match_played
            time.sleep(1) #must be 30

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.triggered = False
        self.humiliation_channel = client.get_guild(908448072730837139).get_channel(1055585865541353564)
        self.match_played = 0
        await self.my_loop()
        return ""
        
    async def on_message(message):
        print("new message")
        

API_KEY = "RGAPI-33ccdc25-6a4a-4e06-a61e-3002ce16ad96"
SPOT_PUUID = "64c8Bnqtzo4JZX7OMpHKOCVoxlTi9KSwNEBxj9c710XnLDVPgYG4tw8ddb5AaEW_q9xOOgckB0Bjfg"
DISCORD_TOKEN = "MTA1NTU4NTA3ODc0ODY2MzgxOA.GbBDYa.dV9TqC_Ro4YBnHOo2wPBeGGTdDJ_ToetsVYDVM"

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

intents = discord.Intents(value=8, guilds=True)
client = MyClient(intents=intents)
asyncio.run(client.run(DISCORD_TOKEN))