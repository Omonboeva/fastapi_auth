from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from order.models import OrderStatus


class CategoryCreateSchema(BaseModel):
    name: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"example": {"name": "Electronics"}}
    }


class CategoryOutSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProductCreateSchema(BaseModel):
    title: str
    desc: str
    price: Decimal
    category_id: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "title": "iPhone 15",
                "desc": "Apple smartfoni",
                "price": 1299.99,
                "category_id": 1
            }
        }
    }


class ProductUpdateSchema(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None

    model_config = {"from_attributes": True}


class ProductOutSchema(BaseModel):
    id: int
    title: str
    desc: str
    price: Decimal
    category_id: Optional[int]

    model_config = {"from_attributes": True}



class CardItemAddSchema(BaseModel):
    product_id: int
    quantity: int = 1

    model_config = {
        "json_schema_extra": {"example": {"product_id": 3, "quantity": 2}}
    }


class CardItemOutSchema(BaseModel):
    id: int
    product_id: int
    quantity: int

    model_config = {"from_attributes": True}


class CardOutSchema(BaseModel):
    id: int
    user_id: int
    items: List[CardItemOutSchema] = []

    model_config = {"from_attributes": True}


class OrderItemOutSchema(BaseModel):
    id: int
    product_id: int
    quantity: int

    model_config = {"from_attributes": True}


class OrderOutSchema(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    items_order: List[OrderItemOutSchema] = []

    model_config = {"from_attributes": True}


class OrderStatusUpdateSchema(BaseModel):
    status: OrderStatus

    model_config = {
        "json_schema_extra": {"example": {"status": "in progress"}}
    }