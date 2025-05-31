import discord


class Constants:
    class Generic:
        EMPTY_STRING = ""
        UNKNOWN = "Desconhecido"
        PLAYER_NAME = "player_name"
        PLAYER_TAG = "player_tag"
        PUUID = "puuid"
        POINTS = "points"
        ACCOUNT = "account"
        GAME_ID = "gameId"
        EVENT_MESSAGE = "message"
        HASHTAG = "#"
        PERCENTAGE = "%"
        INFORMATION = "info"
        PARTICIPANTS = "participants"
        WIN = "win"
        WINS = "wins"
        LOSSES = "losses"
        QUEUE_TYPE = "queueType"
        RANKED_FLEX = "RANKED_FLEX_SR"
        RANKED_SOLO = "RANKED_SOLO_5x5"

    class Riot:
        RIOT_API_TOKEN = "RGAPI-40348c6b-a483-41e0-a2ec-a6dc25a29787"
        RIOT_PLATFORM = "br1"
        RIOT_REGION = "americas"

    class Discord:
        DISCORD_TOKEN = "MTM3MDM3OTg3NTE4NTA2NjAwNA.G4aApZ.Hhv9M5_1kR-mKf6JAFX7eSPIlMfgtmhkV6MDdM"

    class Firebase:
        FIREBASE_DATABASE_URL = "https://galgos-bet-discord-default-rtdb.firebaseio.com/"
        USER_REF_FIREBASE_DATABASE = "users"
        USER_REF_ACCOUNTS_FIREBASE_DATABASE = "accounts"
        USER_REF_POINTS_FIREBASE_DATABASE = "points"
        USER_REF_PLAYER_NAME_FIREBASE_DATABASE = "player_name"

    class Commands:
        COMMAND_REGISTER_PLAYER = "!register"
        COMMAND_RANKING = "!ranking"
        COMMAND_BALANCE = "!balance"
        COMMAND_START_BET = "!start"
        COMMAND_SELF_BET = "!self"
        COMMAND_COMMANDS = "!gb_commands"

    class CommandsView:
        GB_COMMANDS = "**!gb_commands:** Comandos gerais do BOT"
        REGISTER = "**!register:** Se registrar no sistema pela primeira vez"
        BALANCE = "**!balance:** Saber quantos pontos você tem para apostar"
        START = "**!start:** Começar o sistema de bet para algum player registrado"
        SELF = "**!self:** Começar o sistema de bet para sua conta"
        RANKING = "**!ranking:** Exibe o ranking de pontuação dos membros da season"
        TITLE = "Comandos"

    class Errors:
        TIMEOUT_MESSAGE = "Demorou demais!"
        GALGOS_EXCEPTION = "Ocorreu um erro no sistema de apostas dos Galgos"
        RANKING_EXCEPTION = "Ocorreu um erro ao recuperar ranking de pontos :"
        BALANCE_EXCEPTION = "Ocorreu um erro ao recuperar balance de pontos :"
        RANKING_EXCEPTION_FIREBASE = "Ocorreu um erro ao recuperar pontos do Firebase"
        UNKNOWN_SEARCH_RESPONSE = "Search response não foi recuperado no formato ideal"

    class Prints:
        PRINT_REGISTER_PLAYER = "Start player registering for first time"
        PRINT_BALANCE = "Displaying player points balance"
        PRINT_START = "Start player bet"
        PRINT_COMMANDS = "Displaying commands"
        PRINT_RANKING = "Displaying players points ranking"
        PRINT_SELF_START = "Start self player bet"
        MATCH_LIVE = "Partida em andamento"

    class Ranking:
        RANKING = "Ranking"

    class SelfBet:
        NOT_FOUND = "Não foi encontrado ninguém com esse nome no banco de dados"
        DUPLICATED = "Seu usuário está duplicado no banco de dados, por enquanto não suportamos essa função"

    class Bet:
        WHO_START = ", para quem deseja começar bet (nome da conta)?"
        NOT_FOUND = "Não foi encontrado ninguém com esse nome no banco de dados"
        DUPLICATED = "Jogador duplicado no banco de dados, por enquanto não suportamos essa função"

    class BetSystem:
        STARTING_BET = "Começando bet para "
        MATCH_FOUND = "Partida encontrada"
        MATCH_OVER = "Partida finalizada"
        MATCH_NOT_FOUND_OR_OVER = "Partida não encontrada ou já finalizada"
        PLAYER = "Jogador "
        PLAYER_WON = " venceu a partida!"
        PLAYER_LOST = " perdeu a partida."
        BET_VIEW_DESCRIPTION_PLAYER_NAME = "**Player:** "
        BET_VIEW_DESCRIPTION_FLEX_WIN_RATE = "**Flex Win Rate:** "
        BET_VIEW_DESCRIPTION_SOLO_WIN_RATE = "**Solo Win Rate:** "
        BET_VIEW_DESCRIPTION_ODDS_WIN = "**Odds Win:** "
        BET_VIEW_DESCRIPTION_ODDS_LOSE = "**Odds Lose:** "
        BET_VIEW_TITLE = "Estatísticas de jogador"

    class Register:
        REGISTER_NICK = ", digite seu nick da main no lol (sem a tag)"
        REGISTER_TAG = "Agora somente a tag (sem o #)"
        RIOT_ACCOUNT_NOT_FOUND = "Conta não reconhecida na API Riot, tente novamente"
        REGISTERED = "Registrado com sucesso"

    class Balance:
        VIEW_TITLE = "Seus pontos"
        VIEW_TOTAL_POINTS = "Seu total de pontos é: "

    class Functions:
        LAZY_DEV = "Já existe uma bet ativa no momento, espere o final ou reclame com o dev que não escalou a aplicação direito por preguiça."
        NOT_REGISTERED = ", você ainda não possui registro, digite !register primeiro"

    class Colors:
        BLUE = discord.Color.blue()
        PURPLE = discord.Color.purple()
        RED = discord.Color.red()
        GREEN = discord.Color.green()