from dataclasses import asdict
from typing import Optional, Any
import firebase_admin
from firebase_admin import credentials, firestore
from constants import USER_REF_FIREBASE_DATABASE, USER_REF_POINTS_FIREBASE_DATABASE
from modal.user_modal import UserModal

database: Optional[Any] = None

def init_firebase():
    global database
    credential = credentials.Certificate("config\galgos-bet-discord-firebase-adminsdk-fbsvc-30cb193ae2.json")
    firebase_admin.initialize_app(credential)
    database = firestore.client()

def get_firebase_database():
    global database
    if database is None:
        raise RuntimeError("Firebase ainda não foi inicializado. Chame init_firebase() primeiro.")
    return database

def save_user_firebase(user: UserModal):
    db = get_firebase_database()
    user_dict = asdict(user)
    user_ref = db.collection(USER_REF_FIREBASE_DATABASE).document(str(user.user_id))
    user_ref.set(user_dict)

def get_user_points_firebase(user_id: int):
    db = get_firebase_database()
    user_ref = db.collection(USER_REF_FIREBASE_DATABASE).document(str(user_id))
    doc = user_ref.get()

    if doc.exists:
        data = doc.to_dict()
        return data.get(USER_REF_POINTS_FIREBASE_DATABASE)
    else:
        raise ValueError("Pontos não encontrados")

def check_user_registered_firebase(user_id: int):
    db = get_firebase_database()
    user_ref = db.collection(USER_REF_FIREBASE_DATABASE).document(str(user_id))
    doc = user_ref.get()
    return doc.exists
