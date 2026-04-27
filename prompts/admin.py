# prompts/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tag, Prompt, SavedPrompt


# ─── Category Admin ───────────────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'prompt_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}  # Auto-fills slug from name

    def prompt_count(self, obj):
        return obj.prompts.count()
    prompt_count.short_description = 'Total Prompts'


# ─── Tag Admin ────────────────────────────────────────────────────────────────
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


# ─── Prompt Admin ─────────────────────────────────────────────────────────────
class SavedPromptInline(admin.TabularInline):
    model = SavedPrompt
    extra = 0
    readonly_fields = ['user', 'saved_at']
    can_delete = False


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'copy_count',
        'is_trending',
        'is_ai_generated',
        'image_preview',
        'created_at'
    ]
    list_filter = ['is_trending', 'is_ai_generated', 'category', 'created_at']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']   # Nice UI for ManyToMany tags
    readonly_fields = ['copy_count', 'created_at', 'updated_at', 'image_preview']
    list_editable = ['is_trending']  # Edit trending directly from list view
    ordering = ['-is_trending', '-created_at']

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'content', 'category', 'tags')
        }),
        ('Image', {
            'fields': ('image', 'image_preview', 'is_ai_generated')
        }),
        ('Settings', {
            'fields': ('is_trending', 'copy_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)   # Collapsed by default
        }),
    )

    inlines = [SavedPromptInline]  # Show who saved this prompt

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px; height:80px; '
                'object-fit:cover; border-radius:6px;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'


# ─── SavedPrompt Admin ────────────────────────────────────────────────────────
@admin.register(SavedPrompt)
class SavedPromptAdmin(admin.ModelAdmin):
    list_display = ['user', 'prompt', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'prompt__title']
    readonly_fields = ['user', 'prompt', 'saved_at']
