# prompts/serializers.py

from rest_framework import serializers
from .models import Prompt, Category, Tag, SavedPrompt


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ['id', 'name', 'slug']


class PromptDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags     = TagSerializer(many=True, read_only=True)
    is_saved = serializers.SerializerMethodField()
    saved_id = serializers.SerializerMethodField()

    class Meta:
        model  = Prompt
        fields = [
            'id',
            'title',
            'content',
            'image',
            'category',
            'tags',
            'copy_count',
            'is_trending',
            'is_ai_generated',
            'is_saved',
            'saved_id',
            'created_at',
            'updated_at',
        ]

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedPrompt.objects.filter(
                user=request.user,
                prompt=obj
            ).exists()
        return False

    def get_saved_id(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                saved = SavedPrompt.objects.get(
                    user=request.user,
                    prompt=obj
                )
                return saved.id
            except SavedPrompt.DoesNotExist:
                return None
        return None