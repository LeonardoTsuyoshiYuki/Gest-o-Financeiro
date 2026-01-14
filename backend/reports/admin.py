from django.contrib import admin
from .models import Category, Report

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'total_value', 'status', 'reference_date', 'created_at')
    list_filter = ('status', 'category', 'reference_date')
    search_fields = ('title', 'category__name')
    ordering = ('-reference_date',)
