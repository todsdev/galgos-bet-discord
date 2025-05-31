import asyncio
import discord

from constants import Constants
from exceptions import GalgosBetException
from modal.account_modal import AccountModal
from modal.bet_modal import BetModal
from modal.user_modal import UserModal
from server.firebase.firebase_server import init_firebase, save_user_firebase, get_user_points_firebase, \
    check_user_registered_firebase, get_account_by_name, get_account_by_id, get_points_ranking, get_user_by_id, \
    add_user_account
from server.riot.riot_server import return_account_information, spectate_live_game, check_match_result, \
    retrieve_win_rate

intents = discord.Intents.all()
client = discord.Client(intents=intents)
is_bet_started = False
is_bet_period_available = False
bet_modal = BetModal
bettors_list: list[UserModal] = []

@client.event
async def on_ready():
    init_firebase()
    print(Constants.Prints.APPLICATION_ALIVE)

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith(Constants.Commands.COMMAND_REGISTER_PLAYER):
        print(Constants.Prints.PRINT_REGISTER_PLAYER)
        await register_player(message)

    elif message.content.startswith(Constants.Commands.COMMAND_BALANCE):
        print(Constants.Prints.PRINT_BALANCE)
        await get_points_balance(message)

    elif message.content.startswith(Constants.Commands.COMMAND_START_BET):
        print(Constants.Prints.PRINT_START)
        await start_bet(message)

    elif message.content.startswith(Constants.Commands.COMMAND_COMMANDS):
        print(Constants.Prints.PRINT_COMMANDS)
        await display_commands(message)

    elif message.content.startswith(Constants.Commands.COMMAND_RANKING):
        print(Constants.Prints.PRINT_RANKING)
        await get_ranking(message)

    elif message.content.startswith(Constants.Commands.COMMAND_SELF_BET):
        print(Constants.Prints.PRINT_SELF_START)
        await start_self_bet(message)

    elif message.content.startswith(Constants.Commands.COMMAND_JOIN):
        print(Constants.Prints.PRINT_TRYING_JOIN)
        await try_joining(message)

    elif message.content.startswith(Constants.Commands.COMMAND_ADD):
        print(Constants.Prints.PRINT_ADD_ACCOUNT)
        await add_account(message)

async def add_account(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}")
        return

    def check_message(received_message):
        return received_message.author == message.author and received_message.channel == message.channel

    try:
        response_name = None
        response_tag = None
        riot_data = None
        account_verified = False

        while not account_verified:
            await message.channel.send(f"{message.author.display_name}{Constants.AddAccount.REGISTER_NICK}")
            response_name = await client.wait_for(Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message)

            await message.channel.send(Constants.AddAccount.REGISTER_TAG)
            response_tag = await client.wait_for(Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message)

            riot_data = return_account_information(response_name.content, response_tag.content)

            if riot_data is None:
                await message.channel.send(Constants.Register.RIOT_ACCOUNT_NOT_FOUND)
            else:
                account_verified = True

        secondary_account = AccountModal(
            player_name=response_name.content,
            player_tag=response_tag.content,
            main=False,
            puuid=riot_data[Constants.Generic.PUUID]
        )

        add_user_account(message.author.id, secondary_account)

    except GalgosBetException:
        raise GalgosBetException(Constants.Errors.ADD_ACCOUNT_ERROR)

async def try_joining(message: discord.Message):
    global is_bet_period_available, bettors_list

    if await check_bet_started(message, False) and is_bet_period_available:
        try:
            user = get_user_by_id(message.author.id)
            bettors_list.append(user)

        except Exception as exception:
            raise GalgosBetException(f"{Constants.Errors.JOIN_EXCEPTION}{str(exception)}")

    else:
        await message.channel.send(Constants.Join.BET_NOT_FOUND)

async def get_ranking(message: discord.Message):
    try:
        ranking = get_points_ranking()
        if not ranking:
            raise GalgosBetException(Constants.Errors.RANKING_EXCEPTION_FIREBASE)

        description = Constants.Generic.EMPTY_STRING

        for i, player in enumerate(ranking[:20], start=1):
            name = player.get(Constants.Generic.PLAYER_NAME, Constants.Generic.UNKNOWN)
            points = player.get(Constants.Generic.POINTS, 0)
            description += f"**{i}. {name}** — {points} pontos\n"
        await send_embed_message(message, Constants.Ranking.RANKING, description, Constants.Colors.PURPLE)
    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.RANKING_EXCEPTION}{str(exception)}")

