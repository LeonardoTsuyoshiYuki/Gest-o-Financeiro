from django.urls import path
from .views import TriggerInvoiceImportView, InvoiceUploadView, InvoiceDownloadView, InvoiceInboxView, InvoiceConfirmView

urlpatterns = [
    path('import/trigger/', TriggerInvoiceImportView.as_view(), name='invoice-import-trigger'),
    path('invoices/upload/', InvoiceUploadView.as_view(), name='invoice-upload'),
    path('invoices/<int:pk>/download/', InvoiceDownloadView.as_view(), name='invoice-download'),
    path('invoices/inbox/', InvoiceInboxView.as_view(), name='invoice-inbox'),
    path('invoices/<int:pk>/confirm/', InvoiceConfirmView.as_view(), name='invoice-confirm'),
]
