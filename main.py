import requests
from datetime import datetime
import pytz
import time

API_KEY = "RGAPI-33ccdc25-6a4a-4e06-a61e-3002ce16ad96"
SPOT_PUUID = "64c8Bnqtzo4JZX7OMpHKOCVoxlTi9KSwNEBxj9c710XnLDVPgYG4tw8ddb5AaEW_q9xOOgckB0Bjfg"

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

if __name__ == "__main__":
    historic = get_day_history(get_start_tmstp())
    match_duration_total = 0
    for match in historic:
        url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match}?api_key={API_KEY}"
        match_data = requests.get(url)
        match_duration_total += match_data.json()['info']['gameDuration']
    match_duration_total / 3600