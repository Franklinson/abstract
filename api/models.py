from django.db import models
from accounts.models import Users
from registration.models import Register
from django.utils.timezone import now



class AppUser(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name="app_user")
    api_key = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.email



class ScanLog(models.Model):
    scanner = models.ForeignKey(Users, on_delete=models.CASCADE)
    registration = models.ForeignKey(Register, on_delete=models.CASCADE)
    scanned_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Scan by {self.scanner.email} on {self.scanned_at}"