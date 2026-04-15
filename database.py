from sqlalchemy.orm import sessionmaker, declarative_base

from sqlalchemy import create_engine

engine=create_engine('postgresql://postgres:123@localhost:5432/fauth_db',echo=True)

Base=declarative_base()

SessionLocal=sessionmaker(bind=engine)

