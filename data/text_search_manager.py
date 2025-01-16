from meilisearch import Client
from typing import Dict, List
from fastapi import HTTPException
from product_manager import ProductManager

class TextSearchManager:
    def __init__(self, meilisearch_url: str, master_key: str, index_name: str = "products"):
        self.client = Client(meilisearch_url, master_key)
        self.index_name = index_name
        self.index = self.client.index(index_name)
        
        # Configure searchable attributes
        self.index.update_searchable_attributes([
            'title',
            'description',
            'category_name',
        ])
        
        # Configure filterable attributes
        # self.index.update_filterable_attributes([
        #     'category_name',
        #     'currency',
        #     'current_price',
        #     'update_date',
        #     'shop_name',
        #     'status',
        #     'region',
        #     'off_percent'
        # ])

    async def index_product(self, product_model) -> None:
        """Index a single product"""
        try:
            # Convert SQLAlchemy model to dictionary
            product_dict = product_model.meta_data
            product_dict['id'] = str(product_dict['id'])  # Ensure ID is string
            
            # Add the document to Meilisearch
            self.index.add_documents([product_dict])
        except Exception as e:
            print(f"Error indexing product: {str(e)}")

    async def index_products(self, product_manager: ProductManager) -> None:
        """Index all products from the database"""
        try:
            # Get all products from the database
            products = product_manager.get_all_products()
    
            # Prepare products for indexing
            documents = []
            for product in products:
                product_dict = product.meta_data
                product_dict['id'] = str(product_dict['id'])  # Ensure ID is string
                documents.append(product_dict)
            
            print(documents[:3])
            
            print("going to be added:", len(documents))
            # Batch index products
            if documents:
                self.index.add_documents(documents)
                print("docs added")
                
        except Exception as e:
            print("Error indexing products:", str(e))


    def _build_filter_expression(self, filters: Dict) -> List[str]:
        filter_conditions = []
        
        if not filters:
            return filter_conditions

        if 'category_name' in filters and filters['category_name']:
            categories = filters['category_name']
            if isinstance(categories, str):
                categories = [cat.strip() for cat in categories.split(',')]
            filter_conditions.append(f"category_name IN {categories}")

        if 'shop_name' in filters and filters['shop_name']:
            shops = filters['shop_name']
            if isinstance(shops, str):
                shops = [shop.strip() for shop in shops.split(',')]
            filter_conditions.append(f"shop_name IN {shops}")

        if 'currency' in filters and filters['currency']:
            filter_conditions.append(f"currency = '{filters['currency']}'")

        if 'min_current_price' in filters and filters['min_current_price']:
            filter_conditions.append(f"current_price >= {float(filters['min_current_price'])}")

        if 'max_current_price' in filters and filters['max_current_price']:
            filter_conditions.append(f"current_price <= {float(filters['max_current_price'])}")

        if 'status' in filters and filters['status']:
            filter_conditions.append(f"status = '{filters['status']}'")

        if 'region' in filters and filters['region']:
            filter_conditions.append(f"region = '{filters['region']}'")

        if 'off_percent' in filters and filters['off_percent']:
            filter_conditions.append(f"off_percent >= {float(filters['off_percent'])}")

        if 'update_date' in filters and filters['update_date']:
            filter_conditions.append(f"update_date >= '{filters['update_date']}'")

        return filter_conditions

    async def search(self, keyword: str, filters: Dict = None) -> Dict:
        try:
            search_params = {}
            
            if filters:
                filter_conditions = self._build_filter_expression(filters)
                if filter_conditions:
                    search_params['filter'] = filter_conditions

            # Perform the search
            results = self.index.search(keyword, search_params)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")