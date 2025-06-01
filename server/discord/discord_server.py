import asyncio
import discord

from constants import Constants
from exceptions import GalgosBetException
from functions import (
    extract_number_as_int,
    extract_bettor_side,
    extract_win_or_lose,
    extract_winners_and_losers,
)
from modal.account_modal import AccountModal
from modal.bet_modal import BetModal
from modal.statistics_modal import StatisticsModal
from modal.tournament_modal import TournamentModal
from modal.user_modal import UserModal
from server.firebase.firebase_server import (
    init_firebase,
    save_user_firebase,
    get_user_points_firebase,
    check_user_registered_firebase,
    get_account_by_name,
    get_account_by_id,
    get_points_ranking,
    get_user_by_id,
    add_user_account,
    add_points_to_user,
    remove_points_to_user,
    save_tournament_firebase,
    get_tournaments_firebase,
    update_tournament_firebase,
    add_bankruptcy_and_points_to_user,
)
from server.riot.riot_server import (
    return_account_information,
    spectate_live_game,
    check_match_result,
    retrieve_win_rate,
)

intents = discord.Intents.all()
client = discord.Client(intents=intents)
is_bet_started = False
is_bet_period_available = False
bet_modal = None
statistics_modal = None
bettors_list = []
bet_list = []
total_won = 0
total_lost = 0
players_lost = []
players_won = []


@client.event
async def on_ready():
    init_firebase()
    print(Constants.Prints.PRINT_APPLICATION_ALIVE)


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

    elif message.content.startswith(Constants.Commands.COMMAND_BET_VALUE):
        print(Constants.Prints.PRINT_BET_VALUE)
        await add_bet_value(message, message.content)

    elif message.content.startswith(Constants.Commands.COMMAND_BET_VALUE_ALL_IN):
        print(Constants.Prints.PRINT_BET_VALUE_ALL_IN)
        await add_bet_all_in(message, message.content)

    elif message.content.startswith(Constants.Commands.COMMAND_LOAD):
        print(Constants.Prints.PRINT_LOAD)
        await player_load(message)


async def player_load(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(
            f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}"
        )
        return

    user_points = get_user_points_firebase(message.author.id)
    if user_points != 0:
        await message.channel.send(
            f"{message.author.display_name}{Constants.Load.HAVE_POINTS}"
        )
        return

    await message.channel.send(
        f"{message.author.display_name}{Constants.Load.SUPPORTIVE}"
    )

    try:
        add_bankruptcy_and_points_to_user(message.author.id)
        add_points_to_user(message.author.id, 25)

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.JOIN_EXCEPTION}{str(exception)}")


