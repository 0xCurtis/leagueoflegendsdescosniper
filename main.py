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
        self.API_KEY = ""
        self.SPOT_PUUID = ""
        self.base_url = "https://europe.api.riotgames.com/lol/match/v5/matches/"
        self.current_day = int(datetime.now(tz=pytz.timezone('Europe/Paris')).replace(hour=6, minute=0, second=0, microsecond=0).timestamp())
        self.historic = []
        self.triggered = False

    def get_day_history(self, day_timestamp, retries=2):
        if retries > 0:
            url = f"{self.base_url}by-puuid/{self.SPOT_PUUID}/ids?startTime={day_timestamp}&start=0&count=50&api_key={self.API_KEY}"
            res = requests.get(url)
            if res.status_code == 200:
                return res.json()
            else:
                time.sleep(120)
                return self.get_day_history(day_timestamp, retries - 1)

    def get_winrate(self, match_data):
        win = 0
        loose = 0
        for player in match_data['info']['participants']:
                if player['summonerName'] == "Larry444":
                    if player['win'] == False:
                        loose += 1
                    else:
                        win += 1
                else:
                    pass
        if win == 0 and loose+win != 0:
            return 0.00
        return ((loose + win) / win) * 100

    def get_data(self):
        timestamp = int(datetime.now(tz=pytz.timezone('Europe/Paris')).replace(hour=6, minute=0, second=0, microsecond=0).timestamp())
        if timestamp != self.current_day:
            self.current_day = timestamp
            self.triggered = False
        temp_historic = self.get_day_history(timestamp)
        if self.historic == temp_historic:
            return False
        self.historic = temp_historic
        self.playtime = 0

        for match in self.historic:
            url = f"{self.base_url}{match}?api_key={self.API_KEY}"
            match_data = requests.get(url).json()
            self.playtime += match_data['info']['gameDuration']
            self.winrate = self.get_winrate(match_data)
        self.playtime /= 3600
        return True

class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.humiliation_channel = None
        self.sniper = lolSniper()
        self.DISCORD_TOKEN = ""

    async def setup_hook(self) -> None:
        self.my_background_task.start()

    async def on_ready(self):
        self.humiliation_channel = self.get_guild(860295237078745118).get_channel(1068167487348285500)
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(seconds = 30)
    async def my_background_task(self):
        await loop(self)

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()

def get_first_embed_message(play_time :float):
    embedVar = discord.Embed(title="Doc a encore fraudé", color=0xFF0000)
    embedVar.add_field(name="Durée du préjudice ?", value=f"{timedelta(hours=play_time)}", inline=False)
    embedVar.add_field(name="Piece a conviction", value="https://www.op.gg/summoners/euw/Larry444")
    embedVar.set_footer(text="Made by 0xCurtis & Coach")
    return embedVar

def get_random_embed_message(play_time :float, random_str: str, winrate: float):
    embedVar = discord.Embed(title="On te surveille fraudeur.", color=0xFF0000)
    embedVar.add_field(name="Durée du préjudice ?", value=f"{timedelta(hours=play_time)}", inline=False)
    embedVar.add_field(name="Piece a conviction", value="https://www.op.gg/summoners/euw/Larry444", inline=False)
    embedVar.add_field(name="", value=random_str, inline=False)
    embedVar.add_field(name="Mashallah le winrate", value=winrate)
    embedVar.set_footer(text="Made by 0xCurtis & Coach")
    return embedVar

def get_random_messages(play_time):
    time = str(timedelta(hours=play_time)).rsplit(':', 1)[0]
    array = [
        f":pensive: une déception",
        f"Il continue ... il aura joué {time} heures aujourd'hui",
        f"Il aurait pu passer {time} heures a se contruire un futur mais il a préféré relancé une game de lol",
        f"Doc est bloqué sur la faille depuis {time} heures",
        f"Doc... il est pas trop tard pour désinstaller et ce construire un avenir",
        f"Tu pense que lancer des haches en botlane c'est un projet long terme ?",
        f"Les zhommes les zomelette..... et Doc :pensive:",
        f"Where is the sable of Metz Plage ???????? surement pas sur LOL donc ferme ce jeu",
        f"As-tu fait ta lecture du coran quotidienne ?",
        f"Guez man EWAAAA",
        f"Si tu relance une game ça veut dire que tu supplie",
    ]
    return array[random.randint(0, len(array) - 1)]

async def set_presence(client :DiscordClient):
    if client.sniper.playtime == 0:
        await client.change_presence(activity=discord.Game(name=f"Doc n'a pas (encore) joué aujourd'hui. Bon toutou"))
    else:
        await client.change_presence(activity=discord.Game(name=f"Doc a joué {str(timedelta(hours=client.sniper.playtime)).rsplit(':', 1)[0]} heures aujourd'hui"))
    
async def post_message(client :DiscordClient):
    if client.sniper.playtime > 1 and client.sniper.triggered == False:
        await client.humiliation_channel.send(embed=get_first_embed_message(client.sniper.playtime))
        client.sniper.triggered = True
    elif client.sniper.playtime > 1 and client.sniper.triggered == True:
        await client.humiliation_channel.send(embed=get_random_embed_message(client.sniper.playtime, get_random_messages(client.sniper.playtime), client.sniper.winrate))

async def loop (client :DiscordClient):
    update = client.sniper.get_data()
    await set_presence(client)
    if update:
        await post_message(client)

client = DiscordClient(intents=discord.Intents.default())
client.run(client.DISCORD_TOKEN)