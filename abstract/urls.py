from django.urls import path
from .views import *


# app_name = 'abstract'

urlpatterns = [
    path('add/', create_abstract, name='create_abstract'),
    path('edit/<int:id>/', edit_abstract, name='edit_abstract'),
    path('delete/<int:id>/', delete_abstract, name='delete_abstract'),
    path('<int:id>/', abstract_detail, name='abstract_detail'),
    path('reviewer/add/', create_reviewer, name='create_reviewer'),
    path('assignment/add/', create_assignment, name='create_assignment'),
    path('abstract/assign/<int:abstract_id>/', assign_reviewers, name='assign_reviewers'),
    path('abstract/add_review/<int:abstract_id>/', add_review, name='add_review'),
]