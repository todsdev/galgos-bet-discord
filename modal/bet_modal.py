from dataclasses import dataclass
from modal.statistics_modal import StatisticsModal
from modal.user_modal import UserModal


@dataclass()
class BetModal:
    mode: str
    started: bool
    total_points: int
    total_bets: int
    bettors = list[UserModal]
    player: str
    odd: float
    player_statistics: StatisticsModal