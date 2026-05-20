from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class AdCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Ad Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AdTag(models.Model):
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


class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(help_text='Short description about the ad')
    prompt = models.TextField(help_text='Full prompt used to create this ad')
    video = models.FileField(upload_to='ads/videos/%Y/%m/', help_text='Upload ad video (MP4)')
    thumbnail = models.ImageField(upload_to='ads/thumbnails/%Y/%m/', blank=True, null=True)
    
    category = models.ForeignKey(
        AdCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='ads'
    )
    tags = models.ManyToManyField(AdTag, blank=True, related_name='ads')
    
    copy_count = models.IntegerField(default=0)
    is_trending = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_trending', '-created_at']
        indexes = [
            models.Index(fields=['-is_trending', '-created_at']),
        ]

    def __str__(self):
        return self.title


class SavedAd(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_ads')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ad')
        ordering = ['-saved_at']

    def __str__(self):
        return f'{self.user.username} saved {self.ad.title}'
