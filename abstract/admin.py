from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import *
from accounts.models import Users
from django.http import HttpResponse
from docx import Document


@admin.action(description="Export selected abstracts to DOCX")
def export_abstracts_to_docx(modeladmin, request, queryset):
    # Create a new Document
    doc = Document()
    doc.add_heading('Abstracts Export', level=1)

    for abstract in queryset:
        # Add the abstract title
        doc.add_heading(abstract.abstract_title, level=2)

        # Add submission ID and track
        doc.add_paragraph(f"Submission ID: {abstract.submission_id}")
        doc.add_paragraph(f"Track: {abstract.track.track_name}")

        # Add authors
        authors = abstract.authors.all()
        if authors:
            doc.add_paragraph("Authors:")
            for author in authors:
                doc.add_paragraph(
                    f"{author.author_name} ({author.affiliation}, {author.email})", style='List Bullet'
                )

        # Add presenters
        presenters = abstract.presentor.all()
        if presenters:
            doc.add_paragraph("Presenters:")
            for presenter in presenters:
                doc.add_paragraph(
                    f"{presenter.name} ({presenter.email})", style='List Bullet'
                )

        # Add other details
        doc.add_paragraph(f"Keywords: {abstract.keywords}")
        doc.add_paragraph(f"Status: {abstract.status}")
        
        # Add the abstract text itself
        doc.add_paragraph("Abstract:", style='Heading 3')
        doc.add_paragraph(abstract.abstract)

        # Divider between abstracts
        doc.add_paragraph("\n" + "-" * 40 + "\n")

    # Save the document to a response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=abstracts_export.docx'
    doc.save(response)

    return response



# Abstract Model Resource Class
class AbstractResource(resources.ModelResource):
    track = fields.Field(
        column_name='track',
        attribute='track',
        widget=ForeignKeyWidget(Track, 'track_name')
    )
    presentation_type = fields.Field(
        column_name='presentation_type',
        attribute='presentation_type',
        widget=ForeignKeyWidget(PresentationType, 'type_name')
    )
    user = fields.Field(
        column_name='Submitter',
        attribute='user',
        widget=ForeignKeyWidget(Users, 'email')
    )
    reviewers = fields.Field(
        column_name='reviewers',
        attribute='reviewers',
        widget=ManyToManyWidget(Reviewer, field='full_name')
    )

    # Include inlined fields for AuthorInformation and PresenterInformation
    author_names = fields.Field(column_name='author_names')
    author_emails = fields.Field(column_name='author_emails')
    author_affiliations = fields.Field(column_name='author_affiliations')
    presenter_names = fields.Field(column_name='presenter_names')
    presenter_emails = fields.Field(column_name='presenter_emails')

    def dehydrate_author_names(self, abstract):
        return "; ".join([author.author_name for author in abstract.authors.all()])

    def dehydrate_author_emails(self, abstract):
        return "; ".join([author.email for author in abstract.authors.all()])

    def dehydrate_author_affiliations(self, abstract):
        return "; ".join([author.affiliation for author in abstract.authors.all()])

    def dehydrate_presenter_names(self, abstract):
        return "; ".join([presenter.name for presenter in abstract.presentor.all()])

    def dehydrate_presenter_emails(self, abstract):
        return "; ".join([presenter.email for presenter in abstract.presentor.all()])

    class Meta:
        model = Abstract
        fields = (
            'id', 'abstract_title', 'abstract', 'submission_id', 'track', 'status',
            'presentation_type', 'user', 'keywords', 'attachment', 'date_created',
            'reviewers', 'author_names', 'author_emails', 'author_affiliations',
            'presenter_names', 'presenter_emails'
        )
        export_order = fields


# Reviewer Model Resource Class
class ReviewerResource(resources.ModelResource):
    email = fields.Field(
        column_name='email',
        attribute='email',
        widget=ForeignKeyWidget(Users, 'email')
    )
    expertise_area = fields.Field(
        column_name='expertise_area',
        attribute='expertise_area',
        widget=ForeignKeyWidget(Track, 'track_name')
    )

    class Meta:
        model = Reviewer
        fields = ('id', 'full_name', 'email', 'expertise_area')
        export_order = fields


# Assignment Model Resource Class
class AssignmentResource(resources.ModelResource):
    abstract = fields.Field(
        column_name='abstract',
        attribute='abstract',
        widget=ForeignKeyWidget(Abstract, 'abstract_title')
    )
    reviewer = fields.Field(
        column_name='reviewer',
        attribute='reviewer',
        widget=ForeignKeyWidget(Reviewer, 'full_name')
    )

    class Meta:
        model = Assignment
        fields = ('id', 'abstract', 'reviewer', 'status', 'assigned_at')
        export_order = fields


