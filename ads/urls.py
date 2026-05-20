from django.urls import path
from . import views, api_views

app_name = 'ads'

urlpatterns = [
    # Template views (only rendering empty pages)
    path('', views.ads_home, name='home'),
    path('detail/<int:pk>/', views.ad_detail, name='detail'),
    path('saved/', views.my_saved_ads, name='saved'),
    
    # API endpoints
    path('api/categories/', api_views.AdCategoryListAPIView.as_view(), name='api-categories'),
    path('api/list/', api_views.AdListAPIView.as_view(), name='api-list'),
    path('api/detail/<int:pk>/', api_views.AdDetailAPIView.as_view(), name='api-detail'),
    path('api/<int:pk>/copy/', api_views.CopyAdPromptAPIView.as_view(), name='api-copy'),
    path('api/save/', api_views.SaveAdAPIView.as_view(), name='api-save'),
    path('api/unsave/<int:pk>/', api_views.UnsaveAdAPIView.as_view(), name='api-unsave'),
    path('api/my-saved/', api_views.MySavedAdsAPIView.as_view(), name='api-my-saved'),
]