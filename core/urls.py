from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('abstract/', include('abstract.urls')),
    path('', include('accounts.urls')),
]
