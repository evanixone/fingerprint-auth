# urls.py

from django.urls import path
from .views import enroll, register, custom_login, home, enroll_template, custom_logout, delete_fingerprint
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('register/', register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('home/', home, name='home'),
    path('enroll/', enroll, name='enroll'),
    path('enroll-template/', enroll_template, name='enroll_template'),
    path('delete-fingerprint/', delete_fingerprint, name='delete_fingerprint'),
]
