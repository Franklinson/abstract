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
        ('GAND Student', 'GAND Student'),
        ('GAND Full Member', 'GAND Full Member'),
        ('Non GAND Member', 'Non GAND Member'),
        ('Non GAND Student', 'Non GAND Student'),
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
    validated = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.CharField(max_length=50, null=True, blank=True)
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
    



class Coupon(models.Model):
    COUPON_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=COUPON_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateField(null=True, blank=True)

    def is_valid(self):
        from datetime import date
        if not self.is_active:
            return False
        if self.expiry_date and self.expiry_date < date.today():
            return False
        return True

    def __str__(self):
        return self.code