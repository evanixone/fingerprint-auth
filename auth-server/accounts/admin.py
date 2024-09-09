from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Fingerprint

class FingerprintAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

admin.site.register(User, UserAdmin)
admin.site.register(Fingerprint, FingerprintAdmin)