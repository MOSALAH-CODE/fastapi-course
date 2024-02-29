from fastapi import FastAPI
from .blog import models
from .blog.database import engine
from .blog.routers import blog, user, authentication

import redis
import json

rd = redis.Redis(host= "localhost", port=6379, db=0)


app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(authentication.router)
app.include_router(blog.router)
app.include_router(user.router)


# @app.get('/test')
# def  test():
#     cache = rd.get('test1')
#     print(cache)
#     if cache:
#         print("cache hit")
#         return {'msg': json.loads(cache)}
#     else:
#         rd.set("test1","123")
#         rd.expire("test1", 5)
#         print("cache mis")
#         return {"msg": 'Hello World'}