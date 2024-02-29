from sqlalchemy.orm import Session
from app.blog import models, schemas

def log_user_activity(db: Session, user_log: schemas.UserLog):
    new_log = models.UserLog(**user_log.dict())
    db.add(new_log)
    db.commit()
