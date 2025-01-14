from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SearchRequestSerializer
import requests
import json
from django.conf import settings
from .utils.logger import log_search_request
from .validators import FilterValidator
from rest_framework.exceptions import ValidationError
from typing import Dict, Any, List

class SearchPageView(TemplateView):
    template_name = 'search/page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any initial context data needed for the template
        context['initial_data'] = {
            'query': '',
            'filters': {}
        }
        return context

class SearchView(APIView):
    def get(self, request):
        try:
            # Extract query parameters
            query = request.GET.get('query')
            filters_str = request.GET.get('filters', '{}')
            
            # Test handling
            if query == 'test':
                with open("test_products.json") as f:
                    return Response(json.load(f))
            
            try:
                filters = json.loads(filters_str)
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid filters JSON format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate filters
            self.validate_filters(filters)
            
            # Create data dictionary for serializer
            data = {
                'query': query,
                'filters': filters
            }
            
            log_search_request(f"Request parameters: {data}")
            
            serializer = SearchRequestSerializer(data=data)
            
            if not serializer.is_valid():
                return Response(
                    serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get validated data
            query = serializer.validated_data['query']
            filters = serializer.validated_data['filters']
            
            # Prepare filters for data service
            data_service_filters = self.prepare_filters_for_data_service(filters)
            
            # Call the data service
            requests.get(f"{settings.DATA_SERVICE_URL}/health")
            
            response = requests.post(
                f"{settings.DATA_SERVICE_URL}/query",
                json={
                    "query": query,
                    "filters": data_service_filters
                }
            )
        
            response.raise_for_status()
                
            results = response.json()['results']
            
        
            return Response(results)
            
        except ValidationError as e:
            return Response(
                e.detail,
                status=status.HTTP_400_BAD_REQUEST
            )
        except requests.RequestException as e:
            return Response(
                {"error": f"Data service error: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def validate_filters(self, filters: Dict[str, Any]) -> None:
        """Validate all filter fields"""
        if not filters:
            return

        # Get valid options from backend (you'll need to implement these methods)
        valid_categories = self.get_valid_categories()
        valid_currencies = self.get_valid_currencies()
        valid_shops = self.get_valid_shops()
        valid_regions = self.get_valid_regions()

        # Validate individual filters
        if 'category_name' in filters:
            FilterValidator.validate_category(filters['category_name'], valid_categories)
        
        if 'currency' in filters:
            FilterValidator.validate_currency(filters['currency'], valid_currencies)
        
        if 'min_current_price' in filters or 'max_current_price' in filters:
            min_price = float(filters.get('min_current_price', 0))
            max_price = float(filters.get('max_current_price', float('inf')))
            currency = filters.get('currency')
            FilterValidator.validate_price_range(min_price, max_price, currency)
        
        if 'update_date' in filters:
            FilterValidator.validate_update_date(filters['update_date'])
        
        if 'shop_name' in filters:
            FilterValidator.validate_shop(filters['shop_name'], valid_shops)
        
        if 'status' in filters:
            FilterValidator.validate_status(filters['status'])
        
        if 'region' in filters:
            FilterValidator.validate_region(filters['region'], valid_regions)
        
        if 'off_percent' in filters:
            FilterValidator.validate_off_percent(float(filters['off_percent']))

    def prepare_filters_for_data_service(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare filters in the format expected by the data service"""
        prepared_filters = {}
        
        if 'category_name' in filters:
            prepared_filters['category'] = filters['category_name']
        
        if 'min_current_price' in filters or 'max_current_price' in filters:
            prepared_filters['price'] = {
                'min': float(filters.get('min_current_price', 0)),
                'max': float(filters.get('max_current_price', float('inf'))),
                'currency': filters['currency']
            }
        
        if 'update_date' in filters:
            prepared_filters['update_date'] = filters['update_date']
        
        if 'shop_name' in filters:
            prepared_filters['shop'] = filters['shop_name']
        
        if 'status' in filters:
            prepared_filters['status'] = filters['status']
        
        if 'region' in filters:
            prepared_filters['region'] = filters['region']
        
        if 'off_percent' in filters:
            prepared_filters['discount'] = float(filters['off_percent'])
        
        return prepared_filters

    # Methods to fetch valid options from backend
    def get_valid_categories(self) -> List[str]:
        # Implement fetching categories from backend
        response = requests.get(f"{settings.DATA_SERVICE_URL}/categories")
        response.raise_for_status()
        return response.json()['categories']

    def get_valid_currencies(self) -> List[str]:
        # Implement fetching currencies from backend
        response = requests.get(f"{settings.DATA_SERVICE_URL}/currencies")
        response.raise_for_status()
        return response.json()['currencies']

    def get_valid_shops(self) -> List[str]:
        # Implement fetching shops from backend
        response = requests.get(f"{settings.DATA_SERVICE_URL}/shops")
        response.raise_for_status()
        return response.json()['shops']

    def get_valid_regions(self) -> List[str]:
        # Implement fetching regions from backend
        response = requests.get(f"{settings.DATA_SERVICE_URL}/regions")
        response.raise_for_status()
        return response.json()['regions']