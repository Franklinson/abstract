from django.contrib import admin
from .models import *


admin.site.register(Track)
admin.site.register(AuthorInformation)
admin.site.register(PresenterInformation)
admin.site.register(PresentationType)
# admin.site.register(AbstractAuthor)
# admin.site.register(AbstractPresenter)

class AuthorInformationInline(admin.StackedInline):
    model = AuthorInformation
    extra = 1
    
class PresenterInformationInline(admin.StackedInline):
    model = PresenterInformation
    extra = 1
    

# class PresentationTypeInline(admin.StackedInline):
#     model = PresentationType
#     extra = 1


class AbstractAdmin(admin.ModelAdmin):
    ordering = ['abstract_title', 'abstract','keywords', 'attachment', 'presentation_type','track',
                'status']
    inlines = [AuthorInformationInline, PresenterInformationInline ]
    
admin.site.register(Abstract, AbstractAdmin)