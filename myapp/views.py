from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.decorators import login_required
import random
from django.views.decorators.cache import never_cache
from .models import mapped
from .tasks import send_otp_email
User = get_user_model()
import string
BASE62 = string.digits + string.ascii_lowercase + string.ascii_uppercase

def encode_base62(num: int) -> str:
    """Convert an integer to a base62 string."""
    if num == 0:
        return BASE62[0]
    
    base62_str = []
    while num > 0:
        num, rem = divmod(num, 62)
        base62_str.append(BASE62[rem])
    return ''.join(reversed(base62_str))

def decode_base62(base62_str: str) -> int:
    """Convert a base62 string back to an integer."""
    num = 0
    for char in base62_str:
        num = num * 62 + BASE62.index(char)
    return num
# ------------------ SIGNUP ------------------
def signup(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        password2 = request.POST.get('password2')
        terms = request.POST.get('terms')  # Checkbox

        if not terms:
            messages.error(request, "You must agree to the Terms & Conditions.")
            return redirect('/signup')

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect('/signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            return redirect('/signup')

        otp = str(random.randint(100000, 999999))
        cache.set(f'otp_{email}', otp, timeout=300)

        request.session['email'] = email
        request.session['password'] = password
        request.session['name'] = name
        send_otp_email.delay(name,email,otp)
        '''messages.success(request, "Please verify your OTP. Check your email!")'''
        return redirect('/verify_otp')

    return render(request, 'signup.html')


# ------------------ VERIFY OTP ------------------
def verify_otp(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        email = request.session.get('email')
        password = request.session.get('password')
        name = request.session.get('name')

        otp_stored = cache.get(f'otp_{email}')

        if otp_stored and otp_input == otp_stored:
            cache.delete(f'otp_{email}')

            # Create or get existing user
            user = User.objects.create_user(
                email=email,
                username=name,
                password=password
            )
            user.is_active = True
            # Mark as verified
            user.is_verified = True
            user.save()
            # Authenticate and login
            auth_user = authenticate(request,username=email, password=password,backend='django.contrib.auth.backends.ModelBackend')
            login(request, auth_user)
            '''messages.success(request, "OTP verified successfully. You are now logged in.")'''
            return redirect('/')
        else:
            messages.error(request, "Invalid or expired OTP")
            return redirect('/verify_otp')

    return render(request, 'verify_otp.html')


# ------------------ RESEND OTP ------------------
def resend_otp(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect('/signup')

    otp = str(random.randint(100000, 999999))
    cache.set(f'otp_{email}', otp, timeout=300)
    send_otp_email.delay("user",email,otp)
    '''messages.success(request, "A new OTP has been sent to your email.")'''
    return redirect('/verify_otp')

@never_cache
def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            '''messages.success(request, "You are now logged in.")'''
            return redirect('/')
        else:
            messages.error(request, "Invalid email or password")
            return redirect('/signin')

    return render(request, 'signin.html')


# ------------------ LOGOUT ------------------
@login_required(login_url='/signin')
def logout_view(request):
    logout(request)
    return redirect('/signin')
# ------------------ HOME ------------------
BASE_URL = getattr(settings, "BASE_URL", "http://127.0.0.1:8000/api/")


import hashlib
from urllib.parse import urlparse

def normalize_url(url):
    parsed = urlparse(url.strip())
    return parsed.geturl().lower()
@login_required(login_url='/signin')
@never_cache
def home(request):
    if request.method == 'POST':
        name = request.user.username
        link = normalize_url(request.POST.get('link'))
        cache_key = f"urlmap_{name}_{hashlib.md5(link.encode()).hexdigest()}"

        shorter_url = cache.get(cache_key)
        if shorter_url:
            return render(request, 'home.html', {"shorter_url": shorter_url})

        man = mapped.objects.filter(url=link).first()
        if not man:
            pl = mapped.objects.create(url=link, shorter_url="")
            shorter_code = encode_base62(pl.id)
            pl.shorter_url = shorter_code
            pl.save()
            shorter_url = BASE_URL + shorter_code
        else:
            shorter_url = BASE_URL + man.shorter_url

        cache.set(cache_key, shorter_url, timeout=86400 * 7)
        return render(request, 'home.html', {"shorter_url": shorter_url})

    return render(request, 'home.html')



def transfer(request, code):
    """Redirect from short link to original URL."""
    try:
        obj_id = decode_base62(code)
        po = get_object_or_404(mapped, id=obj_id)
        return redirect(po.url)
    except Exception:
        messages.error(request, "Invalid short URL")
        return redirect('/')







