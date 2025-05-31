import asyncio

import discord
from constants import DISCORD_TOKEN, COMMAND_REGISTER_PLAYER, TIMEOUT_MESSAGE, \
    EVENT_MESSAGE, COMMAND_BALANCE, COMMAND_START_BET, COMMAND_COMMANDS, COMMAND_RANKING, COMMAND_SELF_BET
from modal.account_modal import AccountModal
from modal.user_modal import UserModal
from server.firebase.firebase_server import init_firebase, save_user_firebase, get_user_points_firebase, \
    check_user_registered_firebase, get_account_by_name, add_points_to_user, get_account_by_id, get_points_ranking
from server.riot.riot_server import return_account_information, spectate_live_game, check_match_result, \
    retrieve_win_rate
from view.discord_bet_view import DiscordBetView

intents = discord.Intents.all()
client = discord.Client(intents=intents)
is_bet_started = False


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

    elif message.content.startswith(COMMAND_COMMANDS):
        await display_commands(message)

    elif message.content.startswith(COMMAND_RANKING):
        await get_ranking(message)

    elif message.content.startswith(COMMAND_SELF_BET):
        await start_self_bet(message)


async def get_ranking(message: discord.Message):
    ranking = get_points_ranking()
    print(ranking)

    title = "Ranking"
    description = ""

    for i, player in enumerate(ranking[:10], start=1):
        name = player.get("player_name", "Desconhecido")
        points = player.get("points", 0)
        description += f"**{i}. {name}** — {points} pontos\n"
    color = discord.Color.blue()
    await send_embed_message(message, title, description, color)



async def bet_for_myself(message):
    try:
        accounts = get_account_by_id(message.author.id)
        accounts_length = len(accounts)

        if accounts_length == 0:
            await message.channel.send(f"Não foi encontrado ninguém com esse nick no banco de dados")
        elif accounts_length >= 2:
            await message.channel.send("Usuário duplicado no banco de dados, por enquanto não suportamos essa função")
        elif accounts_length == 1:
            await handle_bet_for_specific_player_found(message, accounts)

    except asyncio.TimeoutError:
        await message.channel.send(TIMEOUT_MESSAGE)


async def start_self_bet(message: discord.Message):
    global is_bet_started

    if not check_user_registered_firebase(message.author.id):
        await message.channel.send(f"{message.author.display_name}, você ainda não possui registro, digite !register primeiro.")
        return
    else:
        if is_bet_started:
            await message.channel.send("Já existe uma bet ativa no momento, espere o final ou reclame com o dev que não escalou a aplicação direito por preguiça.")
            return
        else:
            await bet_for_myself(message)


async def start_bet(message: discord.Message):
    global is_bet_started

    def check_message(received_message):
        return received_message.author == message.author and received_message.channel == message.channel

    if not check_user_registered_firebase(message.author.id):
        await message.channel.send(f"{message.author.display_name}, você ainda não possui registro, digite !register primeiro.")
        return

    if is_bet_started:
        await message.channel.send("Já existe uma bet ativa no momento, espere o final ou reclame com o dev que não escalou a aplicação direito por preguiça.")
        return
    else:
        await bet_for_registered_user(check_message, message)


async def bet_for_registered_user(check_message, message):
    try:
        await message.channel.send(f"{message.author.display_name}, para quem deseja startar bet (nick da conta)?")

        player_response = await client.wait_for(EVENT_MESSAGE, timeout=60, check=check_message)
        search_response = get_account_by_name(player_response.content)
        search_response_length = len(search_response)

        if search_response_length == 0:
            await message.channel.send(f"Não foi encontrado ninguém com esse nick no banco de dados")
        elif search_response_length >= 2:
            await message.channel.send("Usuário duplicado no banco de dados, por enquanto não suportamos essa função")
        elif search_response_length == 1:
            await handle_bet_for_specific_player_found(message, search_response)

    except asyncio.TimeoutError:
        await message.channel.send(TIMEOUT_MESSAGE)


