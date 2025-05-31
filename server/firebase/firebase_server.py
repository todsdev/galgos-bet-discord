from dataclasses import asdict
from typing import Optional
import firebase_admin
from firebase_admin import credentials, db
from constants import Constants
from exceptions import GalgosBetException
from modal.account_modal import AccountModal
from modal.user_modal import UserModal

def init_firebase():
    credential = credentials.Certificate(Constants.Firebase.CERTIFICATE_PATH)
    firebase_admin.initialize_app(credential, {
        Constants.Firebase.FIREBASE_DATABASE_URL_REQUEST: Constants.Firebase.FIREBASE_DATABASE_URL,
    })

def get_firebase_database():
    if db is None:
        raise RuntimeError(Constants.Errors.RUNTIME_FIREBASE_EXCEPTION)
    return db.reference()

def save_user_firebase(user: UserModal):
    try:
        database_ref = get_firebase_database()
        accounts_dict = {account.puuid: asdict(account) for account in user.accounts}
        user_dict = asdict(user)
        user_dict[Constants.Firebase.USER_REF_ACCOUNTS_FIREBASE_DATABASE] = accounts_dict
        user_ref = database_ref.child(Constants.Firebase.USER_REF_FIREBASE_DATABASE).child(str(user.user_id))
        user_ref.set(user_dict)

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.FIREBASE_EXCEPTION}{str(exception)}")

def get_user_by_id(user_id: int):
    try:
        database_ref = get_firebase_database()
        user_ref = database_ref.child(Constants.Firebase.USER_REF_FIREBASE_DATABASE).child(str(user_id))
        user_data = user_ref.get()

        if user_data and isinstance(user_data, dict):
            name = user_data.get(Constants.Generic.USER_NAME, Constants.Generic.EMPTY_STRING)
            nick = user_data.get(Constants.Generic.USER_NICK, Constants.Generic.EMPTY_STRING)
            points = float(user_data.get(Constants.Generic.POINTS, 0))

            accounts_raw = user_data.get(Constants.Generic.ACCOUNTS, {})
            accounts: list[AccountModal] = []

            for account_id, data in accounts_raw.items():
                account = AccountModal(
                    player_name=data.get(Constants.Generic.PLAYER_NAME, Constants.Generic.EMPTY_STRING),
                    player_tag=data.get(Constants.Generic.PLAYER_TAG, Constants.Generic.EMPTY_STRING),
                    puuid=data.get(Constants.Generic.PUUID, Constants.Generic.EMPTY_STRING),
                    main=data.get(Constants.Generic.MAIN, False)
                )
                accounts.append(account)

            return UserModal(
                user_id=user_id,
                name=name,
                nick=nick,
                registered=True,
                points=points,
                accounts=accounts
            )

        else:
            raise GalgosBetException(Constants.Errors.VALUE_ERROR_USER)

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.FIREBASE_EXCEPTION}{str(exception)}")

def get_user_points_firebase(user_id: int) -> Optional[float]:
    try:
        database_ref = get_firebase_database()
        user_ref = database_ref.child(Constants.Firebase.USER_REF_FIREBASE_DATABASE).child(str(user_id))
        user_data = user_ref.get()
        if isinstance(user_data, dict) and Constants.Firebase.USER_REF_POINTS_FIREBASE_DATABASE in user_data:
            return user_data[Constants.Firebase.USER_REF_POINTS_FIREBASE_DATABASE]
        else:
            raise ValueError(Constants.Errors.VALUE_ERROR_POINTS)

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.FIREBASE_EXCEPTION}{str(exception)}")

def check_user_registered_firebase(user_id: int) -> bool:
    try:
        database_ref = get_firebase_database()
        user_ref = database_ref.child(Constants.Firebase.USER_REF_FIREBASE_DATABASE).child(str(user_id))
        user_data = user_ref.get()
        return user_data is not None

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.FIREBASE_EXCEPTION}{str(exception)}")

