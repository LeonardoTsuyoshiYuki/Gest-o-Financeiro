from rest_framework import serializers
from .models import Category, Report

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    invoice_source_id = serializers.PrimaryKeyRelatedField(read_only=True, source='invoice_source')
    confidence_score = serializers.IntegerField(source='invoice_source.confidence_score', read_only=True, allow_null=True)

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
