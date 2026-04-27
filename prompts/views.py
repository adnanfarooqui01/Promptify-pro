# prompts/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Prompt, Category, SavedPrompt

PROMPTS_PER_PAGE = 20

def home(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category', None)

    # Initial 20 prompts — server side rendered
    prompts_qs = Prompt.objects.select_related('category').prefetch_related('tags')

    if selected_category:
        prompts_qs = prompts_qs.filter(category__slug=selected_category)

    prompts_qs = prompts_qs.order_by('-is_trending', '-created_at')

    initial_prompts = prompts_qs[:PROMPTS_PER_PAGE]
    total_count     = prompts_qs.count()
    has_more        = total_count > PROMPTS_PER_PAGE

    context = {
        'prompts'          : initial_prompts,
        'categories'       : categories,
        'selected_category': selected_category,
        'has_more'         : has_more,
        'total_count'      : total_count,
    }
    return render(request, 'home.html', context)


def load_more_prompts(request):
    """
    API endpoint for infinite scroll.
    Returns JSON with next batch of prompts.
    GET /api/prompts/load-more/?offset=20&limit=20&category=slug
    """
    offset   = int(request.GET.get('offset', 0))
    limit    = int(request.GET.get('limit', PROMPTS_PER_PAGE))
    category = request.GET.get('category', None)

    prompts_qs = Prompt.objects.select_related('category').prefetch_related('tags')

    if category:
        prompts_qs = prompts_qs.filter(category__slug=category)

    prompts_qs  = prompts_qs.order_by('-is_trending', '-created_at')
    total_count = prompts_qs.count()
    prompts     = prompts_qs[offset: offset + limit]

    data = []
    for prompt in prompts:
        data.append({
            'id'          : prompt.pk,
            'title'       : prompt.title,
            'content'     : prompt.content[:80] + '...' if len(prompt.content) > 80 else prompt.content,
            'image'       : request.build_absolute_uri(prompt.image.url) if prompt.image else None,
            'category'    : prompt.category.name if prompt.category else None,
            'tags'        : [tag.name for tag in prompt.tags.all()[:3]],
            'copy_count'  : prompt.copy_count,
            'is_trending' : prompt.is_trending,
            'detail_url'  : f'/prompt/{prompt.pk}/',
        })

    return JsonResponse({
        'prompts'   : data,
        'has_more'  : (offset + limit) < total_count,
        'next_offset': offset + limit,
        'total'     : total_count,
    })


def prompt_detail(request, pk):
    prompt = get_object_or_404(
        Prompt.objects.select_related('category').prefetch_related('tags'),
        pk=pk
    )
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedPrompt.objects.filter(
            user=request.user, prompt=prompt
        ).exists()

    return render(request, 'prompts/detail.html', {
        'prompt' : prompt,
        'is_saved': is_saved,
    })


@login_required
def profile(request):
    saved_prompts = SavedPrompt.objects.filter(
        user=request.user
    ).select_related('prompt__category').order_by('-saved_at')

    return render(request, 'accounts/profile.html', {
        'saved_prompts': saved_prompts,
    })


@login_required
def generate(request):
    return render(request, 'prompts/generate.html')