from datetime import datetime
from typing import Dict, Any, List
from rest_framework.exceptions import ValidationError

class FilterValidator:
    VALID_STATUSES = ['IN_STOCK', 'OUT_OF_STOCK']
    
    @staticmethod
    def validate_category(category_name: str, valid_categories: List[str]) -> None:
        if category_name not in valid_categories:
            raise ValidationError({
                'category_name': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
            })

    @staticmethod
    def validate_currency(currency: str, valid_currencies: List[str]) -> None:
        if currency not in valid_currencies:
            raise ValidationError({
                'currency': f'Invalid currency. Must be one of: {", ".join(valid_currencies)}'
            })

    @staticmethod
    def validate_price_range(min_price: float, max_price: float, currency: str) -> None:
        if not currency:
            raise ValidationError({
                'currency': 'Currency must be specified when using price filters'
            })
        
        errors = {}
        if min_price < 0:
            errors['min_current_price'] = 'Minimum price cannot be negative'
        if max_price < 0:
            errors['max_current_price'] = 'Maximum price cannot be negative'
        if min_price > max_price:
            errors['min_current_price'] = 'Minimum price cannot be greater than maximum price'
            errors['max_current_price'] = 'Maximum price cannot be less than minimum price'
        
        if errors:
            raise ValidationError(errors)

    @staticmethod
    def validate_update_date(date_str: str) -> None:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValidationError({
                'update_date': 'Invalid date format. Use YYYY-MM-DD'
            })

    @staticmethod
    def validate_shop(shop_name: str, valid_shops: List[str]) -> None:
        if shop_name not in valid_shops:
            raise ValidationError({
                'shop_name': f'Invalid shop name. Must be one of: {", ".join(valid_shops)}'
            })

    @staticmethod
    def validate_status(status: str) -> None:
        if status and status not in FilterValidator.VALID_STATUSES:
            raise ValidationError({
                'status': f'Invalid status. Must be one of: {", ".join(FilterValidator.VALID_STATUSES)}'
            })

    @staticmethod
    def validate_region(region: str, valid_regions: List[str]) -> None:
        if region not in valid_regions:
            raise ValidationError({
                'region': f'Invalid region. Must be one of: {", ".join(valid_regions)}'
            })

    @staticmethod
    def validate_off_percent(off_percent: float) -> None:
        if not (0 <= off_percent <= 100):
            raise ValidationError({
                'off_percent': 'Discount percentage must be between 0 and 100'
            })