import asyncio

import discord
from constants import DISCORD_TOKEN, COMMAND_REGISTER_PLAYER, TIMEOUT_MESSAGE, \
    EVENT_MESSAGE, COMMAND_BALANCE, COMMAND_START_BET
from modal.account_modal import AccountModal
from modal.user_modal import UserModal
from server.firebase.firebase_server import init_firebase, save_user_firebase, get_user_points_firebase, \
    check_user_registered_firebase, get_account_by_name
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

    elif message.content.startswith(COMMAND_START_BET):
        await start_bet(message)

async def start_bet(message: discord.Message):
    def check_message(received_message):
        return received_message.author == message.author and received_message.channel == message.channel

    if not check_user_registered_firebase(message.author.id):
        await message.channel.send(f"{message.author.nick}, você ainda não possui registro, digite !register primeiro!.")
        return

    else:
        try:
            await message.channel.send(f"{message.author.nick}, para quem deseja startar bet (nome da conta)?")

            player_response = await client.wait_for(EVENT_MESSAGE, timeout=60, check=check_message)

            search_response = get_account_by_name(player_response.content)
            search_response_length = len(search_response)
            if search_response_length == 0:
                await message.channel.send(f"Não foi encontrado ninguém com esse nick no banco de dados")
            elif search_response_length <= 2:
                await message.channel.send("Usuário duplicado no banco de dados, por enquanto não suportamos essa função")
            elif search_response_length == 1:
                await message.channel.send(
                    f"{message.author.nick}, seria para {search_response[0]["account"]["player_name"]}#{search_response[0]["account"]["player_tag"]}?")

                # START BET HERE


        except asyncio.TimeoutError:
            await message.channel.send(TIMEOUT_MESSAGE)

async def register_player(message: discord.Message):
    def check_message(received_message):
        return received_message.author == message.author and received_message.channel == message.channel

    if check_user_registered_firebase(message.author.id):
        await message.channel.send(f"{message.author.nick}, já possui registro.")
        return
    else:
        response_name = None
        response_tag = None
        riot_data = None

        try:
            account_verified = False
            while not account_verified:
                await message.channel.send(f"{message.author.nick}, digite seu nick da main no lol (sem a tag)")
                response_name = await client.wait_for(EVENT_MESSAGE, timeout=60, check=check_message)

                await message.channel.send("Agora somente a tag (sem o #)")
                response_tag = await client.wait_for(EVENT_MESSAGE, timeout=60, check=check_message)

                riot_data = return_account_information(response_name.content, response_tag.content)
                if riot_data is None:
                    await message.channel.send("Conta não reconhecida na API Riot, tente novamente.")
                else:
                    account_verified = True

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
            await message.channel.send("Registrado!")

        except asyncio.TimeoutError:
            await message.channel.send(TIMEOUT_MESSAGE)

async def get_points_balance(message: discord.Message):
    if not check_user_registered_firebase(message.author.id):
        await message.channel.send(f"{message.author.nick}, você ainda não possui registro, digite !register primeiro!.")
        return

    user_points = get_user_points_firebase(message.author.id)
    if user_points == 0:
        await message.channel.send(f"Points: {user_points}. Zerou??")

    elif user_points != 0:
        await message.channel.send(f"{user_points} pontos.")



client.run(DISCORD_TOKEN)