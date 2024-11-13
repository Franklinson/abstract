from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path(
    "admin/password_reset/",
    auth_views.PasswordResetView.as_view(
        extra_context={"site_header": admin.site.site_header}
    ),
    name="admin_password_reset",
),
path(
    "admin/password_reset/done/",
    auth_views.PasswordResetDoneView.as_view(
        extra_context={"site_header": admin.site.site_header}
    ),
    name="admin_password_reset_done",
),
path(
    "admin/reset/<uidb64>/<token>/",
    auth_views.PasswordResetConfirmView.as_view(
        extra_context={"site_header": admin.site.site_header}
    ),
    name="admin_password_reset_confirm",
),
path(
    "admin_reset/done/",
    auth_views.PasswordResetCompleteView.as_view(
        extra_context={"site_header": admin.site.site_header}
    ),
    name="admin_password_reset_complete",
),
    path('admin/', admin.site.urls),
    path('abstract/', include('abstract.urls')),
    path('', include('accounts.urls')),
    path('registration/', include('registration.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Conference of Nutrition and Dietetics, COND"
admin.site.site_title = "Conference of Nutrition and Dietetics"
admin.site.index = "Welcome to Admin Dashboard"
# admin.site.index_title = "COND"