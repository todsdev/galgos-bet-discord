import discord


class Constants:
    class Generic:
        EMPTY_STRING = ""
        UNKNOWN = "Desconhecido"
        PLAYER_NAME = "player_name"
        PLAYER_TAG = "player_tag"
        PUUID = "puuid"
        POINTS = "points"
        POINTS_PTBR = "pontos"
        ACCOUNT = "account"
        ACCOUNTS = "accounts"
        GAME_ID = "gameId"
        EVENT_MESSAGE = "message"
        USER_ID = "user_id"
        ACCOUNT_ID = "account_id"
        USER_NAME = "user_name"
        NAME = "name"
        USER_NICK = "user_nick"
        MAIN = "main"
        HASHTAG = "#"
        PERCENTAGE = "%"
        INFORMATION = "info"
        PARTICIPANTS = "participants"
        WIN = "win"
        WINS = "wins"
        LOSE = "lose"
        LOSSES = "losses"
        QUEUE_TYPE = "queueType"
        RANKED_FLEX = "RANKED_FLEX_SR"
        RANKED_SOLO = "RANKED_SOLO_5x5"
        API_KEY = "?api_key="
        REGEX_STRING_AS_INT = r"\d+"
        KEY_W = "w"
        KEY_L = "l"
        COLMA_SPACE = ", "

    class Riot:
        RIOT_API_TOKEN = "RGAPI-3fa78d83-75f4-4687-bb6e-d837fe34b9f2"
        RIOT_PLATFORM = "br1"
        RIOT_REGION = "americas"
        URL_ACCOUNT_BY_RIOT_ID = (
            "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
        )
        URL_SPECTATE_LIVE_GAME = (
            "https://br1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/"
        )
        URL_MATCH_RESULT = (
            "https://americas.api.riotgames.com/lol/match/v5/matches/BR1_"
        )
        URL_WIN_RATE = "https://br1.api.riotgames.com/lol/league/v4/entries/by-puuid/"

    class Discord:
        DISCORD_TOKEN = (
            "MTM3MDM3OTg3NTE4NTA2NjAwNA.G4aApZ.Hhv9M5_1kR-mKf6JAFX7eSPIlMfgtmhkV6MDdM"
        )

    class Firebase:
        FIREBASE_DATABASE_URL = (
            "https://galgos-bet-discord-default-rtdb.firebaseio.com/"
        )
        FIREBASE_DATABASE_URL_REQUEST = "databaseURL"
        USER_REF_FIREBASE_DATABASE = "users"
        USER_REF_ACCOUNTS_FIREBASE_DATABASE = "accounts"
        USER_REF_POINTS_FIREBASE_DATABASE = "points"
        USER_REF_BANKRUPTCY_FIREBASE_DATABASE = "bankruptcies"
        USER_REF_PLAYER_NAME_FIREBASE_DATABASE = "player_name"
        TOURNAMENT_REF_FIREBASE_DATABASE = "tournament"
        CERTIFICATE_PATH = "C:\\Users\\Tods\\PycharmProjects\\PythonProject\\config\\galgos-bet-discord-firebase-adminsdk-fbsvc-30cb193ae2.json"

    class Commands:
        COMMAND_REGISTER_PLAYER = "!register"
        COMMAND_RANKING = "!ranking"
        COMMAND_BALANCE = "!balance"
        COMMAND_START_BET = "!start"
        COMMAND_SELF_BET = "!self"
        COMMAND_COMMANDS = "!commands"
        COMMAND_JOIN = "!join"
        COMMAND_ADD = "!add"
        COMMAND_BET_VALUE = "!bet"
        COMMAND_BET_VALUE_ALL_IN = "!allin"
        COMMAND_LOAD = "!helpmedaddy"

    class CommandsView:
        GB_COMMANDS = "**!commands:** Comandos gerais do BOT"
        REGISTER = "**!register:** Se registrar no sistema pela primeira vez"
        BALANCE = "**!balance:** Saber quantos pontos você tem para apostar"
        START = "**!start:** Começar o sistema de bet para algum player registrado"
        SELF = "**!self:** Começar o sistema de bet para sua conta"
        RANKING = "**!ranking:** Exibe o ranking de pontuação dos membros da season"
        JOIN = "**!join:** Permite entrar na instância de bet aberta"
        ADD = "**!add:** Permite adicionar outra conta ao seu pefil"
        BET_VALUE = "**!bet:** Caso tenha uma aposta ativa e pontos suficiente, permite apostar um valor para vitória ou derrota (exemplo: !bet 500w ou !bet 750l)"
        BET_VALUE_ALL_IN = "**!allin:** Caso tenha uma aposta ativa e pontos suficiente, permite apostar todo seus pontos para vitória ou derrota (exemplo: !allinw ou !allwinl)"
        LOAD = "**!helpmedaddy:** Caso tenha falido devido as suas más escolhas, talvez seu dev seja benevolente com você"
        TITLE = "Comandos"

    class Errors:
        TIMEOUT_MESSAGE = "Demorou demais, tente novamente"
        GALGOS_EXCEPTION = "Ocorreu um erro no sistema de apostas dos Galgos"
        RANKING_EXCEPTION = "Ocorreu um erro ao recuperar ranking de pontos: "
        BALANCE_EXCEPTION = "Ocorreu um erro ao recuperar balance de pontos: "
        RANKING_EXCEPTION_FIREBASE = "Ocorreu um erro ao recuperar pontos do Firebase"
        ADD_ACCOUNT_ERROR = "Ocorreu um erro ao adicionar nova conta"
        JOIN_EXCEPTION = "Ocorreu um erro ao tentar entrar no sistema de bet: "
        UNKNOWN_SEARCH_RESPONSE = "Search response não foi recuperado no formato ideal"
        MULTIPLE_SELF_BET_ERROR = (
            "Ocorreu um erro ao tentar identificar qual conta está sendo jogada: "
        )
        FIREBASE_EXCEPTION = "Erro ao recuperar dados do Firebase: "
        RUNTIME_FIREBASE_EXCEPTION = (
            "Firebase ainda não foi inicializado, chame init_firebase() primeiro"
        )
        VALUE_ERROR_POINTS = "Pontos não encontrados ou formato inválido"
        VALUE_ERROR_TOURNAMENT = "Torneio não encontrado"
        VALUE_ERROR_USER = "Usuário não encontrado"
        ERROR_ADD_BET = "Um erro ao processar bet"
        RIOT_ERROR_ACCOUNT_INFORMATION = "Error (return_account_information): "
        RIOT_ERROR_SPECTATE_LIVE_GAME = "Error (spectate_live_game): "
        RIOT_ERROR_MATCH_RESULT = "Error (check_match_result): "
        RIOT_ERROR_WIN_RATE = "Error (retrieve_win_rate): "

    class Prints:
        PRINT_REGISTER_PLAYER = "Start player registering for first time"
        PRINT_BALANCE = "Displaying player points balance"
        PRINT_START = "Start player bet"
        PRINT_COMMANDS = "Displaying commands"
        PRINT_RANKING = "Displaying players points ranking"
        PRINT_SELF_START = "Start self player bet"
        PRINT_MATCH_LIVE = "Partida em andamento"
        PRINT_TRYING_JOIN = "Jogador tentando entrar no sistema de bet"
        PRINT_ADD_ACCOUNT = "Jogador tentando adicionar conta nova"
        PRINT_BET_VALUE = "Jogador tentando fazer aposta"
        PRINT_BET_VALUE_ALL_IN = "Jogador tentando fazer aposta all in"
        PRINT_GLOBAL_RESET = "Instância global resetada"
        PRINT_ACCOUNT_FOUND = "Encontrado jogo ativo para jogador solicitante"
        PRINT_LOAD = "Jogador precisa de pontos"
        PRINT_APPLICATION_ALIVE = "Application started"

    class Ranking:
        RANKING = "Ranking"

    class SelfBet:
        NOT_FOUND = "Não foi encontrado ninguém com esse nome no banco de dados"
        DUPLICATED = "Você possui mais de uma conta salva, o desenvolvedor preguiçoso ainda não implementou essa parte"

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
        BET_VIEW_DESCRIPTION_FLEX_TOTAL_GAMES = "**Flex Total Games:** "
        BET_VIEW_DESCRIPTION_SOLO_WIN_RATE = "**Solo Win Rate:** "
        BET_VIEW_DESCRIPTION_SOLO_TOTAL_GAMES = "**Solo Total Games:** "
        BET_VIEW_DESCRIPTION_SEASON_TOTAL_GAMES = "**Total Games:** "
        BET_VIEW_DESCRIPTION_ODDS_WIN = "**Odds Win:** "
        BET_VIEW_DESCRIPTION_ODDS_LOSE = "**Odds Lose:** "
        BET_VIEW_TITLE = "Estatísticas de jogador"
        BET_PERIOD_AVAILABLE_TITLE = "Sistema de bet iniciado"
        BET_PERIOD_AVAILABLE_DESCRIPTION = """
        Digite !join para participar da aposta
        Você tem 2 minutos até o sistema fechar
        """
        BET_PERIOD_ENDED = "Sistema de bet para essa partida está fechado"
        REDISTRIBUTED_POINTS = "Os pontos foram redistribuídos"
        BET_ENDED_TITLE = "Estatísticas finais"
        BET_ENDED_DESCRIPTION_TOTAL_BETS = "**Número de apostas:** "
        BET_ENDED_DESCRIPTION_TOTAL_VALUE = "**Valor total:** "
        BET_ENDED_DESCRIPTION_TOTAL_PLAYERS_WON = "**Players vencedores:** "
        BET_ENDED_DESCRIPTION_TOTAL_PLAYERS_LOST = "**Players perdedores:** "
        BET_ENDED_DESCRIPTION_TOTAL_VALUE_WON = "**Valor total ganho:** "
        BET_ENDED_DESCRIPTION_TOTAL_VALUE_LOST = "**Valor total perdido:** "
        BET_ENDED_DESCRIPTION_TOTAL_BETS_WON = "**Número de apostas vencedoras:** "
        BET_ENDED_DESCRIPTION_TOTAL_BETS_LOST = "**Número de apostas perdedoras:** "
        LIVE_MATCH_NOT_FOUND = "Não foi encontrada nenhuma partida ao vivo para suas contas, tente novamente"

    class Register:
        REGISTER_NICK = ", digite seu nick da main no lol (sem a tag)"
        REGISTER_TAG = "Agora somente a tag (sem o #)"
        RIOT_ACCOUNT_NOT_FOUND = "Conta não reconhecida na API Riot, tente novamente"
        REGISTERED = "Registrado com sucesso"

    class Join:
        BET_NOT_FOUND = "Não existe bet ativa no momento"
        YOUR_BALANCE_START = ", você atualmente possui "
        YOUR_BALANCE_END = " pontos para apostar, use com sabedoria"
        NOT_ENOUGH_POINTS = ", você não tem pontos o suficiente"

    class Load:
        HAVE_POINTS = "Não precisa se humilhar, você tem pontos o suficiente"
        SUPPORTIVE = ", seu papai dev é benevolente e vai te dar um trocadinho para você se divertir"

    class Balance:
        VIEW_TITLE = "Seus pontos"
        VIEW_TOTAL_POINTS = "Seu total de pontos é: "

    class AddAccount:
        REGISTER_NICK = ", digite seu nick da sua conta secundária no lol (sem a tag)"
        REGISTER_TAG = "Agora somente a tag (sem o #)"
        REGISTERED = "Conta secundária registrada com sucesso"

    class BetValue:
        NO_BET_AVAILABLE = "No momento não existe uma aposta ativa"
        INCORRECT_BET_VALUE = (
            "Valor incorreto para aposta, reveja informações e tente novamente"
        )
        NO_SIDE = "Não foi enviado 'w' ou 'l' no final do comando de bet para informar se é uma bet de vitória ou derrota (exemplo: !bet 500w)"
        WHICH_SIDE = "Você acha que vai ser vitória ou derrota? Digite 'win' ou 'lose'"
        BET_CANCELED = "Bet cancelada por errar muitas vezes um fluxo tão simples"
        BET_SUCCESS = ", bet enviada com sucesso"
        RECEIPT_TITLE = "Recibo / "
        DESCRIPTION_ALL_IN = "**All in**: Foi apostado todos os pontos, e caso vitorioso, o valor ganho é dobrado"
        DESCRIPTION_VALUE = "**Valor**: "
        DESCRIPTION_IS_WIN = "**Vitória**: "
        DESCRIPTION_ODD_WIN = "**Odd Vitória**: "
        DESCRIPTION_ODD_LOSE = "**Odd Derrota**: "
        DESCRIPTION_WIN_POSSIBILITY = "**Perspectiva de Vitória**: "

    class Functions:
        LAZY_DEV = "Já existe uma bet ativa no momento, espere o final ou reclame com o dev que não escalou a aplicação direito por preguiça."
        NOT_REGISTERED = ", você ainda não possui registro, digite !register primeiro"
        ALREADY_REGISTERED = ", você já possui registro"

    class Colors:
        BLUE = discord.Color.blue()
        PURPLE = discord.Color.purple()
        RED = discord.Color.red()
        GREEN = discord.Color.green()
