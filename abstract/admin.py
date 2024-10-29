from django.contrib import admin
from .models import *


admin.site.register(Track)
admin.site.register(PresentationType)


class AuthorInformationInline(admin.StackedInline):
    model = AuthorInformation
    extra = 1
    fields = ['author_name', 'email', 'affiliation']

class PresenterInformationInline(admin.StackedInline):
    model = PresenterInformation
    extra = 1
    fields = ['name', 'email']


# Abstract Admin
@admin.register(Abstract)
class AbstractAdmin(admin.ModelAdmin):
    list_display = ('abstract_title', 'submission_id', 'track', 'status', 'presentation_type')
    list_filter = ('status', 'track', 'presentation_type')
    search_fields = ('abstract_title', 'keywords', 'track__track_name')
    inlines = [AuthorInformationInline, PresenterInformationInline]
    ordering = ('-date_created',)


# Reviewer Admin with inline assignments
class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ('abstract', 'status', 'assigned_at')
    readonly_fields = ('assigned_at',)

@admin.register(Reviewer)
class ReviewerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'expertise_area')
    search_fields = ('full_name', 'email__email')
    list_filter = ('expertise_area',)
    inlines = [AssignmentInline]


# Assignment Admin
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('abstract', 'reviewer', 'status', 'assigned_at')
    list_filter = ('status', 'assigned_at')
    search_fields = ('abstract__abstract_title', 'reviewer__full_name')
    autocomplete_fields = ('abstract', 'reviewer')
    ordering = ('-assigned_at',)


# Reviews Admin
@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('abstract', 'user', 'reviewer','status', 'total', 'comment', 'attachment', 'presentation')
    list_filter = ('status', 'abstract', 'user')
    search_fields = ('abstract__abstract_title', 'user__username', 'comment')
    readonly_fields = ('total',)  # Make total read-only since it's auto-calculated

    fieldsets = (
        ('Review Details', {
            'fields': ('abstract', 'user', 'reviewer','status', 'comment', 'attachment', 'presentation')
        }),
        ('Scoring', {
            'fields': (
                'title', 'content', 'relevance', 'quality', 'clarity', 
                'methods', 'structure', 'data_collection', 'result', 
                'conclusion', 'total'
            )
        }),
    )