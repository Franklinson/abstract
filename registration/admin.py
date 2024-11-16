from django.contrib import admin
from.models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields

admin.site.register(Register)

# class EmailLogResource(resources.ModelResource):
#     abstract = fields.Field(
#         column_name='abstract',
#         attribute='abstract',
#         widget=ForeignKeyWidget(Abstract, 'abstract_title')
#     )

#     class Meta:
#         model = EmailLog
#         fields = ('recipient', 'abstract','subject', 'plain_message', 'sent_at')

@admin.register(EmailLog)
class EmailLogtAdmin(ImportExportModelAdmin):
    # resource_class = EmailLogResource
    list_display = ('recipient','subject', 'plain_message', 'sent_at')
    list_filter = ('subject', 'sent_at')
    search_fields = ('subject', 'recipient')
    # autocomplete_fields = ('abstract', )
    ordering = ('-sent_at',)