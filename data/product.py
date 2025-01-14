import json
import os
from PIL import Image
import requests # type: ignore
from io import BytesIO
import loggers
from collections import defaultdict

# Get the logger for the search app

MANDATORY_FILEDS = ['id', 'images']

class Product:
    def __init__(self, product_dict):
        self.id = product_dict['id']
        self.image_urls = product_dict['images']
        
        self.meta_data = product_dict
        self.recently_indexed = False
        
    def fetch_image(self, image_url, verbose=False):
        response = requests.get(image_url)
            
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        elif verbose:
            print(f"Failed to fetch image from {image_url}")
    
    def to_json(self):
        return self.meta_data
    
    def to_dict(self):
        return self.meta_data

def load_products_data(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
            products_data = [{k: v for k, v in p.items() if v is not None} for p in products_data]
        
        return products_data

# To be caches enums
ENUMS = ['category_name', 'shop_name', 'region', 'currency']
 
class ProductManager:
    def __init__(self,
                 products_file,
                 verbose_error=True):
        logger = loggers.get_product_manager_logger()
        self.products_file = products_file
        self.products = {}
        
        failed_products = 0
        products_data = load_products_data(products_file)
        
        for product_data in products_data:
            try:
                self.add_product(product_dict=product_data)
            except Exception as e:
                failed_products += 1
                if verbose_error:
                    logger.info(f"Failed to load product {product_data.get('id')}: {str(e)}")
        
        print("Products loaded successfully")
        print("Failed products: ", failed_products)
        
        # to be cached enums
        enum_caches = defaultdict(set)
        
        for product in self.products.values():
            for enum in ENUMS:
                if enum in product.meta_data:
                    enum_caches[f"all_{enum}"].add(product.meta_data[enum])
            
        self.enum_caches = enum_caches
    
    def add_product(self, product=None, product_dict=None):
        assert product or product_dict, "Either product or product_dict must be provided"
        
        
        if product_dict is None:
            product_dict = product.meta_data
        
        try:
            new_product = Product(product_dict)
        except Exception as e:
            raise Exception(f"Invalid product data. Reason: {str(e)}")
        
            
        if new_product.id in self.products:
            raise Exception(f"Product with id {new_product.id} already exists")
        
        self.products[product_dict['id']] = new_product
        # update enum cache
        for enum in ENUMS:
            if enum in product_dict:
                self.enum_caches[f"all_{enum}"].add(product_dict[enum])
     
    def get_all_products(self):
         return self.products.values()
    
    def get_products_by_id(self, products_id):
        if not isinstance(products_id, list):
            products_id = [products_id]
    
        return [self.products[pid] for pid in products_id]    
    
    def product_exists(self, product_id):
        return product_id in self.products
    
    # Can be implemented later if needed
    def crawl_products(self, url):
        pass
    