async def add_bet_all_in(message: discord.Message, content: str):
    if not await is_user_registered(message):
        await message.channel.send(
            f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}"
        )
        return

    user_points = get_user_points_firebase(message.author.id)
    if user_points == 0:
        await message.channel.send(
            f"{message.author.display_name}{Constants.Join.NOT_ENOUGH_POINTS}"
        )
        return

    global is_bet_period_available, bettors_list, statistics_modal, bet_list, bet_modal

    def check_message(received_message):
        return (
            received_message.author == message.author
            and received_message.channel == message.channel
        )

    if is_bet_period_available:
        user_points = get_user_points_firebase(message.author.id)
        bet_value = round(user_points)

        if bet_value > 0:
            side = extract_bettor_side(content)
            is_win: bool

            if side is None:
                await message.channel.send(Constants.BetValue.NO_SIDE)
                await message.channel.send(Constants.BetValue.WHICH_SIDE)

                response = await client.wait_for(
                    Constants.Generic.EVENT_MESSAGE, timeout=15, check=check_message
                )

                win_or_lose = extract_win_or_lose(response)

                if win_or_lose is None:
                    await message.channel.send(Constants.BetValue.BET_CANCELED)
                    return

                if win_or_lose and isinstance(statistics_modal, StatisticsModal):
                    is_win = True
                    possible_win = round(bet_value * statistics_modal.odd_win) * 2

                elif not win_or_lose and isinstance(statistics_modal, StatisticsModal):
                    is_win = False
                    possible_win = round(bet_value * statistics_modal.odd_lose) * 2

                else:
                    raise GalgosBetException(Constants.Errors.ERROR_ADD_BET)

            else:
                if side and isinstance(statistics_modal, StatisticsModal):
                    is_win = True
                    possible_win = round(bet_value * statistics_modal.odd_win) * 2

                elif not side and isinstance(statistics_modal, StatisticsModal):
                    is_win = False
                    possible_win = round(bet_value * statistics_modal.odd_lose) * 2

                else:
                    raise GalgosBetException(Constants.Errors.ERROR_ADD_BET)

            bet_modal = BetModal(
                bet_value=round(bet_value, 0),
                bettor=message.author.display_name,
                bettor_id=message.author.id,
                win=is_win,
                possible_win=possible_win,
            )

            bet_list.append(bet_modal)

            await message.channel.send(
                f"{message.author.display_name}{Constants.BetValue.BET_SUCCESS}"
            )

            description = f"""
            {Constants.BetValue.DESCRIPTION_ALL_IN}
            {Constants.BetValue.DESCRIPTION_VALUE}{bet_value}
            {Constants.BetValue.DESCRIPTION_IS_WIN}{is_win}
            {Constants.BetValue.DESCRIPTION_ODD_WIN}{statistics_modal.odd_win}
            {Constants.BetValue.DESCRIPTION_ODD_LOSE}{statistics_modal.odd_lose}
            {Constants.BetValue.DESCRIPTION_WIN_POSSIBILITY}{possible_win}
            """

            await send_embed_message(
                message,
                f"{Constants.BetValue.RECEIPT_TITLE}{message.author.display_name}",
                description,
                Constants.Colors.PURPLE,
            )

    else:
        await message.channel.send(Constants.BetValue.NO_BET_AVAILABLE)


async def add_bet_value(message: discord.Message, content: str):
    if not await is_user_registered(message):
        await message.channel.send(
            f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}"
        )
        return

    user_points = get_user_points_firebase(message.author.id)
    if user_points == 0:
        await message.channel.send(
            f"{message.author.display_name}{Constants.Join.NOT_ENOUGH_POINTS}"
        )
        return

    global is_bet_period_available, bettors_list, statistics_modal, bet_list, bet_modal

    def check_message(received_message):
        return (
            received_message.author == message.author
            and received_message.channel == message.channel
        )

    if is_bet_period_available:
        user_points = get_user_points_firebase(message.author.id)
        bet_value = extract_number_as_int(content)

        if 0 < bet_value <= user_points:
            side = extract_bettor_side(content)
            is_win: bool

            if side is None:
                await message.channel.send(Constants.BetValue.NO_SIDE)
                await message.channel.send(Constants.BetValue.WHICH_SIDE)

                response = await client.wait_for(
                    Constants.Generic.EVENT_MESSAGE, timeout=15, check=check_message
                )

                win_or_lose = extract_win_or_lose(response)

                if win_or_lose is None:
                    await message.channel.send(Constants.BetValue.BET_CANCELED)
                    return

                if win_or_lose and isinstance(statistics_modal, StatisticsModal):
                    is_win = True
                    possible_win = round(bet_value * statistics_modal.odd_win)

                elif not win_or_lose and isinstance(statistics_modal, StatisticsModal):
                    is_win = False
                    possible_win = round(bet_value * statistics_modal.odd_lose)

                else:
                    raise GalgosBetException(Constants.Errors.ERROR_ADD_BET)

            else:
                if side and isinstance(statistics_modal, StatisticsModal):
                    is_win = True
                    possible_win = round(bet_value * statistics_modal.odd_win)

                elif not side and isinstance(statistics_modal, StatisticsModal):
                    is_win = False
                    possible_win = round(bet_value * statistics_modal.odd_lose)

                else:
                    raise GalgosBetException(Constants.Errors.ERROR_ADD_BET)

            bet_modal = BetModal(
                bet_value=round(bet_value, 0),
                bettor=message.author.display_name,
                bettor_id=message.author.id,
                win=is_win,
                possible_win=possible_win,
            )

            bet_list.append(bet_modal)

            await message.channel.send(
                f"{message.author.display_name}{Constants.BetValue.BET_SUCCESS}"
            )

            description = f"""
            {Constants.BetValue.DESCRIPTION_VALUE}{bet_value}
            {Constants.BetValue.DESCRIPTION_IS_WIN}{is_win}
            {Constants.BetValue.DESCRIPTION_ODD_WIN}{statistics_modal.odd_win}
            {Constants.BetValue.DESCRIPTION_ODD_LOSE}{statistics_modal.odd_lose}
            {Constants.BetValue.DESCRIPTION_WIN_POSSIBILITY}{possible_win}
            """

            await send_embed_message(
                message,
                f"{Constants.BetValue.RECEIPT_TITLE}{message.author.display_name}",
                description,
                Constants.Colors.PURPLE,
            )

        else:
            await message.channel.send(Constants.BetValue.INCORRECT_BET_VALUE)

    else:
        await message.channel.send(Constants.BetValue.NO_BET_AVAILABLE)


