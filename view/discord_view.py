import discord
from discord import ui

from view.bet_view import BetModal


class DiscordBetView(ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user

    @ui.button(label="Place bet")
    async def confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            return

        modal = BetModal(self.user)
        await interaction.response.send_modal(modal)

