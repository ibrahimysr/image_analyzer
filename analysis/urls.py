from django.urls import path
from . import views

urlpatterns = [
    path('', views.analyze_image_view, name='analyze'), 
    path('history/', views.analysis_history_view, name='history'),
]