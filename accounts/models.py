

# Create your models here.



from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('owner', 'Owner'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    email = models.EmailField(unique=True)

    # cart = models.ForeignKey("shop.Cart", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} "

    @property
    def is_owner(self):
        return self.role == 'owner'

    @property
    def is_admin(self):
        return self.role == 'admin'