async def handle_bet_for_specific_player_found(message, search_response):
    global is_bet_started
    player_name = search_response[0]["account"]["player_name"]
    player_tag = search_response[0]["account"]["player_tag"]
    player_puuid = search_response[0]["account"]["puuid"]
    await message.channel.send(f"Começando bet para {player_name}#{player_tag}")
    spectate_result = spectate_live_game(player_puuid)
    game_id = 0
    if spectate_result is not None:
        game_id = spectate_result["gameId"]
        await message.channel.send("Partida encontrada!")
        is_bet_started = True
        checked_game_id = 0

        await handle_bet_view(message=message, player_name=player_name, puuid=player_puuid)

        await asyncio.sleep(60)
        while is_bet_started:
            spectate_result = spectate_live_game(player_puuid)
            if spectate_result is not None:
                checked_game_id = spectate_result["gameId"]
            if spectate_result is None or checked_game_id != game_id:
                is_bet_started = False
                await message.channel.send("Partida finalizada!")
            else:
                print("Partida em andamento.")
                await asyncio.sleep(60)
    else:
        is_bet_started = False
        await message.channel.send("Partida não encontrada ou já finalizada!")

    if game_id != 0:
        match_result = check_match_result(game_id)
        for participant in match_result["info"]["participants"]:
            if participant["puuid"] == player_puuid:
                result = participant["win"]
                if result:
                    await message.channel.send(f"Jogador {player_name}#{player_tag} venceu a partida!")
                else:
                    await message.channel.send(f"Jogador {player_name}#{player_tag} perdeu a partida.")


def randomize_lost_joke():
    jokes = [
        ""
    ]
    chosen_joke = []
    return chosen_joke


def randomize_win_joke():
    jokes = [
        ""
    ]
    chosen_joke = []
    return chosen_joke


async def handle_bet_view(message, player_name, puuid):
    match_results = retrieve_win_rate(puuid=puuid)
    flex_rate = 0
    solo_rate = 0
    for entry in match_results:
        if entry["queueType"] == "RANKED_FLEX_SR":
            flex_wins = entry["wins"]
            flex_losses = entry["losses"]
            flex_rate = flex_wins / (flex_wins + flex_losses) * 100
        if entry["queueType"] == "RANKED_SOLO_5x5":
            solo_wins = entry["wins"]
            solo_losses = entry["losses"]
            solo_rate = solo_wins / (solo_wins + solo_losses) * 100

    house_edge = 0.95
    prob_win = solo_rate / 100
    prob_lose = 1 - prob_win

    odd_win = round((1 / prob_win) * house_edge, 2)
    odd_lose = round((1 / prob_lose) * house_edge, 2)

    description = f"""
    **Player:** {player_name}
    **Flex Win Rate:** {flex_rate:.2f}%
    **Solo Win Rate:** {solo_rate:.2f}%
    **Odds Win:** {odd_win:.2f}
    **Odds Lose:** {odd_lose:.2f}
    """
    await send_embed_message(message, "Estatísticas de jogador", description, discord.Color.blue())


async def register_player(message: discord.Message):
    def check_message(received_message):
        return received_message.author == message.author and received_message.channel == message.channel

    if check_user_registered_firebase(message.author.id):
        await message.channel.send(f"{message.author.display_name}, já possui registro.")
        return
    else:
        response_name = None
        response_tag = None
        riot_data = None

        try:
            account_verified = False
            while not account_verified:
                await message.channel.send(f"{message.author.display_name}, digite seu nick da main no lol (sem a tag)")
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
        await message.channel.send(
            f"{message.author.display_name}, você ainda não possui registro, digite !register primeiro!.")
        return

    user_points = get_user_points_firebase(message.author.id)
    if user_points == 0:
        await send_embed_message(message, "Pontos", f"Seu total de pontos é: {user_points}", discord.Color.red())

    elif user_points != 0:
        await send_embed_message(message, "Pontos", f"Seu total de pontos é: {user_points}", discord.Color.green())


async def display_commands(message: discord.Message):
    title = "Comandos"
    description = """
    **!gb_commands:** Comandos gerais do BOT
    **!register:** Se registrar no sistema pela primeira vez
    **!balance:** Saber quantos pontos você tem para apostar
    **!start:** Começar o sistema de bet para algum player registrado
    **!self:** Começar o sistema de bet para sua conta
    **!ranking:** Exibe o ranking de pontuação dos membros da season
    """
    color = discord.Color.blue()
    await send_embed_message(message, title, description, color)


async def send_embed_message(message, title, description, color, content=None, view=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    await message.channel.send(embed=embed, content=content, view=view)


client.run(DISCORD_TOKEN)