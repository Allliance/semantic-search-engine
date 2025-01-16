from sqlalchemy import Column, String, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

Base = declarative_base()


class ProductModel(Base):
    __tablename__ = 'products'
    
    id = Column(String, primary_key=True)
    image_urls = Column(JSON)
    meta_data = Column(JSON)
    recently_indexed = Column(Boolean, default=False)
    
    def to_dict(self):
        return self.meta_data
    
    def update_from_dict(self, data):
        """Update the product model from a dictionary"""
        self.image_urls = data.get('images', self.image_urls)
        self.meta_data = data
        self.recently_indexed = False


load_dotenv()
# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://postgres@localhost:5432/products_db")

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
