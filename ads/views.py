from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def ads_home(request):
    """Empty page - all data loaded via API"""
    return render(request, 'ads/home.html')


def ad_detail(request, pk):
    """Empty page - data loaded via API"""
    return render(request, 'ads/detail.html', {'ad_id': pk})


@login_required
def my_saved_ads(request):
    """Empty page - data loaded via API"""
    return render(request, 'ads/saved.html')