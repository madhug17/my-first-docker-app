import jwt
from datetime import datetime, timedelta

SECRET = "super-secret-key"

def create_access_token(data: dict):
    exp = datetime.utcnow() + timedelta(minutes=60)
    return jwt.encode({**data, "exp": exp}, SECRET, algorithm="HS256")

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except:
        return None