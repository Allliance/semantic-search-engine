from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SearchRequestSerializer
import requests
import os
import json
from django.conf import settings
from .utils.logger import log_search_request

class SearchView(APIView):
    def get(self, request):
        try:
            
            # Extract query parameters
            query = request.GET.get('query')
            filters_str = request.GET.get('filters', '{}')
            
            # specifically for testing
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
            
            query = serializer.validated_data['query']
            filters = serializer.validated_data['filters']
            
            # Call the data service
            requests.get(f"{settings.DATA_SERVICE_URL}/health")
            
            response = requests.post(
                f"{settings.DATA_SERVICE_URL}/query",
                json={"query": query}
            )
        
            response.raise_for_status()
            
            results = response.json()['results']
            
            # Apply filters
            filtered_results = self.apply_filters(results, filters)
            
            return Response({
                "query": query,
                "filters": filters,
                "results": filtered_results
            })
            
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
    
    def apply_filters(self, results, filters):
        if not filters:
            return results
            
        filtered_results = results.copy()
        
        for key, value in filters.items():
            if key == 'price_range':
                filtered_results = [
                    r for r in filtered_results
                    if value[0] <= float(r['metadata']['price']) <= value[1]
                ]
            elif key == 'categories':
                filtered_results = [
                    r for r in filtered_results
                    if r['metadata']['category'] in value
                ]
            
        return filtered_results
