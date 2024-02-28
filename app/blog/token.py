from fastapi import HTTPException, status
import jwt 
import time


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    payload = {
        "user_id": data['id'],
        "email": data["email"],
        "expires": time.time() + 60 * ACCESS_TOKEN_EXPIRE_MINUTES
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token["expires"] < time.time():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired")    
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    
    return decoded_token
