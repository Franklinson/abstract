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
    path('assign/<int:abstract_id>/', assign_reviewers, name='assign_reviewers'),
    path('add_review/<int:abstract_id>/', add_review, name='add_review'),
    path('review/edit/<int:review_id>/', edit_review, name='edit_review'),
    path('manager_create/', manager_create_abstract, name='manager_create'),
    path('manager_edit/<int:id>/', manager_edit_abstract, name='manager_edit'),
    path('manager_review/<int:abstract_id>/', manager_add_review, name='manager_review'),
    path('manager_edit_review/<int:review_id>/', manager_edit_review, name='manager_edit_review'),
]

manager_edit_abstract