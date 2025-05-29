import requests

from constants import RIOT_BASE_URL, RIOT_API_TOKEN


def return_account_information(name, tag):
    url = f"{RIOT_BASE_URL}/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={RIOT_API_TOKEN}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def calculate_win_rate(name):
    url = f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={RIOT_API_TOKEN}'
