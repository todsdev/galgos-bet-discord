from dataclasses import dataclass


@dataclass()
class BetModal:
    bet_value: int
    bettor: str
    bettor_id: int
    win: bool
    possible_win: int
