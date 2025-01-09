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
        
    def fetch_image(self, image_url, verbose=False):
        response = requests.get(image_url)
            
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        elif verbose:
            print(f"Failed to fetch image from {image_url}")


