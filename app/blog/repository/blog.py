from sqlalchemy.orm import Session
from .. import models, schemas
from fastapi import HTTPException, status, Response
from fastapi.responses import JSONResponse
from app.blog.repository.activity import log_user_activity

def get_all(db: Session):
    blogs = db.query(models.Blog).all()
    return blogs


def create(request: schemas.Blog, current_user: schemas.User, db: Session):
    new_blog = models.Blog(title=request.title, body=request.body, user_id=current_user.id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    user_log = schemas.UserLog(
        user_id=current_user.id, 
        event_type=schemas.BlogEventType.CREATED, 
        description=f'Created new blog by {current_user.email}',  
    )
    log_user_activity(db, user_log)

    return JSONResponse(content={"message": f"New blog created successfully"})


def destroy(id: int, current_user: schemas.User, db: Session):
    q = db.query(models.Blog).filter(models.Blog.id == id)
    blog = q.first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")
    
    if blog.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this blog")


    q.delete(synchronize_session=False)
    db.commit()

    user_log = schemas.UserLog(
        user_id=current_user.id, 
        event_type=schemas.BlogEventType.DELETED, 
        description=f'Deleted blog with id {id} by {current_user.email}',  
    )
    log_user_activity(db, user_log)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Blog with id {id} deleted successfully"})


def update(id: int, request: schemas.Blog, current_user: schemas.User, db: Session):
    q = db.query(models.Blog).filter(models.Blog.id == id)
    blog = q.first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")
    
    if blog.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this blog")
    print(request.dict())
    try:
        q.update(request.dict(), synchronize_session=False)
        db.commit()
    except AttributeError:
        raise HTTPException(status_code=400,  
                            detail="Invalid data provided for updating the Blog")
    
    user_log = schemas.UserLog(
        user_id=current_user.id, 
        event_type=schemas.BlogEventType.UPDATED, 
        description=f'Updated blog with id {id} by {current_user.email}',  
    )
    log_user_activity(db, user_log)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"Blog with id {id} updated successfully"})


def show(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with the id {id} is not available")
    return blog
