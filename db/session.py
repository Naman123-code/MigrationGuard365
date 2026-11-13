import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
) 

class Base(DeclarativeBase):
    pass

# with engine.connect() as connection:
#     result = connection.execute(text("SELECT 1"))
#     print("PostgreSQL connection successful:", result.scalar())

def create_tables():
    from db import models
    Base.metadata.create_all(bind=engine)