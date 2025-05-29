import asyncio

import discord
from constants import DISCORD_TOKEN, COMMAND_REGISTER_PLAYER, TIMEOUT_MESSAGE, \
    EVENT_MESSAGE, COMMAND_BALANCE
from modal.account_model import AccountModal
from modal.user_modal import UserModal
from server.firebase.firebase_server import init_firebase, save_user_firebase, get_user_points_firebase, \
    check_user_registered_firebase
from server.riot.riot_server import return_account_information

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    init_firebase()
    print('Application started')


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith(COMMAND_REGISTER_PLAYER):
        await register_player(message)

    elif message.content.startswith(COMMAND_BALANCE):
        await get_points_balance(message)



async def start_bet(message: discord.Message):
    def check_message(received_message):
        return received_message.author == message.author and received_message.channel == message.channel

    if check_user_registered_firebase(message.author.id):
        await message.channel.send(f"{message.author.nick}, tem que registrar primeiro nóia")
        return

    else:
        try:
            await message.channel.send(f"{message.author.nick}, para quem deseja startar bet (nome da conta)?")

            player_response = await client.wait_for(EVENT_MESSAGE, timeout=60, check=check_message)
            start_bet_by_nick(player_response.content)

        except asyncio.TimeoutError:
            await message.channel.send(TIMEOUT_MESSAGE)



async def register_player(message: discord.Message):
    def check_message(received_message):
        return received_message.author == message.author and received_message.channel == message.channel

    if check_user_registered_firebase(message.author.id):
        await message.channel.send(f"{message.author.nick}, você já tem registro seu chapadinho fedorento")
        return

    else:
        try:
            await message.channel.send(f"{message.author.nick}, digite seu nick da main no lol (sem a tag)")
            response_name = await client.wait_for(EVENT_MESSAGE, timeout=60, check=check_message)

            await message.channel.send("Agora preciso da sua tag (sem o #)")
            response_tag = await client.wait_for(EVENT_MESSAGE, timeout=60, check=check_message)

            riot_data = return_account_information(response_name.content, response_tag.content)
            if riot_data is None:
                await message.channel.send("Conta não reconhecida na API Riot, tenta de novo newba")
                return

            main_account = AccountModal(
                player_name=response_name.content,
                player_tag=response_tag.content,
                main=True,
                puuid=riot_data["puuid"]
            )

            user = UserModal(
                user_id=message.author.id,
                name=message.author.name,
                nick=message.author.nick,
                accounts=[main_account],
                registered=True,
                points=1000.0
            )
            save_user_firebase(user)
            await message.channel.send("Registrado, fellinha")

        except asyncio.TimeoutError:
            await message.channel.send(TIMEOUT_MESSAGE)

async def get_points_balance(message: discord.Message):
    if check_user_registered_firebase(message.author.id):
        await message.channel.send(f"{message.author.nick}, tem que registrar primeiro menzinho")
        return

    user_points = get_user_points_firebase(message.author.id)
    if user_points == 0:
        await message.channel.send("Zerou menzinho??")

    elif user_points != 0:
        await message.channel.send(f"{user_points} pontos")



client.run(DISCORD_TOKEN)