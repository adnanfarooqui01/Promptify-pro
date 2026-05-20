from django.contrib import admin
from django.utils.html import format_html
from .models import AdCategory, AdTag, Ad, SavedAd


@admin.register(AdCategory)
class AdCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'ad_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def ad_count(self, obj):
        return obj.ads.count()
    ad_count.short_description = 'Total Ads'


@admin.register(AdTag)
class AdTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'category', 
        'copy_count', 
        'is_trending', 
        'thumbnail_preview',
        'created_at'
    ]
    list_filter = ['is_trending', 'category', 'created_at']
    search_fields = ['title', 'description', 'prompt']
    filter_horizontal = ['tags']
    list_editable = ['is_trending']
    readonly_fields = ['copy_count', 'created_at', 'updated_at', 'video_preview', 'thumbnail_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'tags')
        }),
        ('Ad Content', {
            'fields': ('video', 'video_preview', 'thumbnail', 'thumbnail_preview')
        }),
        ('Prompt Details', {
            'fields': ('prompt',)
        }),
        ('Statistics', {
            'fields': ('copy_count', 'is_trending', 'created_at', 'updated_at')
        }),
    )
    
    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="300" controls><source src="{}" type="video/mp4"></video>',
                obj.video.url
            )
        return '—'
    video_preview.short_description = 'Video Preview'
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width:100px; height:auto; border-radius:6px;" />',
                obj.thumbnail.url
            )
        return '—'
    thumbnail_preview.short_description = 'Thumbnail'


@admin.register(SavedAd)
class SavedAdAdmin(admin.ModelAdmin):
    list_display = ['user', 'ad', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'ad__title']