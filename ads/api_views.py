from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.db import transaction
from .models import Ad, AdCategory, SavedAd
from .serializers import AdListSerializer, AdDetailSerializer, AdCategorySerializer


class AdCategoryListAPIView(APIView):
    """Get all ad categories"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        categories = AdCategory.objects.all()
        serializer = AdCategorySerializer(categories, many=True)
        return Response({
            'categories': serializer.data
        })


class AdListAPIView(APIView):
    """
    Get ads with pagination (10 per page)
    Query params: ?page=1&category=slug
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = 10
        category_slug = request.GET.get('category', None)
        
        # Query ads
        ads_qs = Ad.objects.select_related('category').prefetch_related('tags')
        
        # Filter by category
        if category_slug:
            ads_qs = ads_qs.filter(category__slug=category_slug)
        
        # Ordering
        ads_qs = ads_qs.order_by('-is_trending', '-created_at')
        
        # Pagination
        total_count = ads_qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        ads = ads_qs[start:end]
        
        # Serialize
        serializer = AdListSerializer(ads, many=True, context={'request': request})
        
        return Response({
            'ads': serializer.data,
            'page': page,
            'page_size': page_size,
            'total': total_count,
            'has_next': end < total_count,
            'has_previous': page > 1
        })


class AdDetailAPIView(APIView):
    """Get single ad detail"""
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        ad = get_object_or_404(Ad, pk=pk)
        serializer = AdDetailSerializer(ad, context={'request': request})
        return Response(serializer.data)


class CopyAdPromptAPIView(APIView):
    """Increment copy counter (atomic)"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        ad = get_object_or_404(Ad, pk=pk)
        
        with transaction.atomic():
            Ad.objects.filter(pk=pk).update(copy_count=F('copy_count') + 1)
            ad.refresh_from_db()
        
        return Response({
            'message': 'Prompt copied!',
            'copy_count': ad.copy_count
        })


class SaveAdAPIView(APIView):
    """Save ad to collection"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        ad_id = request.data.get('ad_id')
        ad = get_object_or_404(Ad, pk=ad_id)
        
        saved, created = SavedAd.objects.get_or_create(
            user=request.user,
            ad=ad
        )
        
        return Response({
            'message': 'Ad saved!' if created else 'Already saved',
            'saved': True,
            'id': saved.id
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class UnsaveAdAPIView(APIView):
    """Remove ad from saved collection"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        saved = get_object_or_404(SavedAd, pk=pk, user=request.user)
        saved.delete()
        
        return Response({
            'message': 'Removed from saved ads',
            'saved': False
        })


class MySavedAdsAPIView(APIView):
    """Get user's saved ads with pagination"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = 10
        
        # Query saved ads
        saved_qs = SavedAd.objects.filter(user=request.user) \
                                  .select_related('ad__category') \
                                  .prefetch_related('ad__tags') \
                                  .order_by('-saved_at')
        
        # Pagination
        total_count = saved_qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        saved_ads = saved_qs[start:end]
        
        # Extract ads and serialize
        ads = [saved.ad for saved in saved_ads]
        serializer = AdListSerializer(ads, many=True, context={'request': request})
        
        return Response({
            'ads': serializer.data,
            'page': page,
            'page_size': page_size,
            'total': total_count,
            'has_next': end < total_count,
            'has_previous': page > 1
        })