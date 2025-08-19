from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ("superadmin", "Super Admin"),
        ("admin", "Admin"),
        ("seller", "Seller"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="seller")

    def __str__(self):
        return f"{self.username} ({self.role})"
