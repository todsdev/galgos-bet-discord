from dataclasses import dataclass


@dataclass()
class StatisticsModal:
    flex_win_rate: float
    flex_wins: int
    flex_losses: int
    flex_games: int
    solo_win_rate: float
    solo_wins: int
    solo_losses: int
    solo_games: int
    odd_win: float
    odd_lose: float
