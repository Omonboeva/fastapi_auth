from fastapi import FastAPI
from users.router import router as user_router
from database import Base, engine
from users.models import User

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router=user_router)

@app.get('/')
def test():
    return {'message': True}