from django.db import models

# Create your models here.


class Client(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} ({self.email})'
    