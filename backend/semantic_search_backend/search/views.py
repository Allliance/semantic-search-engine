from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SearchRequestSerializer
import requests
import os
from django.conf import settings

class SearchView(APIView):
    def post(self, request):
        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        filters = serializer.validated_data['filters']
        
        try:
            # Call the data service
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
            # Add more filter conditions as needed
            
        return filtered_results