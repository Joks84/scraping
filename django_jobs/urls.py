from django.urls import path
from . import views

app_name = "django_jobs"

urlpatterns = [
    path('', views.Homepage.as_view(), name='homepage'),
    path('<int:pk>/', views.CompanyDetailView.as_view(), name='company-detail'),
    path('search_jobs/', views.SearchViewSet.as_view(), name='search'),
]