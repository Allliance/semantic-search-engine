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

def get_enums() -> Dict[str, List[str]]:
    # Implement fetching enums from backend
    response = requests.get(f"{settings.DATA_SERVICE_URL}/enums")
    response.raise_for_status()
    return response.json()

class SearchPageView(TemplateView):
    template_name = 'search/page.html'
    
    def get_context_data(self, **kwargs):
        enums = get_enums()
        context = super().get_context_data(**kwargs)
        context.update({
        'categories': enums.get('categories'),
        'currencies': enums.get('currencies'),
        'shops': enums.get('shops'),
        'regions': enums.get('regions'),
        })
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
            
            # Test handling
            if query == 'test':
                with open("test_products.json") as f:
                    return Response(json.load(f))
            
            # Create data dictionary for serializer
            data = {
                'query': query,
                'category_name': request.GET.get('category_name'),
                'currency': request.GET.get('currency'),
                'min_current_price': request.GET.get('min_current_price'),
                'max_current_price': request.GET.get('max_current_price'),
                'update_date': request.GET.get('update_date'),
                'shop_name': request.GET.get('shop_name'),
                'status': request.GET.get('status'),
                'region': request.GET.get('region'),
                'off_percent': request.GET.get('off_percent')
            }
            
            # Convert string values to appropriate types
            if data['min_current_price']:
                data['min_current_price'] = float(data['min_current_price'])
            if data['max_current_price']:
                data['max_current_price'] = float(data['max_current_price'])
            if data['off_percent']:
                data['off_percent'] = float(data['off_percent'])
            
            log_search_request(f"Request parameters: {data}")
            
            serializer = SearchRequestSerializer(data=data)
            
            if not serializer.is_valid():
                return Response(
                    serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get validated data
            validated_data = serializer.validated_data
            
            # Validate individual fields against backend data
            self.validate_fields(validated_data)
            
            # Prepare filters for data service
            data_service_filters = self.prepare_filters_for_data_service(validated_data)
            
            # Call the data service
            requests.get(f"{settings.DATA_SERVICE_URL}/health")
            
            response = requests.post(
                f"{settings.DATA_SERVICE_URL}/query",
                json={
                    "query": validated_data['query'],
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

    def validate_fields(self, validated_data: Dict[str, Any]) -> None:
        """Validate individual fields against backend data"""
        errors = {}

        # Get valid options from backend
        
        
        enums = get_enums()
        valid_categories = enums.get('categories')
        valid_currencies = enums.get('currencies')
        valid_shops = enums.get('shops')
        valid_regions = enums.get('regions')

        if category_name := validated_data.get('category_name'):
            try:
                FilterValidator.validate_category(category_name, valid_categories)
            except ValidationError as e:
                errors['category_name'] = e.detail

        if currency := validated_data.get('currency'):
            try:
                FilterValidator.validate_currency(currency, valid_currencies)
            except ValidationError as e:
                errors['currency'] = e.detail

        if shop_name := validated_data.get('shop_name'):
            try:
                FilterValidator.validate_shop(shop_name, valid_shops)
            except ValidationError as e:
                errors['shop_name'] = e.detail

        if region := validated_data.get('region'):
            try:
                FilterValidator.validate_region(region, valid_regions)
            except ValidationError as e:
                errors['region'] = e.detail

        if status := validated_data.get('status'):
            try:
                FilterValidator.validate_status(status)
            except ValidationError as e:
                errors['status'] = e.detail

        if update_date := validated_data.get('update_date'):
            try:
                FilterValidator.validate_update_date(update_date)
            except ValidationError as e:
                errors['update_date'] = e.detail

        if errors:
            raise ValidationError(errors)

    def prepare_filters_for_data_service(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare filters in the format expected by the data service"""
        prepared_filters = {}
        
        if category_name := validated_data.get('category_name'):
            prepared_filters['category'] = category_name
        
        if (validated_data.get('min_current_price') is not None or 
            validated_data.get('max_current_price') is not None):
            prepared_filters['price'] = {
                'min': validated_data.get('min_current_price', 0),
                'max': validated_data.get('max_current_price', float('inf')),
                'currency': validated_data['currency']
            }
        
        if update_date := validated_data.get('update_date'):
            prepared_filters['update_date'] = update_date
        
        if shop_name := validated_data.get('shop_name'):
            prepared_filters['shop'] = shop_name
        
        if status := validated_data.get('status'):
            prepared_filters['status'] = status
        
        if region := validated_data.get('region'):
            prepared_filters['region'] = region
        
        if off_percent := validated_data.get('off_percent'):
            prepared_filters['discount'] = off_percent
        
        return prepared_filters
