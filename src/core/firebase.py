import firebase_admin
from firebase_admin import credentials, auth
from src.core.config import settings
import json

def initialize_firebase():
    if not firebase_admin._apps:
        cred_dict = {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }

        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)