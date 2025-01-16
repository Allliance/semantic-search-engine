from rest_framework import serializers

class StringListField(serializers.ListField):
    child = serializers.CharField()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    category_name = StringListField(required=False, allow_null=True)
    currency = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    min_current_price = serializers.FloatField(required=False, allow_null=True, min_value=0)
    max_current_price = serializers.FloatField(required=False, allow_null=True, min_value=0)
    update_date = serializers.DateField(required=False, allow_null=True)
    shop_name = StringListField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    region = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    off_percent = serializers.FloatField(required=False, allow_null=True, min_value=0, max_value=100)

    def validate(self, data):
        """
        Custom validation for interdependent fields
        """
        if (data.get('min_current_price') is not None or 
            data.get('max_current_price') is not None) and not data.get('currency'):
            raise serializers.ValidationError({
                "currency": "Currency is required when specifying price range"
            })

        if (data.get('min_current_price') is not None and 
            data.get('max_current_price') is not None and 
            data['min_current_price'] > data['max_current_price']):
            raise serializers.ValidationError({
                "min_current_price": "Minimum price cannot be greater than maximum price",
                "max_current_price": "Maximum price cannot be less than minimum price"
            })

        return data