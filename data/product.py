import json
import os
from PIL import Image
import requests # type: ignore
from io import BytesIO


class Product:
    def __init__(self, product_dict):
        self.id = product_dict['id']
        self.name = product_dict['name']
        self.description = product_dict['description']
        self.image_urls = product_dict['images']
        self.meta_data = product_dict
        self.recently_indexed = False
        
    def fetch_image(self, image_url, verbose=False):
        response = requests.get(image_url)
            
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        elif verbose:
            print(f"Failed to fetch image from {image_url}")


class ProductManager:
    def __init__(self, products_file):
        self.products_file = products_file
        self.products = self.load_products()
    
    def add_product(self, product=None, product_dict=None):
        assert product or product_dict, "Either product or product_dict must be provided"
        if product_dict is None:
            product_dict = product.meta_data
            
        if product_dict['id'] in self.products:
            raise Exception(f"Product with id {product.id} already exists")
        
        self.products[product_dict['id']] = Product(product_dict)
     
    def get_all_products(self):
         return self.products.values()
     
    def load_products(self):
        with open(self.products_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
            products_data = [{k: v for k, v in p.items() if v is not None} for p in products_data]
        
        return {p['id']: Product(p) for p in products_data}
    
    def get_products_by_id(self, products_id):
        if not isinstance(products_id, list):
            products_id = [products_id]
    
        return [self.products[pid] for pid in products_id]    
    
    def product_exists(self, product_id):
        return product_id in self.products
    
    # Can be implemented later if needed
    def crawl_products(self, url):
        pass
    