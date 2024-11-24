from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AppUser
import secrets

@receiver(post_save, sender=AppUser)
def generate_api_key(sender, instance, created, **kwargs):
    if created and not instance.api_key:
        instance.api_key = secrets.token_hex(16)
        instance.save()
