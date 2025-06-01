from dataclasses import dataclass

from modal.account_modal import AccountModal


@dataclass()
class UserModal:
    user_id: int
    name: str
    nick: str
    registered: bool
    accounts: list[AccountModal]
    points: float
    bankruptcies: int = 0
