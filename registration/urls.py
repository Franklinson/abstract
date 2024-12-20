from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('paystack/callback/', views.paystack_callback, name='paystack_callback'),
    path('fetch-member-info/', views.fetch_member_info, name='fetch_member_info'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
]