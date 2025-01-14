import unittest
import requests
import json
from datetime import datetime, timedelta

class BackendTester(unittest.TestCase):
    BASE_URL = "http://localhost:5000"
    
    def setUp(self):
        # Check if service is healthy before running tests
        try:
            response = requests.get(f"{self.BASE_URL}/health")
            self.assertEqual(response.status_code, 200)
        except requests.RequestException:
            self.fail("Backend service is not running")

    def test_basic_search(self):
        """Test basic search without filters"""
        data = {
            "query": "blue jeans"
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        self.assertIsInstance(results, list)

    def test_empty_query(self):
        """Test search with empty query"""
        data = {
            "query": ""
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 400)

    def test_category_filter(self):
        """Test category filter"""
        data = {
            "query": "shirt",
            "filters": {
                "category_name": "Clothing"
            }
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        for result in results:
            self.assertEqual(result.get('category_name'), "Clothing")

    def test_price_range_filter(self):
        """Test price range filter"""
        min_price = 50
        max_price = 200
        data = {
            "query": "shoes",
            "filters": {
                "min_current_price": min_price,
                "max_current_price": max_price,
                "currency": "USD"
            }
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        for result in results:
            price = float(result.get('current_price', 0))
            self.assertTrue(min_price <= price <= max_price)
            self.assertEqual(result.get('currency'), "USD")

    def test_date_filter(self):
        """Test update date filter"""
        test_date = datetime.now() - timedelta(days=30)
        date_str = test_date.strftime("%Y-%m-%d")
        data = {
            "query": "laptop",
            "filters": {
                "update_date": date_str
            }
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 200)

    def test_shop_filter(self):
        """Test shop name filter"""
        data = {
            "query": "phone",
            "filters": {
                "shop_name": "Amazon"
            }
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        for result in results:
            self.assertEqual(result.get('shop_name'), "Amazon")

    def test_multiple_filters(self):
        """Test combination of multiple filters"""
        data = {
            "query": "sneakers",
            "filters": {
                "category_name": "Shoes",
                "min_current_price": 50,
                "max_current_price": 200,
                "currency": "USD",
                "shop_name": "Nike",
                "status": "IN_STOCK"
            }
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 200)

    def test_discount_filter(self):
        """Test discount percentage filter"""
        min_discount = 20
        data = {
            "query": "jacket",
            "filters": {
                "off_percent": min_discount
            }
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        for result in results:
            self.assertGreaterEqual(float(result.get('off_percent', 0)), min_discount)

    def test_region_filter(self):
        """Test region filter"""
        data = {
            "query": "book",
            "filters": {
                "region": "North America"
            }
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        for result in results:
            self.assertEqual(result.get('region'), "North America")

    def test_status_filter(self):
        """Test product status filter"""
        data = {
            "query": "headphones",
            "filters": {
                "status": "IN_STOCK"
            }
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 200)
        results = response.json().get('results', [])
        for result in results:
            self.assertEqual(result.get('status'), "IN_STOCK")

    def test_invalid_price_range(self):
        """Test invalid price range (min > max)"""
        data = {
            "query": "watch",
            "filters": {
                "min_current_price": 200,
                "max_current_price": 100,
                "currency": "USD"
            }
        }
        response = requests.post(f"{self.BASE_URL}/query", json=data)
        self.assertEqual(response.status_code, 400)

    def test_product_indexing(self):
        """Test product indexing endpoint"""
        test_product = {
            "id": "test_product_001",
            "name": "Test Product",
            "description": "This is a test product",
            "images": ["https://example.com/test-image.jpg"],
            "category_name": "Test Category",
            "currency": "USD",
            "current_price": 99.99,
            "update_date": datetime.now().strftime("%Y-%m-%d"),
            "shop_name": "Test Shop",
            "status": "IN_STOCK",
            "region": "Test Region",
            "off_percent": 10
        }
        response = requests.post(f"{self.BASE_URL}/index_product", json=test_product)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main(verbosity=2)