async def add_account(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(
            f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}"
        )
        return

    def check_message(received_message):
        return (
            received_message.author == message.author
            and received_message.channel == message.channel
        )

    try:
        response_name = None
        response_tag = None
        riot_data = None
        account_verified = False

        while not account_verified:
            await message.channel.send(
                f"{message.author.display_name}{Constants.AddAccount.REGISTER_NICK}"
            )
            response_name = await client.wait_for(
                Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message
            )

            await message.channel.send(Constants.AddAccount.REGISTER_TAG)
            response_tag = await client.wait_for(
                Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message
            )

            riot_data = return_account_information(
                response_name.content, response_tag.content
            )

            if riot_data is None:
                await message.channel.send(Constants.Register.RIOT_ACCOUNT_NOT_FOUND)
            else:
                account_verified = True

        secondary_account = AccountModal(
            player_name=response_name.content,
            player_tag=response_tag.content,
            main=False,
            puuid=riot_data[Constants.Generic.PUUID],
        )

        add_user_account(message.author.id, secondary_account)

        await message.channel.send(Constants.AddAccount.REGISTERED)

    except GalgosBetException:
        raise GalgosBetException(Constants.Errors.ADD_ACCOUNT_ERROR)


async def try_joining(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(
            f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}"
        )
        return

    user_points = get_user_points_firebase(message.author.id)
    if user_points == 0:
        await message.channel.send(
            f"{message.author.display_name}{Constants.Join.NOT_ENOUGH_POINTS}"
        )
        return

    global is_bet_period_available, bettors_list

    if await check_bet_started(message, False) and is_bet_period_available:
        try:
            user = get_user_by_id(message.author.id)
            bettors_list.append(user)

            points = get_user_points_firebase(message.author.id)

            await message.channel.send(
                f"{message.author.display_name}{Constants.Join.YOUR_BALANCE_START}{str(round(points))}{Constants.Join.YOUR_BALANCE_END}"
            )

        except Exception as exception:
            raise GalgosBetException(
                f"{Constants.Errors.JOIN_EXCEPTION}{str(exception)}"
            )

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
            description += (
                f"**{i}. {name}** — {round(points)} {Constants.Generic.POINTS_PTBR}\n"
            )
        await send_embed_message(
            message, Constants.Ranking.RANKING, description, Constants.Colors.PURPLE
        )
    except Exception as exception:
        raise GalgosBetException(
            f"{Constants.Errors.RANKING_EXCEPTION}{str(exception)}"
        )


async def bet_for_myself(message):
    try:
        accounts = get_account_by_id(message.author.id)
        accounts_length = len(accounts)

        if accounts_length == 0:
            await message.channel.send(Constants.SelfBet.NOT_FOUND)
        elif accounts_length >= 2:
            await handle_bet_for_multiple_player_accounts_found(message, accounts)
        elif accounts_length == 1:
            await handle_bet_for_specific_player_found(message, accounts)

    except asyncio.TimeoutError:
        await message.channel.send(Constants.Errors.TIMEOUT_MESSAGE)


