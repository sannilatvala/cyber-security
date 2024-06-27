from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile


def home_page_view(request):
    return render(request, 'index.html')

def logout_view(request):
    logout(request)
    return redirect('/')

# Flaw 1: Cryptographic failures (storing password in plain text)
# Flaw 4: Insecure Design (no form validation handling)
# Flaw 5: Injection (using vulnerable raw SQL query)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        # Flaw 1: Plain text password handling
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            error_message = "Passwords do not match"
            return render(request, 'register.html', {'error_message': error_message})
        if User.objects.filter(username=username).exists():
            error_message = "Username already exists"
            return render(request, 'register.html', {'error_message': error_message})
        # Flaw 1: Creating user manually and storing password in plain text
        user = User(username=username, password=password1)
        user.save()
        # Flaw 4: No form validation handling
        Profile.objects.create(user=user)
        return redirect('/login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            # Flaw 5: A malicious user can inject SQL to manipulate the query result
            user = User.objects.raw(f"SELECT * FROM auth_user WHERE username='{username}' AND password='{password}'")
            user = user[0] if user else None
        except User.DoesNotExist:
            user = None
        if user:
            login(request, user)
            return redirect('profile', user_id=user.id)
        else:
            error_message = 'Invalid username or password. Please try again.'
            form = AuthenticationForm()
            return render(request, 'login.html', {'form': form, 'error_message': error_message})
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Fix for Flaw 1: Storing password securely using Django's built-in UserCreationForm
# Fix for Flaw 4: Using Django's form validation
# Fix for Flaw 5: Using Django's ORM to avoid raw SQL injection

# Fix for flaw 1, 4 and 5:

# def register_view(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             Profile.objects.create(user=user)
#             return redirect('/login')
#     else:
#         form = UserCreationForm()
#     return render(request, 'register.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             print(user.password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('profile', user_id=user.id)
#     else:
#         form = AuthenticationForm()
#     return render(request, 'login.html', {'form': form})


# Flaw 2: Broken Access Control (No access control, anyone can view any user's profile)
# Flaw 3: Cross-Site Request Forgery (CSRF) protection missing

# Flaw 3: Missing CSRF protection
@csrf_exempt
def user_profile(request, user_id):
    # Flaw 2: No access control
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    if request.method == 'POST':
        profile.bio = request.POST.get('bio')
        profile.save()
    return render(request, 'profile.html', {'profile': profile})

# Fix for Flaw 2: Adding login required and access control
# Fix for Flaw 3: Adding CSRF protection

# Fix for flaw 2 and 3:

# @login_required
# def user_profile(request, user_id):
#     if request.user.id != user_id:
#         return redirect('/')
#     profile = get_object_or_404(Profile, user=request.user)
#     if request.method == 'POST':
#         profile.bio = request.POST.get('bio')
#         profile.save()
#     return render(request, 'profile.html', {'profile': profile})
