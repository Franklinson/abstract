from django.db import models
from django.conf import settings

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
