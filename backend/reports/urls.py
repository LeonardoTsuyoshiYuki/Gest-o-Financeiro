from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, CategoryViewSet, DashboardStatusSummaryView, DashboardTimelineView, DashboardCarrierView

router = DefaultRouter()
router.register(r'reports', ReportViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('dashboard/status-summary/', DashboardStatusSummaryView.as_view(), name='dashboard-status-summary'),
    path('dashboard/timeline/', DashboardTimelineView.as_view(), name='dashboard-timeline'),
    path('dashboard/carrier-summary/', DashboardCarrierView.as_view(), name='dashboard-carrier-summary'),
    path('', include(router.urls)),
]
