from sqlalchemy.orm import Session
from typing import List, Dict, Set, Optional
from collections import defaultdict
import json
from models import ProductModel, SessionLocal
from sqlalchemy import distinct, text
from product import Product
from sqlalchemy.exc import SQLAlchemyError

def load_products_data(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as f:
        products_data = json.load(f)
        return [{k: v for k, v in p.items() if v is not None} for p in products_data]

class ProductManager:
    def __init__(self, db: Session, products_file: Optional[str] = None):
        self.db = db
        if products_file:
            self._load_initial_data(products_file)

    def _load_initial_data(self, products_file: str) -> None:
        products_data = load_products_data(products_file)
        for product_data in products_data:
            # Create a new session for each product
            with SessionLocal() as session:
                try:
                    self.add_product(product_dict=product_data, session=session)
                except Exception as e:
                    print(f"Failed to load product {product_data.get('id')}: {str(e)}")
                    session.rollback()
    
    
    def get_enum_values(self, enum_name: str) -> List[str]:
        """
        Get unique values for a specific enum field from the database,
        handling cases where the field might not exist in meta_data
        """
        try:
            # Using proper string quoting for the JSON field access
            query = text("""
                SELECT DISTINCT meta_data->>:enum_name
                FROM products
                WHERE meta_data->>:enum_name IS NOT NULL
                  AND meta_data->>:enum_name != 'null'
                  AND meta_data->>:enum_name != ''
            """)
            
            result = self.db.execute(query, {"enum_name": enum_name})
            values = [row[0] for row in result if row[0]]
            return sorted(set(values))  # Remove duplicates and sort
        except Exception as e:
            print(f"Error getting enum values for {enum_name}: {str(e)}")
            return []

    def add_product(self, product: Optional[Product] = None, product_dict: Optional[Dict] = None, session: Optional[Session] = None) -> None:
        """Add or update a product in the database"""
        if product_dict is None and product is not None:
            product_dict = product.meta_data
        
        if product_dict is None:
            raise ValueError("Either product or product_dict must be provided")

        # Use provided session or self.db
        db_session = session or self.db
        
        try:
            # Check if product already exists
            existing_product = db_session.query(ProductModel).filter(
                ProductModel.id == str(product_dict['id'])
            ).first()

            if existing_product:
                # Update existing product
                existing_product.update_from_dict(product_dict)
            else:
                # Create new product
                db_product = ProductModel(
                    id=product_dict['id'],
                    image_urls=product_dict.get('images', []),
                    meta_data=product_dict,
                    recently_indexed=False
                )
                db_session.add(db_product)

            db_session.commit()
            
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            db_session.rollback()
            raise Exception(f"Error adding/updating product: {str(e)}")

    def get_all_products(self) -> List[ProductModel]:
        return self.db.query(ProductModel).all()

    def get_products_by_id(self, products_id: List[str]) -> List[ProductModel]:
        if not isinstance(products_id, list):
            products_id = [products_id]
        return self.db.query(ProductModel).filter(ProductModel.id.in_(products_id)).all()

    def product_exists(self, product_id: str) -> bool:
        return self.db.query(ProductModel).filter(ProductModel.id == str(product_id)).first() is not None
