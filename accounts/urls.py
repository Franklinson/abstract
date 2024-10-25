from django.urls import path
from .views import *

urlpatterns = [
    path('home/', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', author_dashboard, name='author_dashboard'),

]