from dataclasses import asdict
from typing import Optional

import firebase_admin
from firebase_admin import credentials, db
from constants import USER_REF_FIREBASE_DATABASE, USER_REF_POINTS_FIREBASE_DATABASE, FIREBASE_DATABASE_URL, \
    USER_REF_ACCOUNTS_FIREBASE_DATABASE, USER_REF_PLAYER_NAME_FIREBASE_DATABASE
from modal.user_modal import UserModal

def init_firebase():
    credential = credentials.Certificate("C:\\Users\\Tods\\PycharmProjects\\PythonProject\\config\\galgos-bet-discord-firebase-adminsdk-fbsvc-30cb193ae2.json")
    firebase_admin.initialize_app(credential, {
        'databaseURL': FIREBASE_DATABASE_URL,
    })


def get_firebase_database():
    if db is None:
        raise RuntimeError("Firebase ainda não foi inicializado. Chame init_firebase() primeiro.")
    return db.reference()


def save_user_firebase(user: UserModal):
    database_ref = get_firebase_database()
    accounts_dict = {account.puuid: asdict(account) for account in user.accounts}
    user_dict = asdict(user)
    user_dict[USER_REF_ACCOUNTS_FIREBASE_DATABASE] = accounts_dict
    user_ref = database_ref.child(USER_REF_FIREBASE_DATABASE).child(str(user.user_id))
    user_ref.set(user_dict)


def get_user_points_firebase(user_id: int) -> Optional[float]:
    database_ref = get_firebase_database()
    user_ref = database_ref.child(USER_REF_FIREBASE_DATABASE).child(str(user_id))
    user_data = user_ref.get()
    if isinstance(user_data, dict) and USER_REF_POINTS_FIREBASE_DATABASE in user_data:
        return user_data[USER_REF_POINTS_FIREBASE_DATABASE]
    else:
        raise ValueError("Pontos não encontrados ou formato inválido")


def check_user_registered_firebase(user_id: int) -> bool:
    database_ref = get_firebase_database()
    user_ref = database_ref.child(USER_REF_FIREBASE_DATABASE).child(str(user_id))
    user_data = user_ref.get()
    return user_data is not None


def get_account_by_id(user_id):
    database_ref = get_firebase_database()
    accounts_ref = database_ref.child(USER_REF_FIREBASE_DATABASE).child(str(user_id)).child(USER_REF_ACCOUNTS_FIREBASE_DATABASE)
    accounts = accounts_ref.get()

    matching_accounts = []

    if accounts and isinstance(accounts, dict):
        for account_id, account_data in accounts.items():
            matching_accounts.append({
                "user_id": str(user_id),
                "account_id": account_id,
                "account": account_data
            })

    return matching_accounts


def get_account_by_name(name):
    database_ref = get_firebase_database()
    user_ref = database_ref.child(USER_REF_FIREBASE_DATABASE)
    all_users = user_ref.get()

    matching_users = []

    if all_users and isinstance(all_users, dict):
        for user_id, user_data in all_users.items():
            accounts = user_data.get(USER_REF_ACCOUNTS_FIREBASE_DATABASE, {})
            for account_id, account in accounts.items():
                if account.get(USER_REF_PLAYER_NAME_FIREBASE_DATABASE, "").lower() == name.lower():
                    matching_users.append({
                        "user_id": user_id,
                        "account_id": account_id,
                        "account": account
                    })

    return matching_users


def add_points_to_user(user_id, points):
    database_ref = get_firebase_database()
    user_ref = database_ref.child(USER_REF_FIREBASE_DATABASE).child(str(user_id))
    user_data = user_ref.get()

    if not user_data and not isinstance(user_data, dict):
        raise ValueError("User not found")

    current_points = float(user_data.get(USER_REF_POINTS_FIREBASE_DATABASE, 0.0))
    new_points = current_points + points

    user_ref.update({USER_REF_POINTS_FIREBASE_DATABASE: new_points})


def get_points_ranking():
    database_ref = get_firebase_database()
    user_ref = database_ref.child(USER_REF_FIREBASE_DATABASE)
    all_users = user_ref.get()

    ranked_users = []

    if all_users and isinstance(all_users, dict):
        for user_id, user_data in all_users.items():
            points = user_data.get("points")
            accounts = user_data.get("accounts", {})

            player_name = None
            if accounts and isinstance(accounts, dict):
                first_account = next(iter(accounts.values()))
                player_name = first_account.get("player_name")

            if points is not None and player_name:
                ranked_users.append({
                    "player_name": player_name,
                    "points": points
                })

    ranked_users.sort(key=lambda x: x["points"], reverse=True)
    return ranked_users