from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from shortuuid.django_fields import ShortUUIDField

# event information for which the abstract will be submitted to
# class Event(models.Model):
#     event_name = models.CharField(max_length=100)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     event_location = models.CharField(max_length=200)
#     event_description = models.TextField()
#     event_image = models.ImageField(upload_to='event_images')

#     def __str__(self):
#         return f'{self.event_name}'
    
#     verbose_name = "Events"


# abstract tracks for the event
class Track(models.Model):
    track_name = models.CharField(max_length=100)
    track_description = models.TextField()

    def __str__(self):
        return self.track_name

    
    
# authors who are part of the abstract 
class AuthorInformation(models.Model):
    author_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=254, null=True)
    affiliation = models.CharField(max_length=200, null=True)
    abstract = models.ForeignKey('Abstract', on_delete=models.CASCADE, related_name='authors')

    def __str__(self):
        return f'{self.author_name}'
    

# the presenter information 
class PresenterInformation(models.Model):
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=254, null=True)
    abstract = models.ForeignKey('Abstract', on_delete=models.CASCADE, related_name='presentor')

    def __str__(self):
        return f'{self.name} {self.email}'
    

# types of abstract presentation    
class PresentationType(models.Model):
    type_name = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.type_name

 
Choices = (
    ('Pending', 'Pending'),
    ('Submitted', 'Submitted'),
    ('Accepted', 'Accepted'),
    ('Reviewed', 'Reviewed'),
    ('Rejected', 'Rejected'),
)

# abstract information 
class Abstract(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    abstract_title = models.CharField(max_length=200)
    abstract = models.TextField(max_length=306)
    keywords = models.CharField(max_length=100)
    attachment = models.FileField(upload_to='abstract_files')
    # event = models.ForeignKey(Event, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    submission_id = ShortUUIDField(unique=True, length=6, max_length=30, prefix="COND-", alphabet="1234567890", editable=False)
    presentation_type = models.ForeignKey(PresentationType, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10, choices=Choices, default='Pending')
    reviewers = models.ManyToManyField('Reviewer', related_name='assigned_abstracts', through='Assignment', blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.abstract_title}  {self.track} {self.date_created}'
    
    

class Reviewer(models.Model):
    email = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=300, null=False, blank=False)
    expertise_area = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='reviewers')

    def __str__(self):
        return self.full_name


class Assignment(models.Model):
    abstract = models.ForeignKey(Abstract, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('assigned', 'Assigned'), ('reviewed', 'Reviewed')], default='assigned')

    class Meta:
        unique_together = ('abstract', 'reviewer')

    def __str__(self):
        return f"{self.abstract.abstract_title} -> {self.reviewer.email}"




STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Accept Pending Review', 'Accept Pending Review'),
    ('Rejected', 'Rejected'),
)

class Reviews(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    abstract = models.ForeignKey(Abstract, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    comment = models.TextField()
    attachment = models.FileField(upload_to='review_attachment', blank=True, null=True)  # Make attachment optional
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    presentation = models.ForeignKey(PresentationType, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Scoring fields, with range constraints for consistency
    title = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)]) 
    content = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    relevance = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    clarity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    methods = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])  
    structure = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    data_collection = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    result = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    conclusion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    total = models.IntegerField(editable=False) 

    class Meta:
        verbose_name_plural = "Review Scorings"

    def save(self, *args, **kwargs):
        # Automatically calculate the total score based on all scoring fields
        self.total = (
            self.title + self.content + self.relevance + self.quality +
            self.clarity + self.methods + self.structure +
            self.data_collection + self.result + self.conclusion
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Review for {self.abstract.abstract_title} by {self.reviewer.full_name}'