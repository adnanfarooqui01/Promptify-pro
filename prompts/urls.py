# prompts/urls.py

from django.urls import path
from . import views
from . import api_views

app_name = 'prompts'

urlpatterns = [
    # ─── Template Views ───────────────────────────────────────────────────
    path('', views.home, name='home'),
    path('prompt/<int:pk>/', views.prompt_detail, name='detail'),
    path('profile/', views.profile, name='profile'),
    path('generate/', views.generate, name='generate'),

    # ─── Infinite Scroll ──────────────────────────────────────────────────
    path('api/prompts/load-more/', views.load_more_prompts, name='load_more'),
    path('api/saved/load-more/',   views.load_more_saved,   name='load_more_saved'),

    # ─── DRF APIs (single source of truth) ───────────────────────────────
    path('api/v1/prompts/<int:pk>/',
         api_views.PromptDetailAPIView.as_view(),
         name='api_prompt_detail'),

    path('api/v1/prompts/<int:pk>/copy/',
         api_views.CopyPromptAPIView.as_view(),
         name='api_copy_prompt'),

    path('api/v1/save/',
         api_views.SavePromptAPIView.as_view(),
         name='api_save_prompt'),

    path('api/v1/save/<int:pk>/',
         api_views.UnsavePromptAPIView.as_view(),
         name='api_unsave_prompt'),
]