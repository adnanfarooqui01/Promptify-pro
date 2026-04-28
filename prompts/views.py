# prompts/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Prompt, Category, SavedPrompt
from django.views.decorators.http import require_POST, require_http_methods
from django.db import models     
from django.db.models import F  
from django.db import transaction
import json

PROMPTS_PER_PAGE = 20

def home(request):
    categories         = Category.objects.all()
    selected_category  = request.GET.get('category', None)

    # Base queryset
    prompts_qs = Prompt.objects.select_related('category').prefetch_related('tags')

    # ✅ Apply category filter BEFORE slicing
    if selected_category:
        prompts_qs = prompts_qs.filter(category__slug=selected_category)

    prompts_qs = prompts_qs.order_by('-is_trending', '-created_at')

    # ✅ Count AFTER filter — so has_more is correct per category
    total_count = prompts_qs.count()

    # ✅ Only first 20 rendered server-side
    initial_prompts = prompts_qs[:PROMPTS_PER_PAGE]

    # ✅ has_more based on filtered count
    has_more = total_count > PROMPTS_PER_PAGE

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
    saved_id = None

    if request.user.is_authenticated:
        try:
            saved    = SavedPrompt.objects.get(user=request.user, prompt=prompt)
            is_saved = True
            saved_id = saved.id       # ← Pass saved_id to template
        except SavedPrompt.DoesNotExist:
            pass

    return render(request, 'prompts/detail.html', {
        'prompt'  : prompt,
        'is_saved': is_saved,
        'saved_id': saved_id,         # ← Pass to template
    })


SAVED_PER_PAGE = 20

@login_required
def profile(request):
    saved_qs = SavedPrompt.objects.filter(
        user=request.user
    ).select_related('prompt__category').order_by('-saved_at')

    total_count     = saved_qs.count()
    initial_saved   = saved_qs[:SAVED_PER_PAGE]
    has_more        = total_count > SAVED_PER_PAGE

    context = {
        'saved_prompts' : initial_saved,
        'has_more'      : has_more,
        'total_count'   : total_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def load_more_saved(request):
    """
    API for infinite scroll on profile/saved page.
    GET /api/saved/load-more/?offset=20&limit=20
    """
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
# ─── Copy Prompt ──────────────────────────────────────────────────────────────
@require_POST
def copy_prompt(request, pk):
    """
    Called when user clicks Copy button.
    Increments copy_count atomically.
    Login required — checked via JS redirect.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    prompt = get_object_or_404(Prompt, pk=pk)

    # Atomic update — prevents race condition if 2 users copy at same time
    with transaction.atomic():
        Prompt.objects.filter(pk=pk).update(
            copy_count=models.F('copy_count') + 1
        )
        prompt.refresh_from_db()

    return JsonResponse({
        'message'   : 'Copied!',
        'copy_count': prompt.copy_count,
    })


# ─── Save Prompt ──────────────────────────────────────────────────────────────
@require_POST
def save_prompt(request):
    """
    Saves a prompt for the logged in user.
    Prevents duplicate saves via unique_together constraint.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    try:
        data      = json.loads(request.body)
        prompt_id = data.get('prompt_id')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    if not prompt_id:
        return JsonResponse({'error': 'prompt_id is required'}, status=400)

    prompt = get_object_or_404(Prompt, pk=prompt_id)

    # get_or_create prevents duplicates
    saved, created = SavedPrompt.objects.get_or_create(
        user=request.user,
        prompt=prompt
    )

    if created:
        return JsonResponse({
            'message': 'Prompt saved!',
            'saved'  : True,
            'id'     : saved.id,
        }, status=201)
    else:
        return JsonResponse({
            'message': 'Already saved',
            'saved'  : True,
            'id'     : saved.id,
        }, status=200)


# ─── Unsave Prompt ────────────────────────────────────────────────────────────
@require_http_methods(['DELETE'])
def unsave_prompt(request, pk):
    """
    Removes a saved prompt.
    Deletes from SavedPrompt only — original Prompt stays safe.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)

    saved = get_object_or_404(
        SavedPrompt,
        pk=pk,
        user=request.user   # Extra security — only owner can unsave
    )
    saved.delete()

    return JsonResponse({
        'message': 'Removed from saved',
        'saved'  : False,
    })


# ─── Get Saved Status ─────────────────────────────────────────────────────────
def check_saved(request, pk):
    """
    Returns whether current user has saved a prompt.
    Used by JS to update button state.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'is_saved': False, 'saved_id': None})

    prompt = get_object_or_404(Prompt, pk=pk)

    try:
        saved = SavedPrompt.objects.get(user=request.user, prompt=prompt)
        return JsonResponse({'is_saved': True, 'saved_id': saved.id})
    except SavedPrompt.DoesNotExist:
        return JsonResponse({'is_saved': False, 'saved_id': None})

@login_required
def generate(request):
    return render(request, 'prompts/generate.html')