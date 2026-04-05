

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


load_dotenv()


DB_USER     = os.getenv("DB_USER",     "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "3306")
DB_NAME     = os.getenv("DB_NAME",     "finance_tracker")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

#  the low-level connection to MySQL 
engine = create_engine(
    DATABASE_URL,
    echo=False,          
    pool_pre_ping=True, 
)

# SessionLocal: a factory that creates new DB sessions 
SessionLocal = sessionmaker(
    autocommit=False,   
    autoflush=False,
    bind=engine,
)

# Base: all ORM models inherit from this 
Base = declarative_base()


def get_db():
   
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
