# prompts/urls.py

from django.urls import path
from . import views

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

    # ─── Copy & Save ──────────────────────────────────────────────────────
    path('api/prompts/<int:pk>/copy/', views.copy_prompt,   name='copy_prompt'),
    path('api/save/',                  views.save_prompt,   name='save_prompt'),
    path('api/save/<int:pk>/delete/',  views.unsave_prompt, name='unsave_prompt'),
    path('api/saved/check/<int:pk>/',  views.check_saved,   name='check_saved'),
]