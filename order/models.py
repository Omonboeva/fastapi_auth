from datetime import datetime

from database import Base, engine
from sqlalchemy import Text, String, Column, Integer, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
import enum


class OrderStatus(str, enum.Enum):
    new = "new"
    in_progress = "in progress"
    done = "done"


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    product = relationship('Products', back_populates='category')


class Products(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    desc = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(ForeignKey('category.id'), nullable=True)
    user_id = Column(ForeignKey('user.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    category = relationship('Category', back_populates='product')
    user = relationship('User', back_populates='product')


class Card(Base):
    __tablename__ = 'card'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'), unique=True)

    items = relationship('CardItem', back_populates='card')
    user = relationship('User', back_populates='card')


class CardItem(Base):
    __tablename__ = 'card_item'

    id = Column(Integer, primary_key=True)
    card_id = Column(ForeignKey('card.id'))
    product_id = Column(ForeignKey('product.id'))
    quantity = Column(Integer, default=1)

    card = relationship('Card', back_populates='items')
    product = relationship('Products')


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'))
    status = Column(Enum(OrderStatus), default=OrderStatus.new)
    created_at = Column(DateTime, default=datetime.now)

    items_order = relationship('OrderItem', back_populates='order')
    user = relationship('User', back_populates='order')


class OrderItem(Base):
    __tablename__ = 'order_item'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('order.id'))
    product_id = Column(ForeignKey('product.id'))
    quantity = Column(Integer, default=1)

    order = relationship('Order', back_populates='items_order')
    product = relationship('Products')