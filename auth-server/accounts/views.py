import json
from django.shortcuts import render, redirect
from django.http import HttpRequest, Http404, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .generate.match.match import match_sets
from .generate.hide_data.hide_data import hide_data, extract_message
from .generate.encrypt.encrypt import encrypt, decrypt
from .models import User, Fingerprint
from .forms import RegisterForm

# accounts/views.py

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        descriptors_json = request.POST.get('descriptors')

        if password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        elif descriptors_json:
            try:
                descriptors = json.loads(descriptors_json)
            except json.JSONDecodeError:
                return HttpResponseBadRequest('Invalid JSON format for descriptors')
            
            username = extract_message(descriptors)
            if not username:
                return HttpResponseBadRequest('Username is missing')

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return HttpResponseBadRequest('User with the provided username does not exist')

            fingerprints = Fingerprint.objects.filter(user=user)
            for fingerprint in fingerprints:
                encrypted_descriptors = fingerprint.descriptors
                decrypted_descriptors = decrypt(encrypted_descriptors, user.password)

                if match_sets(decrypted_descriptors, descriptors):
                    login(request, user)
                    return JsonResponse({'message': f'Fingerprint matched with user {user.username}.'})

            return JsonResponse({'message': 'No matching fingerprint found.'})
        else:
            messages.error(request, 'Invalid login details.')

    return render(request, 'login.html')

def custom_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')  # Redirect to the login page after logging out


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully.')
            login(request, user)  # Log the user in after registration
            return redirect('enroll_template')  # Redirect to the enrollment page
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')

@csrf_exempt
@login_required
def enroll(request):
    if request.method == 'POST':
        descriptors_json = request.POST.get('descriptors')
        if not descriptors_json:
            return HttpResponseBadRequest('Descriptors data is missing')

        try:
            descriptors = json.loads(descriptors_json)
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON format for descriptors')
        
        username = extract_message(descriptors)
        if not username:
            return HttpResponseBadRequest('Username is missing')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseBadRequest('User with the provided username does not exist')
        
        encrypted_descriptors = encrypt(descriptors, user.password)

        fingerprint = Fingerprint(user=user, descriptors=encrypted_descriptors)
        fingerprint.save()

        return JsonResponse({'message': 'Descriptors received successfully.'})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

@login_required
def enroll_template(request):
    return render(request, 'enroll.html')

@login_required
def delete_fingerprint(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if not username:
            return HttpResponseBadRequest('Username is missing')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseBadRequest('User with the provided username does not exist')
        
        fingerprints = Fingerprint.objects.filter(user=user)
        fingerprints.delete()

        # Redirect back to the home page
        return redirect('home')
    else:
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
