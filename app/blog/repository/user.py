
from sqlalchemy.orm import Session
from app.blog.repository.blog import destroy
from app.blog.repository.activity import log_user_activity
from .. import models, schemas
from fastapi import HTTPException, status, Response
from ..hashing import Hash
from datetime import datetime

def create(request: schemas.User, db: Session):
    existing_user = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"User with email {request.email} already exists")

    new_user = models.User(
        name=request.name, 
        email=request.email, 
        password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    user_log = schemas.UserLog(
        user_id=new_user.id, 
        event_type=schemas.UserEventType.CREATED, 
        description=f'Created account for {new_user.email}',  
    )
    log_user_activity(db, user_log)
    return new_user


def get_user(id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Current user is not available")
    return user


def show(current_user: schemas.User, db: Session):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User is not available")
    return user


def destroy(current_user: schemas.User, db: Session):
    q = db.query(models.User).filter(models.User.id == current_user.id)
    user = q.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User is not available")
    user_log = schemas.UserLog(
        user_id=user.id, 
        event_type=schemas.UserEventType.DELETED, 
        description=f'Deleted account for {user.email}',  
    )
    q.delete(synchronize_session=False)
    db.commit()
    log_user_activity(db, user_log)
    return Response(status_code=status.HTTP_200_OK, content=f"User deleted successfully")

def update_user(current_user: schemas.User, request: schemas.UserUpdate, db: Session):
    user_obj = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_user = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"User with email {request.email} already exists")


    user_data = request.dict(exclude_unset=True)
    for key, value in user_data.items():
        if key == 'password':
            setattr(user_obj, key, Hash.bcrypt(value))
        else:
            setattr(user_obj, key, value)

    db.commit()
    user_log = schemas.UserLog(
        user_id=current_user.id, 
        event_type=schemas.UserEventType.UPDATED, 
        description=f'Updated account for {current_user.email}',  
    )
    log_user_activity(db, user_log)
    return user_obj

# def log_user_activity(db: Session, user_log: schemas.UserLog):
#     print(user_log)
#     new_log = models.UserLog(**user_log.dict())
#     db.add(new_log)
#     db.commit()

def get_logs(current_user: schemas.User, db: Session):
    logs = db.query(models.UserLog).filter(models.UserLog.user_id == current_user.id).all()
    if not logs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Logs for the user are not available")
    return logs

