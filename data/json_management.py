import json
import os
from dataclasses import asdict

from constants import DATA_USER_PATH
from modal.user_modal import UserModal


def sync_data_user():
    if os.path.exists(DATA_USER_PATH):
        with open(DATA_USER_PATH, 'r') as f:
            return json.load(f)
    return {}


def save_user(user: UserModal):
    user_data = sync_data_user()

    if user.user_id in user_data:
        return

    user_data[user.user_id] = asdict(user)
    with open(DATA_USER_PATH, 'w') as f:
        json.dump(user_data, f, indent=4)

def check_user_registered(user_id: int) -> bool:
    user_data = sync_data_user()
    return str(user_id) in user_data

def get_user_points(user_id: int):
    user_data = sync_data_user()
    user = user_data.get(str(user_id))

    if user:
        return user.get("points")
    return None

def start_bet_by_nick(nick: str):
    user_data = sync_data_user()

    for user in user_data.values():
        accounts = user.get("accounts", [])
        for account in accounts:
            if account.get("player_name") == nick:
                return {
                    "player_name": account.get("player_name"),
                    "player_tag": account.get("player_tag")
                }

    return None