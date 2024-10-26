from django.contrib import admin
from .models import (
    Track, AuthorInformation, PresenterInformation, 
    PresentationType, Abstract, Reviewer, Assignment
)


admin.site.register(Track)
admin.site.register(PresentationType)


class AuthorInformationInline(admin.StackedInline):
    model = AuthorInformation
    extra = 1 


class PresenterInformationInline(admin.StackedInline):
    model = PresenterInformation
    extra = 1  



@admin.register(Abstract)
class AbstractAdmin(admin.ModelAdmin):
    list_display = ('abstract_title', 'track', 'presentation_type', 'status')
    search_fields = ('abstract_title', 'keywords', 'track__track_name')
    list_filter = ('track', 'presentation_type', 'status')
    ordering = ('abstract_title',)
    inlines = [AuthorInformationInline, PresenterInformationInline] 



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



@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('abstract', 'reviewer', 'status', 'assigned_at')
    list_filter = ('status', 'assigned_at')
    search_fields = ('abstract__title', 'reviewer__full_name')
    autocomplete_fields = ('abstract', 'reviewer')  
    ordering = ('-assigned_at',)  
