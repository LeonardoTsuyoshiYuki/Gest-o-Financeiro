from django.contrib import admin
from .models import InvoiceImport

@admin.register(InvoiceImport)
class InvoiceImportAdmin(admin.ModelAdmin):
    list_display = ('carrier', 'city', 'month', 'year', 'due_date', 'total_value', 'status', 'created_at')
    list_filter = ('carrier', 'status', 'year')
    search_fields = ('carrier', 'city', 'invoice_number')
    readonly_fields = ('file_hash', 'created_at', 'updated_at')
