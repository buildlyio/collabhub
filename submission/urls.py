from django.urls import path
from . import views

app_name = 'submission'

urlpatterns = [
    path('generate/', views.generate_link, name='generate_link'),
    path('submit/<str:unique_url>/', views.submission_form, name='submission_form'),
    path('delete/<str:unique_url>/', views.delete_submission_link, name='delete_submission_link'),
    path('update_resource_progress/', views.update_resource_progress, name='update_resource_progress'),
    path('get_resource_progress/', views.get_resource_progress, name='get_resource_progress'),
]
