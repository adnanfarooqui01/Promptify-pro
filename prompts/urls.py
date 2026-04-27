from django.urls import path
from . import views

app_name = 'prompts'

urlpatterns = [
    path('', views.home, name='home'),
    path('prompt/<int:pk>/', views.prompt_detail, name='detail'),
    path('profile/', views.profile, name='profile'),
    path('generate/', views.generate, name='generate'),
    path('api/prompts/load-more/', views.load_more_prompts, name='load_more'),
]