async def handle_bet_for_multiple_player_accounts_found(message, accounts):
    try:
        for account in accounts:
            player_puuid = account[Constants.Generic.ACCOUNT][Constants.Generic.PUUID]

            spectate_result = spectate_live_game(player_puuid)

            if spectate_result is not None:
                await handle_bet_for_specific_player_found(message, account)
                print(Constants.Prints.PRINT_ACCOUNT_FOUND)

        await message.channel.send(Constants.BetSystem.LIVE_MATCH_NOT_FOUND)

    except Exception as exception:
        raise GalgosBetException(
            f"{Constants.Errors.MULTIPLE_SELF_BET_ERROR}{str(exception)}"
        )


async def start_self_bet(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(
            f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}"
        )
        return

    if await check_bet_started(message):
        return

    await bet_for_myself(message)


async def is_user_registered(message: discord.Message) -> bool:
    if check_user_registered_firebase(message.author.id):
        return True

    return False


async def check_bet_started(message: discord.Message, lazy_message=True):
    global is_bet_started

    if is_bet_started:
        if lazy_message:
            await message.channel.send(Constants.Functions.LAZY_DEV)
        return True
    return False


async def start_bet(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(
            f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}"
        )
        return

    if await check_bet_started(message):
        return

    await bet_for_registered_user(message)


async def bet_for_registered_user(message):
    def check_message(received_message):
        return (
            received_message.author == message.author
            and received_message.channel == message.channel
        )

    try:
        await message.channel.send(
            f"{message.author.display_name}{Constants.Bet.WHO_START}"
        )

        player_response = await client.wait_for(
            Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message
        )
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
    global statistics_modal, total_won, total_lost, bet_list, bettors_list
    global is_bet_started, is_bet_period_available, bet_modal
    player_name = search_response[0][Constants.Generic.ACCOUNT][
        Constants.Generic.PLAYER_NAME
    ]
    player_tag = search_response[0][Constants.Generic.ACCOUNT][
        Constants.Generic.PLAYER_TAG
    ]
    player_puuid = search_response[0][Constants.Generic.ACCOUNT][
        Constants.Generic.PUUID
    ]

    await message.channel.send(
        f"{Constants.BetSystem.STARTING_BET}{player_name}{Constants.Generic.HASHTAG}{player_tag}"
    )

    spectate_result = spectate_live_game(player_puuid)
    game_id = 0
    checked_game_id = 0
    game_had_result = False

    if spectate_result is not None:
        game_id = spectate_result[Constants.Generic.GAME_ID]
        is_bet_started = True

        await message.channel.send(Constants.BetSystem.MATCH_FOUND)

        await handle_bet_view(
            message=message, player_name=player_name, puuid=player_puuid
        )

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
        bet_win, bet_lose = extract_winners_and_losers(bet_list)

        for participant in match_result[Constants.Generic.INFORMATION][
            Constants.Generic.PARTICIPANTS
        ]:

            if participant[Constants.Generic.PUUID] == player_puuid:
                result = participant[Constants.Generic.WIN]
                game_had_result = True

                tournament_data = get_tournaments_firebase()

                if result:
                    handle_bet_won(bet_win, tournament_data)
                    handle_bet_lost(bet_lose, tournament_data)
                    await message.channel.send(
                        f"{Constants.BetSystem.PLAYER}{player_name}{Constants.Generic.HASHTAG}{player_tag}{Constants.BetSystem.PLAYER_WON}"
                    )

                else:
                    handle_bet_won(bet_lose, tournament_data)
                    handle_bet_lost(bet_win, tournament_data)
                    await message.channel.send(
                        f"{Constants.BetSystem.PLAYER}{player_name}{Constants.Generic.HASHTAG}{player_tag}{Constants.BetSystem.PLAYER_LOST}"
                    )

        await message.channel.send(Constants.BetSystem.REDISTRIBUTED_POINTS)

        if game_had_result:
            total_value = 0
            for bet in bet_list:
                total_value += bet.bet_value

            description = f"""
                    {Constants.BetSystem.BET_ENDED_DESCRIPTION_TOTAL_BETS}{len(bet_list)}
                    {Constants.BetSystem.BET_ENDED_DESCRIPTION_TOTAL_VALUE}{total_value}
                    {Constants.BetSystem.BET_ENDED_DESCRIPTION_TOTAL_BETS_WON}{len(players_won)}
                    {Constants.BetSystem.BET_ENDED_DESCRIPTION_TOTAL_BETS_LOST}{len(players_lost)}
                    {Constants.BetSystem.BET_ENDED_DESCRIPTION_TOTAL_VALUE_WON}{total_won}
                    {Constants.BetSystem.BET_ENDED_DESCRIPTION_TOTAL_VALUE_LOST}{total_lost}
                    {Constants.BetSystem.BET_ENDED_DESCRIPTION_TOTAL_PLAYERS_WON}{Constants.Generic.COLMA_SPACE.join(players_won)}
                    {Constants.BetSystem.BET_ENDED_DESCRIPTION_TOTAL_PLAYERS_LOST}{Constants.Generic.COLMA_SPACE.join(players_lost)}
                    """

            await send_embed_message(
                message,
                Constants.BetSystem.BET_ENDED_TITLE,
                description,
                Constants.Colors.RED,
            )

        reset_global()


