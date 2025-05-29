from dataclasses import dataclass
from modal.statistics_modal import StatisticsModal

@dataclass()
class BetModal:
    mode: str
    started: bool
    total_points: int
    total_bets: int
    who_is_playing_one: str
    who_is_playing_two: str
    multiplier: float
    player_one_statistics: StatisticsModal