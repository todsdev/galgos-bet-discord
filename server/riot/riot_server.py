import os
import requests
from urllib.parse import quote
from constants import Constants

RIOT_API_TOKEN = os.getenv("RIOT_API_TOKEN")


def return_account_information(name, tag):
    url = f"{Constants.Riot.URL_ACCOUNT_BY_RIOT_ID}{quote(name)}/{quote(tag)}{Constants.Generic.API_KEY}{RIOT_API_TOKEN}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"{Constants.Errors.RIOT_ERROR_ACCOUNT_INFORMATION}{response.status_code} - {response.text}"
        )
        return None


def spectate_live_game(puuid):
    url = f"{Constants.Riot.URL_SPECTATE_LIVE_GAME}{puuid}{Constants.Generic.API_KEY}{RIOT_API_TOKEN}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"{Constants.Errors.RIOT_ERROR_SPECTATE_LIVE_GAME}{response.status_code} - {response.text}"
        )
        return None


def check_match_result(game_id):
    url = f"{Constants.Riot.URL_MATCH_RESULT}{game_id}{Constants.Generic.API_KEY}{RIOT_API_TOKEN}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"{Constants.Errors.RIOT_ERROR_MATCH_RESULT}{response.status_code} - {response.text}"
        )
        return None


def retrieve_win_rate(puuid):
    url = f"{Constants.Riot.URL_WIN_RATE}{puuid}{Constants.Generic.API_KEY}{RIOT_API_TOKEN}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"{Constants.Errors.RIOT_ERROR_WIN_RATE}{response.status_code} - {response.text}"
        )
        return None
