import firebase_admin
from firebase_admin import credentials

firebase_config = {
    "type": "service_account",
    "project_id": "bluewave-ai-34bdc",
    "private_key_id": "4d9e3beb25181dedb384dc21b2ffb2c6dd1830a7",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCtG9AoC+r63eXE
... your key continues ...
-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-fbsvc@bluewave-ai-34bdc.iam.gserviceaccount.com",
    "client_id": "102907051675531062017",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40bluewave-ai-34bdc.iam.gserviceaccount.com"
}

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

print("Firebase credentials loaded successfully.")

