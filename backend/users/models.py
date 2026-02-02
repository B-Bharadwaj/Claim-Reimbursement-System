from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('EMPLOYEE', 'Employee'),
        ('MANAGER', 'Manager'),
        ('FINANCE', 'Finance Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')

    reports_to = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="direct_reports",
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
