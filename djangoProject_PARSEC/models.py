from django.db import models



class Clients(models.Model):
    name = models.CharField(max_length=300)
    email = models.CharField(max_length=100)
