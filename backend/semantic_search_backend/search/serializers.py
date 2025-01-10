# backend/search/serializers.py
from rest_framework import serializers
from .models import SearchHistory

class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    filters = serializers.DictField(required=False, default=dict)

