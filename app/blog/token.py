from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
import jwt 
import time
from .repository import user
from datetime import datetime, timedelta

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# def create_access_token(data: dict):
#     payload = {
#         "user_id": data['id'],
#         "email": data["email"],
#         "expires": time.time() + 60 * ACCESS_TOKEN_EXPIRE_MINUTES
#     }
#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": data['id'],
        "email": data["email"],
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):

    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "user_id": data['id'],
        "email": data["email"],
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, credentials_exception, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if payload["exp"] < time.time():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired")    
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    except jwt.PyJWTError:
        raise credentials_exception
    
    user_obj = user.get_user(id=user_id, db=db)
    if user_obj is None:
        raise credentials_exception
    return user_obj

def verify_refresh_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise credentials_exception