async def bet_for_myself(message):
    try:
        accounts = get_account_by_id(message.author.id)
        accounts_length = len(accounts)

        if accounts_length == 0:
            await message.channel.send(Constants.SelfBet.NOT_FOUND)
        elif accounts_length >= 2:
            await message.channel.send(Constants.SelfBet.DUPLICATED)
        elif accounts_length == 1:
            await handle_bet_for_specific_player_found(message, accounts)

    except asyncio.TimeoutError:
        await message.channel.send(Constants.Errors.TIMEOUT_MESSAGE)

async def start_self_bet(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}")
        return

    if await check_bet_started(message):
        return

    await bet_for_myself(message)

async def is_user_registered(message: discord.Message) -> bool:
    if check_user_registered_firebase(message.author.id):
        return True

    return False

async def check_bet_started(message: discord.Message, lazy_message = True):
    global is_bet_started

    if is_bet_started:
        if lazy_message:
            await message.channel.send(Constants.Functions.LAZY_DEV)
        return True
    return False

async def start_bet(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}")
        return

    if await check_bet_started(message):
        return

    await bet_for_registered_user(message)

async def bet_for_registered_user(message):
    def check_message(received_message):
        return received_message.author == message.author and received_message.channel == message.channel

    try:
        await message.channel.send(f"{message.author.display_name}{Constants.Bet.WHO_START}")

        player_response = await client.wait_for(Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message)
        search_response = get_account_by_name(player_response.content)
        search_response_length = len(search_response)

        if search_response_length == 0:
            await message.channel.send(Constants.Bet.NOT_FOUND)
        elif search_response_length >= 2:
            await message.channel.send(Constants.Bet.DUPLICATED)
        elif search_response_length == 1:
            await handle_bet_for_specific_player_found(message, search_response)
        else:
            raise GalgosBetException(Constants.Errors.UNKNOWN_SEARCH_RESPONSE)

    except asyncio.TimeoutError:
        await message.channel.send(Constants.Errors.TIMEOUT_MESSAGE)

async def handle_bet_for_specific_player_found(message, search_response):
    global is_bet_started
    player_name = search_response[0][Constants.Generic.ACCOUNT][Constants.Generic.PLAYER_NAME]
    player_tag = search_response[0][Constants.Generic.ACCOUNT][Constants.Generic.PLAYER_TAG]
    player_puuid = search_response[0][Constants.Generic.ACCOUNT][Constants.Generic.PUUID]

    await message.channel.send(f"{Constants.BetSystem.STARTING_BET}{player_name}{Constants.Generic.HASHTAG}{player_tag}")

    spectate_result = spectate_live_game(player_puuid)
    game_id = 0
    checked_game_id = 0

    if spectate_result is not None:
        game_id = spectate_result[Constants.Generic.GAME_ID]
        is_bet_started = True

        await message.channel.send(Constants.BetSystem.MATCH_FOUND)

        await handle_bet_view(message=message, player_name=player_name, puuid=player_puuid)

        await initiate_bet(message)

        await asyncio.sleep(60)

        while is_bet_started:
            spectate_result = spectate_live_game(player_puuid)

            if spectate_result is not None:
                checked_game_id = spectate_result[Constants.Generic.GAME_ID]

            if spectate_result is None or checked_game_id != game_id:
                is_bet_started = False
                await message.channel.send(Constants.BetSystem.MATCH_OVER)
            else:
                print(Constants.Prints.PRINT_MATCH_LIVE)
                await asyncio.sleep(60)

    else:
        is_bet_started = False
        await message.channel.send(Constants.BetSystem.MATCH_NOT_FOUND_OR_OVER)

    if game_id != 0:
        match_result = check_match_result(game_id)
        for participant in match_result[Constants.Generic.INFORMATION][Constants.Generic.PARTICIPANTS]:
            if participant[Constants.Generic.PUUID] == player_puuid:
                result = participant[Constants.Generic.WIN]
                if result:
                    await message.channel.send(f"{Constants.BetSystem.PLAYER}{player_name}{Constants.Generic.HASHTAG}{player_tag}{Constants.BetSystem.PLAYER_WON}")
                else:
                    await message.channel.send(f"{Constants.BetSystem.PLAYER}{player_name}{Constants.Generic.HASHTAG}{player_tag}{Constants.BetSystem.PLAYER_LOST}")

