from dataclasses import dataclass


@dataclass()
class TournamentModal:
    user_id: int
    user_name: str
    wins: int = 0
    losses: int = 0
    has_win_streak: bool = False
    consecutive_wins: int = 0

    def check_and_update_win_streak(self, streak_threshold: int = 3):
        if self.consecutive_wins >= streak_threshold:
            self.has_win_streak = True
        else:
            self.has_win_streak = False

    def add_win(self):
        self.wins += 1
        self.consecutive_wins += 1
        self.check_and_update_win_streak()

    def add_loss(self):
        self.losses += 1
        self.consecutive_wins = 0
        self.has_win_streak = False
