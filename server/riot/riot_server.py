import requests
from urllib.parse import quote
from constants import Constants


def return_account_information(name, tag):
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(name)}/{quote(tag)}?api_key={Constants.Riot.RIOT_API_TOKEN}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error(return_account_information): {response.status_code} - {response.text}")
        return None

def spectate_live_game(puuid):
    url = f'https://br1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={Constants.Riot.RIOT_API_TOKEN}'

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error(spectate_live_game): {response.status_code} - {response.text}")
        return None

def check_match_result(game_id):
    url = f'https://americas.api.riotgames.com/lol/match/v5/matches/BR1_{game_id}?api_key={Constants.Riot.RIOT_API_TOKEN}'

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error(check_match_result): {response.status_code} - {response.text}")
        return None

def retrieve_win_rate(puuid):
    url = f'https://br1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={Constants.Riot.RIOT_API_TOKEN}'

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error(retrieve_win_rate): {response.status_code} - {response.text}")
        return None