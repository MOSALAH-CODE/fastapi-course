from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.blog.token import verify_token
from sqlalchemy.orm import Session
from app.blog.database import get_db
from . import token
from .repository import user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(data: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token = token.verify_token(data)

    current_user = user.show(verify_token['user_id'], db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {verify_token['id']} is not available")
    return current_user
    