# prompts/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
from .models import Prompt, Category, SavedPrompt
import json

PROMPTS_PER_PAGE = 20
SAVED_PER_PAGE   = 20


# ─── Home ─────────────────────────────────────────────────────────────────────
def home(request):
    categories        = Category.objects.all()
    selected_category = request.GET.get('category', None)

    prompts_qs = Prompt.objects.select_related(
        'category'
    ).prefetch_related('tags')

    if selected_category:
        prompts_qs = prompts_qs.filter(category__slug=selected_category)

    prompts_qs      = prompts_qs.order_by('-is_trending', '-created_at')
    total_count     = prompts_qs.count()
    initial_prompts = prompts_qs[:PROMPTS_PER_PAGE]
    has_more        = total_count > PROMPTS_PER_PAGE

    return render(request, 'home.html', {
        'prompts'          : initial_prompts,
        'categories'       : categories,
        'selected_category': selected_category,
        'has_more'         : has_more,
        'total_count'      : total_count,
    })


# ─── Load More Prompts (Infinite Scroll) ──────────────────────────────────────
def load_more_prompts(request):
    offset   = int(request.GET.get('offset', 0))
    limit    = int(request.GET.get('limit', PROMPTS_PER_PAGE))
    category = request.GET.get('category', None)

    prompts_qs = Prompt.objects.select_related(
        'category'
    ).prefetch_related('tags')

    if category:
        prompts_qs = prompts_qs.filter(category__slug=category)

    prompts_qs  = prompts_qs.order_by('-is_trending', '-created_at')
    total_count = prompts_qs.count()
    prompts     = prompts_qs[offset: offset + limit]

    data = []
    for prompt in prompts:
        data.append({
            'id'         : prompt.pk,
            'title'      : prompt.title,
            'content'    : prompt.content[:80] + '...' if len(prompt.content) > 80 else prompt.content,
            'image'      : request.build_absolute_uri(prompt.image.url) if prompt.image else None,
            'category'   : prompt.category.name if prompt.category else None,
            'tags'       : [tag.name for tag in prompt.tags.all()[:3]],
            'copy_count' : prompt.copy_count,
            'is_trending': prompt.is_trending,
            'detail_url' : f'/prompt/{prompt.pk}/',
        })

    return JsonResponse({
        'prompts'    : data,
        'has_more'   : (offset + limit) < total_count,
        'next_offset': offset + limit,
        'total'      : total_count,
    })


# ─── Prompt Detail ────────────────────────────────────────────────────────────
def prompt_detail(request, pk):
    return render(request, 'prompts/detail.html', {
        'prompt_id': pk
    })


# ─── Profile ──────────────────────────────────────────────────────────────────
@login_required
def profile(request):
    saved_qs    = SavedPrompt.objects.filter(
        user=request.user
    ).select_related('prompt__category').order_by('-saved_at')

    total_count   = saved_qs.count()
    initial_saved = saved_qs[:SAVED_PER_PAGE]
    has_more      = total_count > SAVED_PER_PAGE

    return render(request, 'accounts/profile.html', {
        'saved_prompts': initial_saved,
        'has_more'     : has_more,
        'total_count'  : total_count,
    })


# ─── Load More Saved (Infinite Scroll) ───────────────────────────────────────
@login_required
def load_more_saved(request):
    offset = int(request.GET.get('offset', 0))
    limit  = int(request.GET.get('limit', SAVED_PER_PAGE))

    saved_qs    = SavedPrompt.objects.filter(
        user=request.user
    ).select_related('prompt__category').order_by('-saved_at')

    total_count = saved_qs.count()
    saved_items = saved_qs[offset: offset + limit]

    data = []
    for item in saved_items:
        prompt = item.prompt
        data.append({
            'saved_id'  : item.id,
            'saved_at'  : item.saved_at.strftime('%b %d, %Y'),
            'id'        : prompt.pk,
            'title'     : prompt.title,
            'content'   : prompt.content[:80] + '...' if len(prompt.content) > 80 else prompt.content,
            'image'     : request.build_absolute_uri(prompt.image.url) if prompt.image else None,
            'category'  : prompt.category.name if prompt.category else None,
            'copy_count': prompt.copy_count,
            'detail_url': f'/prompt/{prompt.pk}/',
        })

    return JsonResponse({
        'saved'      : data,
        'has_more'   : (offset + limit) < total_count,
        'next_offset': offset + limit,
        'total'      : total_count,
    })


# ─── Generate ─────────────────────────────────────────────────────────────────
@login_required
def generate(request):
    categories = Category.objects.all()
    return render(request, 'prompts/generate.html', {
        'categories': categories
    })