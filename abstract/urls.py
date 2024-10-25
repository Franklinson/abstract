from django.urls import path
from .views import *


urlpatterns = [
    path('add/', create_abstract, name='create_abstract'),
    path('edit/<int:id>/', edit_abstract, name='edit_abstract'),
    path('delete/<int:id>/', delete_abstract, name='delete_abstract'),
    path('<int:id>/', abstract_detail, name='abstract_detail'),
]