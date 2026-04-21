from fastapi import FastAPI
from database import Base, engine
from users.models import User, TokenBlacklist
from users.router import router as user_router
from fastapi import FastAPI
from database import Base, engine
from users.models import User, TokenBlacklist
from users.router import router as user_router
from order.models import Products, Category, Card, CardItem, Order, OrderItem
from order.router import category_router, product_router, card_router, order_router


Base.metadata.create_all(bind=engine)


app = FastAPI()
app.include_router(router=user_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(card_router)
app.include_router(order_router)

@app.get('/')
def test():
    return {'message': True}







