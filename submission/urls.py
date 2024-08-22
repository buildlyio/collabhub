from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_link, name='generate_link'),
    path('submit/<str:unique_url>/', views.submission_form, name='submission_form'),
]
