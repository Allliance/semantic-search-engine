from sqlalchemy.orm import Session
from typing import List, Dict, Set, Optional
from collections import defaultdict
import json
from models import ProductModel
from sqlalchemy import distinct
from product import Product

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
            try:
                self.add_product(product_dict=product_data)
            except Exception as e:
                print(f"Failed to load product {product_data.get('id')}: {str(e)}")

    def get_enum_values(self, enum_name: str) -> List[str]:
        """Get unique values for a specific enum field from the database"""
        return [
            value[0] for value in 
            self.db.query(distinct(ProductModel.meta_data[enum_name]))
            .filter(ProductModel.meta_data[enum_name].isnot(None))
            .all()
        ]


    def add_product(self, product: Optional[Product] = None, product_dict: Optional[Dict] = None) -> None:
        if product_dict is None and product is not None:
            product_dict = product.meta_data
        
        if product_dict is None:
            raise ValueError("Either product or product_dict must be provided")

        db_product = ProductModel(
            id=product_dict['id'],
            image_urls=product_dict['images'],
            meta_data=product_dict,
            recently_indexed=False
        )
        
        self.db.add(db_product)
        self.db.commit()

    def get_all_products(self) -> List[ProductModel]:
        return self.db.query(ProductModel).all()

    def get_products_by_id(self, products_id: List[str]) -> List[ProductModel]:
        if not isinstance(products_id, list):
            products_id = [products_id]
        return self.db.query(ProductModel).filter(ProductModel.id.in_(products_id)).all()

    def product_exists(self, product_id: str) -> bool:
        return self.db.query(ProductModel).filter(ProductModel.id == product_id).first() is not None