# Reviews Model Resource Class
class ReviewsResource(resources.ModelResource):
    abstract = fields.Field(
        column_name='abstract',
        attribute='abstract',
        widget=ForeignKeyWidget(Abstract, 'abstract_title')
    )
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(Users, 'email')
    )
    reviewer = fields.Field(
        column_name='reviewer',
        attribute='reviewer',
        widget=ForeignKeyWidget(Reviewer, 'full_name')
    )
    presentation = fields.Field(
        column_name='presentation',
        attribute='presentation',
        widget=ForeignKeyWidget(PresentationType, 'type_name')
    )

    class Meta:
        model = Reviews
        fields = (
            'id', 'abstract', 'user', 'reviewer', 'comment', 'attachment', 'status',
            'presentation', 'date_created', 'title', 'content', 'relevance', 'quality', 
            'clarity', 'methods', 'structure', 'data_collection', 'result', 'conclusion', 'total'
        )
        export_order = fields


class EmailLogResource(resources.ModelResource):
    abstract = fields.Field(
        column_name='abstract',
        attribute='abstract',
        widget=ForeignKeyWidget(Abstract, 'abstract_title')
    )

    class Meta:
        model = EmailLog
        fields = ('recipient', 'abstract','subject', 'plain_message', 'sent_at')

# Admin Classes for Exporting

class AuthorInformationInline(admin.StackedInline):
    model = AuthorInformation
    extra = 1
    fields = ['author_name', 'email', 'affiliation']

class PresenterInformationInline(admin.StackedInline):
    model = PresenterInformation
    extra = 1
    fields = ['name', 'email']


@admin.register(Abstract)
class AbstractAdmin(ImportExportModelAdmin):
    resource_class = AbstractResource
    list_display = ('abstract_title', 'submission_id', 'track', 'status', 'presentation_type')
    list_filter = ('status', 'track', 'presentation_type')
    search_fields = ('abstract_title', 'keywords', 'track__track_name')
    inlines = [AuthorInformationInline, PresenterInformationInline]
    ordering = ('-date_created',)
    actions = [export_abstracts_to_docx]


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ('abstract', 'status', 'assigned_at')
    readonly_fields = ('assigned_at',)


@admin.register(Reviewer)
class ReviewerAdmin(ImportExportModelAdmin):
    resource_class = ReviewerResource
    list_display = ('full_name', 'email', 'expertise_area')
    search_fields = ('full_name', 'email__email')
    list_filter = ('expertise_area',)
    inlines = [AssignmentInline]


@admin.register(Assignment)
class AssignmentAdmin(ImportExportModelAdmin):
    resource_class = AssignmentResource
    list_display = ('abstract', 'reviewer', 'status', 'assigned_at')
    list_filter = ('status', 'assigned_at')
    search_fields = ('abstract__abstract_title', 'reviewer__full_name')
    autocomplete_fields = ('abstract', 'reviewer')
    ordering = ('-assigned_at',)


@admin.register(EmailLog)
class EmailLogtAdmin(ImportExportModelAdmin):
    resource_class = EmailLogResource
    list_display = ('recipient', 'abstract','subject', 'plain_message', 'sent_at')
    list_filter = ('subject', 'sent_at')
    search_fields = ('abstract__abstract_title', 'recipient')
    autocomplete_fields = ('abstract', )
    ordering = ('-sent_at',)




@admin.register(Reviews)
class ReviewsAdmin(ImportExportModelAdmin):
    resource_class = ReviewsResource
    list_display = ('abstract', 'user', 'reviewer', 'status', 'total', 'comment', 'attachment', 'presentation')
    list_filter = ('status', 'abstract', 'user')
    search_fields = ('abstract__abstract_title', 'user__username', 'comment')
    readonly_fields = ('total',)
    fieldsets = (
        ('Review Details', {
            'fields': ('abstract', 'user', 'reviewer', 'status', 'comment', 'attachment', 'presentation')
        }),
        ('Scoring', {
            'fields': (
                'title', 'content', 'relevance', 'quality', 'clarity', 
                'methods', 'structure', 'data_collection', 'result', 
                'conclusion', 'total'
            )
        }),
    )

admin.site.register(Track)
admin.site.register(PresentationType)