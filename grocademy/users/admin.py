from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.
class CustomUserAdmin(UserAdmin):
    # Baris-baris ini menambahkan field 'balance' ke halaman detail pengguna di admin
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('balance',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('balance',)}),
    )

# Mendaftarkan CustomUser dengan konfigurasi tampilan CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)