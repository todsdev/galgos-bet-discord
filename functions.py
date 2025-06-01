import re

from constants import Constants
from modal.bet_modal import BetModal


def extract_number_as_int(message: str) -> int:
    number_string = "".join(re.findall(Constants.Generic.REGEX_STRING_AS_INT, message))
    return int(number_string) if number_string else 0


def extract_bettor_side(message: str) -> bool | None:
    if message.endswith(Constants.Generic.KEY_W) or message.endswith(
        Constants.Generic.KEY_L
    ):
        if message.endswith(Constants.Generic.KEY_W):
            return True
        return False
    return None


def extract_win_or_lose(message: str) -> bool | None:
    if Constants.Generic.WIN in message or Constants.Generic.LOSE in message:
        if Constants.Generic.WIN in message:
            return True
        return False
    return None


def extract_winners_and_losers(bet_list: list[BetModal]):
    bet_win = [bet for bet in bet_list if bet.win]
    bet_lose = [bet for bet in bet_list if not bet.win]
    return bet_win, bet_lose
