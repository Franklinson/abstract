from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

# app_name = 'account'

urlpatterns = [
    path('', login, name='login'),
    path('signup/', register, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', author_dashboard, name='author_dashboard'),
    path('manager/', manager, name='manager'),
    path('profile/update/', update_profile, name='profile_update'),


     path('reset_password/',
     auth_views.PasswordResetView.as_view(template_name="account/password_reset.html"),
     name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="account/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name="account/password_reset_form.html"), 
     name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="account/password_reset_done.html"), 
        name="password_reset_complete"),

]