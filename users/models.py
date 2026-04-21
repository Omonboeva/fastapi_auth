from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(250))
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


    product = relationship('Products', back_populates='user')
    card = relationship('Card', back_populates='user', uselist=False)
    order = relationship('Order', back_populates='user')

    def __repr__(self):
        return self.username


class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id = Column(Integer, primary_key=True)
    token = Column(String(500), unique=True, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.now)