from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr
from enum import Enum


class BlogBase(BaseModel):
    title: str
    body: str

class Blog(BlogBase):
    class Config():
        orm_mode = True

class User(BaseModel):
    id: int
    name:str
    email:str
    password:str

class ShowUser(BaseModel):
    name:str
    email:str

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


# class BaseEventType(str, Enum):
#     CREATED = "created"
#     UPDATED = "updated"
#     DELETED = "deleted"
#     LOGGED_IN = "logged_in"
#     LOGGED_OUT = "logged_out"

#     @classmethod
#     def model_events(cls, model_name: str):
#         """
#         Dynamically generate event types for a specific model.
#         """
#         return {f"{model_name.upper()}_{event.value.upper()}": f"{model_name.lower()}_{event.value}" for event in cls}

class UserEventType(str, Enum):
    CREATED = "user_created"
    UPDATED = "user_updated"
    DELETED = "user_deleted"

class BlogEventType(str, Enum):
    CREATED = "blog_created"
    UPDATED = "blog_updated"
    DELETED = "blog_deleted"

class UserLog(BaseModel):
    user_id: int
    event_type: Union[UserEventType, BlogEventType]
    description: str

class ShowUserBlogs(BaseModel):
    name:str
    email:str
    blogs : List[Blog] =[]
    class Config():
        orm_mode = True

class ShowBlog(BaseModel):
    title: str
    body:str
    creator: ShowUser

    class Config():
        orm_mode = True


class Login(BaseModel):
    username: str
    password:str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    id: Optional[int] = None
