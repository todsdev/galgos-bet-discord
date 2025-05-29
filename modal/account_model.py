from dataclasses import dataclass

@dataclass()
class AccountModal:
    player_tag: str
    player_name: str
    main: bool
    puuid: str