def reset_global():
    global is_bet_started, is_bet_period_available, bet_modal, statistics_modal, bet_list, bettors_list, total_won, total_lost, players_lost, players_won
    is_bet_started = False
    is_bet_period_available = False
    bet_modal = None
    statistics_modal = None
    bettors_list = []
    bet_list = []
    total_won = 0
    total_lost = 0
    players_lost = []
    players_won = []
    print(Constants.Prints.PRINT_GLOBAL_RESET)


def handle_bet_won(
    bet_won_list: list[BetModal], tournament_data: list[TournamentModal]
):
    global total_won, players_won

    for bet in bet_won_list:
        value_to_add = bet.possible_win - bet.bet_value
        add_points_to_user(bet.bettor_id, value_to_add)

        total_won += bet.possible_win - bet.bet_value
        players_won.append(bet.bettor)

        for tournament in tournament_data:
            if tournament.user_id == bet.bettor_id:
                update_tournament_firebase(bet.bettor_id, True)
                break


def handle_bet_lost(
    bet_lost_list: list[BetModal], tournament_data: list[TournamentModal]
):
    global total_lost, players_lost

    for bet in bet_lost_list:
        remove_points_to_user(bet.bettor_id, bet.bet_value)
        total_lost += bet.bet_value
        players_lost.append(bet.bettor)

        for tournament in tournament_data:
            if tournament.user_id == bet.bettor_id:
                update_tournament_firebase(bet.bettor_id, False)
                break


async def handle_bet_view(message, player_name, puuid):
    global statistics_modal

    match_results = retrieve_win_rate(puuid=puuid)
    flex_rate = 0
    solo_rate = 0
    flex_games = 0
    solo_games = 0
    flex_wins = 0
    flex_losses = 0
    solo_wins = 0
    solo_losses = 0

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

    if prob_win == 0:
        prob_win = 1

    if prob_lose == 0:
        prob_lose = 1

    odd_win = round((1 / prob_win) * house_edge, 2)
    odd_lose = round((1 / prob_lose) * house_edge, 2)

    description = f"""
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_PLAYER_NAME}{player_name}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_SOLO_TOTAL_GAMES}{solo_games}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_SOLO_WIN_RATE}{solo_rate:.2f}{Constants.Generic.PERCENTAGE}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_FLEX_TOTAL_GAMES}{flex_games}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_SEASON_TOTAL_GAMES}{solo_games + flex_games}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_FLEX_WIN_RATE}{flex_rate:.2f}{Constants.Generic.PERCENTAGE}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_ODDS_WIN}{odd_win:.2f}
    {Constants.BetSystem.BET_VIEW_DESCRIPTION_ODDS_LOSE}{odd_lose:.2f}
    """

    await send_embed_message(
        message, Constants.BetSystem.BET_VIEW_TITLE, description, Constants.Colors.BLUE
    )

    statistics_modal = StatisticsModal(
        flex_win_rate=flex_rate,
        flex_wins=flex_wins,
        flex_losses=flex_losses,
        flex_games=flex_games,
        solo_win_rate=solo_rate,
        solo_wins=solo_wins,
        solo_losses=solo_losses,
        solo_games=solo_games,
        odd_win=odd_win,
        odd_lose=odd_lose,
    )


