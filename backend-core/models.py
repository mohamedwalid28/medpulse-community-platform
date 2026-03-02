from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Oncologist'
        MODERATOR = 'MODERATOR', 'Staff'
        MEMBER = 'MEMBER', 'Patient'
    
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    stripe_id = models.CharField(max_length=255, blank=True)
    subscription_active = models.BooleanField(default=False)

class VideoContent(models.Model):
    title = models.CharField(max_length=250)
    video_url = models.URLField()
    transcript_text = models.TextField(blank=True)
    category = models.CharField(max_length=100) # e.g., 'Integrated Medicine'