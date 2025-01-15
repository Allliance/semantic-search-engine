from sqlalchemy import Column, Integer, String, JSON, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class ProductModel(Base):
    __tablename__ = 'products'
    
    id = Column(String, primary_key=True)
    image_urls = Column(JSON)
    meta_data = Column(JSON)
    recently_indexed = Column(Boolean, default=False)
    
    def to_dict(self):
        return self.meta_data

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://postgres:postgres@postgres:5432/products_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()