async def handle_bet_view(message, player_name, puuid):
    match_results = retrieve_win_rate(puuid=puuid)
    flex_rate = 0
    solo_rate = 0
    flex_games = 0
    solo_games = 0

    for entry in match_results:
        if entry[Constants.Generic.QUEUE_TYPE] == Constants.Generic.RANKED_FLEX:
            flex_wins = entry[Constants.Generic.WINS]
            flex_losses = entry[Constants.Generic.LOSSES]
            flex_rate = flex_wins / (flex_wins + flex_losses) * 100
            flex_games = flex_wins + flex_losses

        if entry[Constants.Generic.QUEUE_TYPE] == Constants.Generic.RANKED_SOLO:
            solo_wins = entry[Constants.Generic.WINS]
            solo_losses = entry[Constants.Generic.LOSSES]
            solo_rate = solo_wins / (solo_wins + solo_losses) * 100
            solo_games = solo_wins + solo_losses

    house_edge = 0.95
    prob_win = solo_rate / 100
    prob_lose = 1 - prob_win

    odd_win = round((1 / prob_win) * house_edge, 2)
    odd_lose = round((1 / prob_lose) * house_edge, 2)

    description = f"""
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_PLAYER_NAME}{player_name}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_SOLO_TOTAL_GAMES}{solo_games}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_SOLO_WIN_RATE}{solo_rate:.2f}{Constants.Generic.PERCENTAGE}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_FLEX_TOTAL_GAMES}{flex_games}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_FLEX_WIN_RATE}{flex_rate:.2f}{Constants.Generic.PERCENTAGE}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_ODDS_WIN}{odd_win:.2f}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_ODDS_LOSE}{odd_lose:.2f}
    """

    await send_embed_message(message, Constants.BetSystem.BET_VIEW_TITLE, description, Constants.Colors.BLUE)

async def register_player(message: discord.Message):
    def check_message(received_message):
        return received_message.author == message.author and received_message.channel == message.channel

    if await is_user_registered(message):
        await message.channel.send(f"{message.author.display_name}{Constants.Functions.ALREADY_REGISTERED}")
        return

    response_name = None
    response_tag = None
    riot_data = None

    try:
        account_verified = False

        while not account_verified:
            await message.channel.send(f"{message.author.display_name}{Constants.Register.REGISTER_NICK}")
            response_name = await client.wait_for(Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message)

            await message.channel.send(Constants.Register.REGISTER_TAG)
            response_tag = await client.wait_for(Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message)

            riot_data = return_account_information(response_name.content, response_tag.content)

            if riot_data is None:
                await message.channel.send(Constants.Register.RIOT_ACCOUNT_NOT_FOUND)
            else:
                account_verified = True

        main_account = AccountModal(
            player_name=response_name.content,
            player_tag=response_tag.content,
            main=True,
            puuid=riot_data[Constants.Generic.PUUID]
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

        await message.channel.send(Constants.Register.REGISTERED)

    except asyncio.TimeoutError:
        await message.channel.send(Constants.Errors.TIMEOUT_MESSAGE)

async def get_points_balance(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}")
        return

    try:
        user_points = get_user_points_firebase(message.author.id)
        if user_points == 0:
            await send_embed_message(message, Constants.Balance.VIEW_TITLE, f"{Constants.Balance.VIEW_TOTAL_POINTS}{user_points}", Constants.Colors.RED)

        elif user_points != 0:
            await send_embed_message(message, Constants.Balance.VIEW_TITLE, f"{Constants.Balance.VIEW_TOTAL_POINTS}{user_points}", Constants.Colors.GREEN)

    except GalgosBetException as exception:
        raise GalgosBetException(f"{Constants.Errors.BALANCE_EXCEPTION}{str(exception)}")

async def display_commands(message: discord.Message):
    description = f"""
    {Constants.CommandsView.GB_COMMANDS}
    {Constants.CommandsView.REGISTER}
    {Constants.CommandsView.BALANCE}
    {Constants.CommandsView.START}
    {Constants.CommandsView.SELF}
    {Constants.CommandsView.RANKING}
    {Constants.CommandsView.JOIN}
    {Constants.CommandsView.ADD}
    """
    await send_embed_message(message, Constants.CommandsView.TITLE, description, Constants.Colors.BLUE)

async def send_embed_message(message, title, description, color, content=None, view=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    await message.channel.send(embed=embed, content=content, view=view)

async def initiate_bet(message: discord.Message):
    if not await check_bet_started(message, False):
        return

    global is_bet_period_available
    is_bet_period_available = True

    await send_embed_message(message, Constants.BetSystem.BET_PERIOD_AVAILABLE_TITLE, Constants.BetSystem.BET_PERIOD_AVAILABLE_DESCRIPTION, Constants.Colors.GREEN)

    try:
        await asyncio.sleep(120)

    finally:
        is_bet_period_available = False
        await message.channel.send(Constants.BetSystem.BET_PERIOD_ENDED)


client.run(Constants.Discord.DISCORD_TOKEN)