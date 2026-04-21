from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from users.router import get_current_user
from users.models import User
from order.models import Products, Category, Card, CardItem, Order, OrderItem, OrderStatus
from order.schemas import (
    ProductCreateSchema, ProductUpdateSchema,
    CategoryCreateSchema,
    CardItemAddSchema,
    OrderStatusUpdateSchema
)

router = APIRouter(tags=['products'])

category_router = APIRouter(prefix='/categories', tags=['categories'])


@category_router.get('/')
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return JSONResponse(content={
        "status": 200,
        "data": [{"id": c.id, "name": c.name} for c in categories]
    })


@category_router.post('/', status_code=201)
def create_category(
    data: CategoryCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(status_code=400, detail="Bu kategoriya mavjud")

    cat = Category(name=data.name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return JSONResponse(status_code=201, content={
        "status": 201, "message": "Kategoriya yaratildi",
        "data": {"id": cat.id, "name": cat.name}
    })


@category_router.delete('/{category_id}')
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    db.delete(cat)
    db.commit()
    return JSONResponse(content={"status": 200, "message": "Kategoriya o'chirildi"})



product_router = APIRouter(prefix='/products', tags=['products'])


@product_router.get('/')
def list_products(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    return JSONResponse(content={
        "status": 200,
        "data": [
            {
                "id": p.id,
                "title": p.title,
                "desc": p.desc,
                "price": float(p.price),
                "category_id": p.category_id
            }
            for p in products
        ]
    })


@product_router.get('/{product_id}')
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Products).filter(Products.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return JSONResponse(content={
        "status": 200,
        "data": {
            "id": p.id, "title": p.title,
            "desc": p.desc, "price": float(p.price),
            "category_id": p.category_id
        }
    })


@product_router.post('/', status_code=201)
def create_product(
    data: ProductCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    product = Products(
        title=data.title,
        desc=data.desc,
        price=data.price,
        category_id=data.category_id,
        user_id=current_user.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return JSONResponse(status_code=201, content={
        "status": 201, "message": "Mahsulot yaratildi",
        "data": {"id": product.id, "title": product.title, "price": float(product.price)}
    })


@product_router.patch('/{product_id}')
def update_product(
    product_id: int,
    data: ProductUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    if data.title is not None:
        product.title = data.title
    if data.desc is not None:
        product.desc = data.desc
    if data.price is not None:
        product.price = data.price
    if data.category_id is not None:
        product.category_id = data.category_id

    db.commit()
    db.refresh(product)
    return JSONResponse(content={
        "status": 200, "message": "Mahsulot yangilandi",
        "data": {"id": product.id, "title": product.title, "price": float(product.price)}
    })


@product_router.delete('/{product_id}')
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    db.delete(product)
    db.commit()
    return JSONResponse(content={"status": 200, "message": "Mahsulot o'chirildi"})


card_router = APIRouter(prefix='/card', tags=['card'])


def get_or_create_card(user: User, db: Session) -> Card:
    card = db.query(Card).filter(Card.user_id == user.id).first()
    if not card:
        card = Card(user_id=user.id)
        db.add(card)
        db.commit()
        db.refresh(card)
    return card


@card_router.get('/')
def get_card(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = get_or_create_card(current_user, db)
    items = db.query(CardItem).filter(CardItem.card_id == card.id).all()
    return JSONResponse(content={
        "status": 200,
        "data": {
            "id": card.id,
            "items": [
                {"id": i.id, "product_id": i.product_id, "quantity": i.quantity}
                for i in items
            ]
        }
    })


@card_router.post('/add')
def add_to_card(
    data: CardItemAddSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Products).filter(Products.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    card = get_or_create_card(current_user, db)


    existing = db.query(CardItem).filter(
        CardItem.card_id == card.id,
        CardItem.product_id == data.product_id
    ).first()

    if existing:
        existing.quantity += data.quantity
    else:
        db.add(CardItem(card_id=card.id, product_id=data.product_id, quantity=data.quantity))

    db.commit()
    return JSONResponse(content={"status": 200, "message": "Mahsulot savatchaga qo'shildi"})


@card_router.delete('/remove/{item_id}')
def remove_from_card(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = get_or_create_card(current_user, db)
    item = db.query(CardItem).filter(
        CardItem.id == item_id,
        CardItem.card_id == card.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Element topilmadi")

    db.delete(item)
    db.commit()
    return JSONResponse(content={"status": 200, "message": "Mahsulot savatchadan o'chirildi"})


@card_router.delete('/clear')
def clear_card(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    card = get_or_create_card(current_user, db)
    db.query(CardItem).filter(CardItem.card_id == card.id).delete()
    db.commit()
    return JSONResponse(content={"status": 200, "message": "Savatcha tozalandi"})





order_router = APIRouter(prefix='/orders', tags=['orders'])


@order_router.post('/checkout', status_code=201)
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    card = db.query(Card).filter(Card.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=400, detail="Savatcha bo'sh")

    items = db.query(CardItem).filter(CardItem.card_id == card.id).all()
    if not items:
        raise HTTPException(status_code=400, detail="Savatcha bo'sh")

    order = Order(user_id=current_user.id, status=OrderStatus.new)
    db.add(order)
    db.flush()

    for item in items:
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity
        ))


    db.query(CardItem).filter(CardItem.card_id == card.id).delete()
    db.commit()
    db.refresh(order)

    return JSONResponse(status_code=201, content={
        "status": 201,
        "message": "Order yaratildi",
        "data": {"order_id": order.id, "status": order.status.value}
    })


@order_router.get('/')
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return JSONResponse(content={
        "status": 200,
        "data": [
            {
                "id": o.id,
                "status": o.status.value,
                "items": [
                    {"product_id": i.product_id, "quantity": i.quantity}
                    for i in o.items_order
                ]
            }
            for o in orders
        ]
    })


@order_router.get('/{order_id}')
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order topilmadi")

    return JSONResponse(content={
        "status": 200,
        "data": {
            "id": order.id,
            "status": order.status.value,
            "items": [
                {"product_id": i.product_id, "quantity": i.quantity}
                for i in order.items_order
            ]
        }
    })


@order_router.patch('/{order_id}/status')
def update_order_status(
    order_id: int,
    data: OrderStatusUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_staff:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order topilmadi")

    order.status = data.status
    db.commit()
    return JSONResponse(content={
        "status": 200,
        "message": "Order holati yangilandi",
        "data": {"order_id": order.id, "status": order.status.value}
    })