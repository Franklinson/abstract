from django.db import models
from shortuuid.django_fields import ShortUUIDField

class Register(models.Model):
    
    Title = (
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr'),
        ('Prof', 'Prof'),
    )

    Category = (
        ('Student', 'Student'),
        ('GAND Member', 'GAND Member'),
        ('Non GAND Member', 'Non GAND Member'),
        ('International', 'International'),
    )

    Profession = (
        ('Dietitian', 'Dietitian'),
        ('Nutritionist', 'Nutritionist'),
        ('Technician', 'Technician'),
        ('Student', 'Student'),
        ('Health Educator', 'Health Educator'),
        ('Others', 'Others'),
    )

    About_us = (
        ('A Member', 'A Member'),
        ('Socials', 'Socials'),
        ('Email', 'Email'),
        ('Website', 'Website'),
        ('others', 'others'),
    )
    registration_number = ShortUUIDField(unique=True, length=6, max_length=30, prefix="COREG-", alphabet="1234567890")
    title = models.CharField(max_length=20, choices=Title)
    name = models.CharField(max_length=500)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female')))
    category = models.CharField(max_length=200, choices=Category)
    gand_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    prof_of_status = models.FileField(null=True, blank=True)
    profession = models.CharField(max_length=100, choices=Profession)
    organization = models.CharField(max_length=50)
    about_us = models.CharField(max_length=100, choices=About_us)
    complaince = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_ref = models.CharField(max_length=500, null=True)
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    


class EmailLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    plain_message = models.TextField()
    html_message = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email to {self.recipient} - {self.subject}"