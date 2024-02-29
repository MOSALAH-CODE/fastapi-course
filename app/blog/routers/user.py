from .. import database, schemas, models, oauth2
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from ..repository import user
from typing import List
from app import main
import json

router = APIRouter(
    prefix="/user",
    tags=['Users']
)

get_db = database.get_db


@router.post('/', response_model=schemas.ShowUser)
def create_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    return user.create(request, db)


# @router.get('/{id}', response_model=schemas.ShowUser)
# def get_user(id: int, db: Session = Depends(get_db)):
#     return user.show(id, db)

@router.get('/', response_model=schemas.ShowUser)
def profile(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.show(current_user, db)

@router.delete('/')
def destroy(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.destroy(current_user, db)

@router.put('/', response_model=schemas.ShowUser)
def update_user(request: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return user.update_user(current_user, request, db)

@router.get('/logs', response_model=List[schemas.UserLog])
def get_user_logs(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    cache = main.rd.get("user-log")
    if cache:
        cached_logs = json.loads(cache.decode('utf-8'))
        return [schemas.UserLog(**log) for log in cached_logs]
    else:
        user_logs = user.get_logs(current_user, db)
        serialized_logs = []
        for log in user_logs:
            serialized_logs.append({
                "user_id": log.user.id,
                "event_type": log.event_type,
                "description": log.description
            })
        serialized_logs_bytes = json.dumps(serialized_logs).encode('utf-8')
        main.rd.setex('user-log', 30, serialized_logs_bytes)
        return user_logs