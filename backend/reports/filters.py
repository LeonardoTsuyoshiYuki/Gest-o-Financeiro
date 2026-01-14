import django_filters
from .models import Report

class ReportFilter(django_filters.FilterSet):
    min_value = django_filters.NumberFilter(field_name="total_value", lookup_expr='gte')
    max_value = django_filters.NumberFilter(field_name="total_value", lookup_expr='lte')
    start_date = django_filters.DateFilter(field_name="reference_date", lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name="reference_date", lookup_expr='lte')
    category_name = django_filters.CharFilter(field_name="category__name", lookup_expr='icontains')

    class Meta:
        model = Report
        fields = ['status', 'category', 'min_value', 'max_value', 'start_date', 'end_date']