async def register_player(message: discord.Message):
    def check_message(received_message):
        return (
            received_message.author == message.author
            and received_message.channel == message.channel
        )

    if await is_user_registered(message):
        await message.channel.send(
            f"{message.author.display_name}{Constants.Functions.ALREADY_REGISTERED}"
        )
        return

    response_name = None
    response_tag = None
    riot_data = None

    try:
        account_verified = False

        while not account_verified:
            await message.channel.send(
                f"{message.author.display_name}{Constants.Register.REGISTER_NICK}"
            )
            response_name = await client.wait_for(
                Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message
            )

            await message.channel.send(Constants.Register.REGISTER_TAG)
            response_tag = await client.wait_for(
                Constants.Generic.EVENT_MESSAGE, timeout=60, check=check_message
            )

            riot_data = return_account_information(
                response_name.content, response_tag.content
            )

            if riot_data is None:
                await message.channel.send(Constants.Register.RIOT_ACCOUNT_NOT_FOUND)
            else:
                account_verified = True

        main_account = AccountModal(
            player_name=response_name.content,
            player_tag=response_tag.content,
            main=True,
            puuid=riot_data[Constants.Generic.PUUID],
        )

        user = UserModal(
            user_id=message.author.id,
            name=message.author.name,
            nick=message.author.nick,
            accounts=[main_account],
            registered=True,
            points=100.0,
        )

        tournament = TournamentModal(
            user_id=message.author.id,
            user_name=message.author.name,
        )

        save_user_firebase(user)

        save_tournament_firebase(tournament)

        await message.channel.send(Constants.Register.REGISTERED)

    except asyncio.TimeoutError:
        await message.channel.send(Constants.Errors.TIMEOUT_MESSAGE)


async def get_points_balance(message: discord.Message):
    if not await is_user_registered(message):
        await message.channel.send(
            f"{message.author.display_name}{Constants.Functions.NOT_REGISTERED}"
        )
        return

    try:
        user_points = get_user_points_firebase(message.author.id)
        if user_points == 0:
            await send_embed_message(
                message,
                Constants.Balance.VIEW_TITLE,
                f"{Constants.Balance.VIEW_TOTAL_POINTS}{user_points}",
                Constants.Colors.RED,
            )

        elif user_points != 0:
            await send_embed_message(
                message,
                Constants.Balance.VIEW_TITLE,
                f"{Constants.Balance.VIEW_TOTAL_POINTS}{user_points}",
                Constants.Colors.GREEN,
            )

    except GalgosBetException as exception:
        raise GalgosBetException(
            f"{Constants.Errors.BALANCE_EXCEPTION}{str(exception)}"
        )


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
    {Constants.CommandsView.BET_VALUE}
    {Constants.CommandsView.BET_VALUE_ALL_IN}
    {Constants.CommandsView.LOAD}
    """
    await send_embed_message(
        message, Constants.CommandsView.TITLE, description, Constants.Colors.BLUE
    )


async def send_embed_message(
    message, title, description, color, content=None, view=None
):
    embed = discord.Embed(title=title, description=description, color=color)
    await message.channel.send(embed=embed, content=content, view=view)


async def initiate_bet(message: discord.Message):
    if not await check_bet_started(message, False):
        return

    global is_bet_period_available
    is_bet_period_available = True

    await send_embed_message(
        message,
        Constants.BetSystem.BET_PERIOD_AVAILABLE_TITLE,
        Constants.BetSystem.BET_PERIOD_AVAILABLE_DESCRIPTION,
        Constants.Colors.GREEN,
    )

    try:
        await asyncio.sleep(300)

    finally:
        is_bet_period_available = False
        await message.channel.send(Constants.BetSystem.BET_PERIOD_ENDED)


client.run(Constants.Discord.DISCORD_TOKEN)
