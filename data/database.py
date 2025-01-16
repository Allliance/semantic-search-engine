from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv

Base = declarative_base()

load_dotenv()
# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://postgres@localhost:5432/products_db")


def init_database():
    global DATABASE_URL
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create database if it doesn't exist
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Created database: {engine.url}")
    else:
        print(f"Database already exists: {engine.url}")