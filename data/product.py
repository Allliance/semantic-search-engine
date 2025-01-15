

MANDATORY_FILEDS = ['id', 'images']

class Product:
    def __init__(self, product_dict):
        # Validate required fields
        if not all(field in product_dict for field in MANDATORY_FILEDS):
            raise ValueError(f"Missing mandatory fields. Required fields: {MANDATORY_FILEDS}")
            
        # Store the entire dictionary as meta_data
        self.meta_data = product_dict
        
        # Set individual fields from meta_data
        self.id = self.meta_data['id']
        self.image_urls = self.meta_data['images']
        self.recently_indexed = False