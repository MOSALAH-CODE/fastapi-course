from fastapi import APIRouter, Depends, status, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from .. import schemas, database, models, token
from ..hashing import Hash
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from ..oauth2 import oauth2_scheme

REFRESH_TOKEN_EXPIRE_DAYS = 7


router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials"
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect password"
        )
    
    access_token = token.create_access_token(data={"email": user.email, "id": user.id})
    refresh_token = token.create_refresh_token(data={"email": user.email, "id": user.id})

    new_refresh_token = models.RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_refresh_token)
    db.commit()
    return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})

@router.post("/refresh")
def refresh_token(refresh_token: str = Form(...), db: Session = Depends(database.get_db)):
    # refresh_token = request.cookies.get("refresh_token")
    # if not refresh_token:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = token.verify_refresh_token(refresh_token, credentials_exception)
        user_id = payload.get("user_id")
        email = payload.get("user_id")

        db_refresh_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == refresh_token).first()
        if not db_refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        if db_refresh_token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired refresh token")

        new_access_token = token.create_access_token(data={"id": user_id, "email": email})
        return JSONResponse(content={"access_token": new_access_token, "token_type": "bearer"})
    except HTTPException as e:
        raise e
