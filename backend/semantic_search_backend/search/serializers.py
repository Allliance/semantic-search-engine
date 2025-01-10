# backend/search/serializers.py
from rest_framework import serializers

class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    filters = serializers.DictField(required=False, default=dict)

