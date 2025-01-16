from meilisearch import Client
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv
from product import Product

load_dotenv()

class TextSearchManager:
    def __init__(self):
        # Initialize MeiliSearch client with cloud credentials
        self.client = Client(
            os.environ.get('MEILISEARCH_HOST'),
            os.environ.get('MEILISEARCH_API_KEY')
        )
        self.index = self.client.index('products')
        
        # Set up filterable attributes
        self.index.update_filterable_attributes([
            'category_name',
            'currency',
            'current_price',
            'update_date',
            'shop_name',
            'status',
            'region',
            'off_percent'
        ])

    def index_products(self, products) -> None:
        """Index a single product if not already indexed."""
        # Prepare document for indexing
        documents = []
        for product in products:
            documents.append({
                'id': product.id,
                'name': product.meta_data.get('name', ''),
                'description': product.meta_data.get('description', ''),
                'category_name': product.meta_data.get('category_name', ''),
                'currency': product.meta_data.get('currency'),
                'current_price': float(product.meta_data.get('current_price', 0)),
                'update_date': product.meta_data.get('update_date'),
                'shop_name': product.meta_data.get('shop_name', ''),
                'status': product.meta_data.get('status'),
                'region': product.meta_data.get('region'),
                'off_percent': float(product.meta_data.get('off_percent', 0))
            })
        
        # Add document to index
        self.index.add_documents(documents)

    def search_products(self, keyword: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search products with keyword and filters."""
        # Build filter string
        filter_conditions = []
        
        if filters.get('category_name'):
            categories = filters['category_name']
            if isinstance(categories, list) and categories[0]:  # Check if list is not empty
                category_conditions = [f"category_name = '{cat}'" for cat in categories]
                filter_conditions.append(f"({' OR '.join(category_conditions)})")
        
        if filters.get('shop_name'):
            shops = filters['shop_name']
            if isinstance(shops, list) and shops[0]:  # Check if list is not empty
                shop_conditions = [f"shop_name = '{shop}'" for shop in shops]
                filter_conditions.append(f"({' OR '.join(shop_conditions)})")

        if filters.get('currency'):
            filter_conditions.append(f"currency = '{filters['currency']}'")
            
        if filters.get('min_current_price'):
            filter_conditions.append(
                f"current_price >= {float(filters['min_current_price'])}"
            )
            
        if filters.get('max_current_price'):
            filter_conditions.append(
                f"current_price <= {float(filters['max_current_price'])}"
            )
            
        if filters.get('update_date'):
            filter_conditions.append(f"update_date = '{filters['update_date']}'")
            
        if filters.get('status'):
            filter_conditions.append(f"status = '{filters['status']}'")
            
        if filters.get('region'):
            filter_conditions.append(f"region = '{filters['region']}'")
            
        if filters.get('off_percent'):
            filter_conditions.append(
                f"off_percent = {float(filters['off_percent'])}"
            )

        # Combine all filters with AND
        filter_string = ' AND '.join(filter_conditions) if filter_conditions else None

        # Perform search
        search_results = self.index.search(
            keyword,
            {
                'filter': filter_string,
                'attributesToRetrieve': ['*']
            }
        )
        
        return search_results