from django.db import models

# Create your models here.


class Blog(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="blogs/", blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)   # auto set on create
    updated_at = models.DateTimeField(auto_now=True)       # auto update on save

    def __str__(self):
        return self.title
