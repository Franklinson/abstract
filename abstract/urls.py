from django.urls import path
from .views import *


urlpatterns = [
    path('create/', create_abstract, name='create_abstract'),
    path('<int:id>/edit/', edit_abstract, name='edit_abstract'),
    path('<int:id>/delete/', delete_abstract, name='delete_abstract'),
    path('<int:id>/', abstract_detail, name='abstract_detail'),
]