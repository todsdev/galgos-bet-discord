from dataclasses import dataclass


@dataclass()
class BetModal:
    bet_value: int
    bettor: str
    win: bool
    possible_win: int