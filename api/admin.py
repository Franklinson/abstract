from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import AppUser, ScanLog

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'api_key', 'is_active')
    readonly_fields = ('api_key',)
    search_fields = ('user__email',)
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        if not obj.user.email or not obj.user.has_usable_password():
            raise ValidationError("The associated user must have a valid email and password.")
        super().save_model(request, obj, form, change)



@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('scanner', 'registration', 'scanned_at')
    list_filter = ('scanned_at', 'scanner')
    search_fields = ('scanner__email', 'registration__name', 'registration__registration_number')
    ordering = ('-scanned_at',)
    date_hierarchy = 'scanned_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('scanner', 'registration')