def get_account_by_id(user_id):
    try:
        database_ref = get_firebase_database()
        accounts_ref = database_ref.child(Constants.Firebase.USER_REF_FIREBASE_DATABASE).child(str(user_id)).child(
            Constants.Firebase.USER_REF_ACCOUNTS_FIREBASE_DATABASE)
        accounts = accounts_ref.get()

        matching_accounts = []

        if accounts and isinstance(accounts, dict):
            for account_id, account_data in accounts.items():
                matching_accounts.append({
                    Constants.Generic.USER_ID: str(user_id),
                    Constants.Generic.ACCOUNT_ID: account_id,
                    Constants.Generic.ACCOUNT: account_data
                })

        return matching_accounts

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.FIREBASE_EXCEPTION}{str(exception)}")

def get_account_by_name(name):
    try:
        database_ref = get_firebase_database()
        user_ref = database_ref.child(Constants.Firebase.USER_REF_FIREBASE_DATABASE)
        all_users = user_ref.get()

        matching_users = []

        if all_users and isinstance(all_users, dict):
            for user_id, user_data in all_users.items():
                accounts = user_data.get(Constants.Firebase.USER_REF_ACCOUNTS_FIREBASE_DATABASE, {})
                for account_id, account in accounts.items():
                    if account.get(Constants.Firebase.USER_REF_PLAYER_NAME_FIREBASE_DATABASE,
                                   "").lower() == name.lower():
                        matching_users.append({
                            Constants.Generic.USER_ID: user_id,
                            Constants.Generic.ACCOUNT_ID: account_id,
                            Constants.Generic.ACCOUNT: account
                        })

        return matching_users

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.FIREBASE_EXCEPTION}{str(exception)}")

def add_points_to_user(user_id, points):
    try:
        database_ref = get_firebase_database()
        user_ref = database_ref.child(Constants.Firebase.USER_REF_FIREBASE_DATABASE).child(str(user_id))
        user_data = user_ref.get()

        if not user_data and not isinstance(user_data, dict):
            raise ValueError(Constants.Errors.VALUE_ERROR_USER)

        current_points = float(user_data.get(Constants.Firebase.USER_REF_POINTS_FIREBASE_DATABASE, 0.0))
        new_points = current_points + points

        user_ref.update({Constants.Firebase.USER_REF_POINTS_FIREBASE_DATABASE: new_points})

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.FIREBASE_EXCEPTION}{str(exception)}")

def get_points_ranking():
    try:
        database_ref = get_firebase_database()
        user_ref = database_ref.child(Constants.Firebase.USER_REF_FIREBASE_DATABASE)
        all_users = user_ref.get()

        ranked_users = []

        if all_users and isinstance(all_users, dict):
            for user_id, user_data in all_users.items():
                points = user_data.get(Constants.Generic.POINTS)
                accounts = user_data.get(Constants.Generic.ACCOUNTS, {})

                player_name = None
                if accounts and isinstance(accounts, dict):
                    first_account = next(iter(accounts.values()))
                    player_name = first_account.get(Constants.Generic.PLAYER_NAME)

                if points is not None and player_name:
                    ranked_users.append({
                        Constants.Generic.PLAYER_NAME: player_name,
                        Constants.Generic.POINTS: points
                    })

        ranked_users.sort(key=lambda x: x[Constants.Generic.POINTS], reverse=True)
        return ranked_users

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.FIREBASE_EXCEPTION}{str(exception)}")

def add_user_account(user_id: int, account: AccountModal):
    try:
        database_ref = get_firebase_database()
        account_ref = database_ref.child(Constants.Firebase.USER_REF_FIREBASE_DATABASE).child(str(user_id)).child(
            Constants.Firebase.USER_REF_ACCOUNTS_FIREBASE_DATABASE).child(account.puuid)

        account_ref.set(asdict(account))

    except Exception as exception:
        raise GalgosBetException(f"{Constants.Errors.FIREBASE_EXCEPTION}{str(exception)}")