import discord
from discord import ui


class BetModal(discord.ui.Modal, title="Fazer aposta"):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.bet = ui.TextInput(
            label="QUANTO VOCÊ QUER APOSTAR?",
            placeholder="Digite um valor",
            max_length=10
        )
        self.add_item(self.bet)

    async def on_submit(self, interaction: discord.Interaction):
        print("BetModal submit")
        return