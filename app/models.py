from django.db import models


# Create your models here.
class MyModel(models.Model):
    current_time = models.IntegerField()
