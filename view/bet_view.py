import discord
from discord import ui


class BetModal(discord.ui.Modal, title="Fazer aposta"):
    def __init__(self, user, future):
        super().__init__()
        self.user = user
        self.future = future
        self.bet = ui.TextInput(
            label="QUANTO VOCÊ QUER APOSTAR?",
            placeholder="Digite um valor",
            max_length=10
        )
        self.add_item(self.bet)

    async def on_submit(self, interaction: discord.Interaction):
        if not self.future.done():
            self.future.set_result(self.bet.value)
        print("BetModal submit")
        return