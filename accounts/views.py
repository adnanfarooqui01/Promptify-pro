# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignupForm, LoginForm


def signup_view(request):
    # If already logged in → go home
    if request.user.is_authenticated:
        return redirect('prompts:home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto login after signup
            login(request, user)
            messages.success(request, f'Welcome to Promptify, {user.username}! 🎉')
            return redirect('prompts:home')
        else:
            # Show first error
            for field, errors in form.errors.items():
                messages.error(request, errors[0])
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    # If already logged in → go home
    if request.user.is_authenticated:
        return redirect('prompts:home')

    # 'next' param — redirect back after login
    next_url = request.GET.get('next', '/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user     = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}! 👋')
                # Redirect to next_url or home
                next_url = request.POST.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form'    : form,
        'next_url': next_url,
    })


@login_required
def logout_view(request):
    username = request.user.username
    logout(request)
    messages.success(request, f'Goodbye, {username}! See you soon. 👋')
    return redirect('prompts:home')