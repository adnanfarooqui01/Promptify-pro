# prompts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Auto-generate slug from name
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Prompt(models.Model):
    # Core fields
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="The actual AI prompt text")
    image = models.ImageField(
        upload_to='prompts/%Y/%m/',   # Organized by year/month
        blank=True,
        null=True
    )

    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prompts'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='prompts'
    )

    # Stats & Flags
    copy_count = models.PositiveIntegerField(default=0)
    is_trending = models.BooleanField(default=False)
    is_ai_generated = models.BooleanField(
        default=False,
        help_text="True if image was generated via AI API"
    )

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_trending', '-created_at']  # Trending first, then newest
        indexes = [
            models.Index(fields=['-is_trending', '-created_at']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title


class SavedPrompt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_prompts'
    )
    prompt = models.ForeignKey(
        Prompt,
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate saves — one user can save a prompt only once
        unique_together = ('user', 'prompt')
        ordering = ['-saved_at']

    def __str__(self):
        return f"{self.user.username} saved → {self.prompt.title}"
