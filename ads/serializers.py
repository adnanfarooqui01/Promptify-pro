from rest_framework import serializers
from .models import Ad, AdCategory, AdTag, SavedAd


class AdCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdCategory
        fields = ['id', 'name', 'slug']


class AdTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdTag
        fields = ['id', 'name', 'slug']


class AdListSerializer(serializers.ModelSerializer):
    """Serializer for ads list (homepage)"""
    category = AdCategorySerializer(read_only=True)
    tags = AdTagSerializer(many=True, read_only=True)
    is_saved = serializers.SerializerMethodField()
    saved_id = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = Ad
        fields = [
            'id', 'title', 'description', 'video', 'thumbnail', 
            'category', 'tags', 'copy_count', 'is_trending', 
            'is_saved', 'saved_id', 'created_at'
        ]

    def get_video(self, obj):
        """Return full Cloudinary URL for video"""
        if obj.video:
            return obj.video.url
        return None

    def get_thumbnail(self, obj):
        """Return full Cloudinary URL for thumbnail"""
        if obj.thumbnail:
            return obj.thumbnail.url
        return None
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedAd.objects.filter(user=request.user, ad=obj).exists()
        return False
    
    def get_saved_id(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                saved = SavedAd.objects.get(user=request.user, ad=obj)
                return saved.id
            except SavedAd.DoesNotExist:
                return None
        return None


class AdDetailSerializer(serializers.ModelSerializer):
    """Serializer for ad detail page"""
    category = AdCategorySerializer(read_only=True)
    tags = AdTagSerializer(many=True, read_only=True)
    is_saved = serializers.SerializerMethodField()
    saved_id = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = Ad
        fields = [
            'id', 'title', 'description', 'prompt', 'video', 'thumbnail',
            'category', 'tags', 'copy_count', 'is_trending', 
            'is_saved', 'saved_id', 'created_at', 'updated_at'
        ]

    def get_video(self, obj):
        """Return full Cloudinary URL for video"""
        if obj.video:
            return obj.video.url
        return None

    def get_thumbnail(self, obj):
        """Return full Cloudinary URL for thumbnail"""
        if obj.thumbnail:
            return obj.thumbnail.url
        return None
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedAd.objects.filter(user=request.user, ad=obj).exists()
        return False
    
    def get_saved_id(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                saved = SavedAd.objects.get(user=request.user, ad=obj)
                return saved.id
            except SavedAd.DoesNotExist:
                return None
        return None