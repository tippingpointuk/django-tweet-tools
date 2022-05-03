from django.db import models

# Create your models here.


class Config(models.Model):
    name = models.CharField(max_length=100)
    # Targets, e.g. MPs
    target_base = models.CharField(max_length=50)
    target_table = models.CharField(max_length=50)
    # Tweets base
    tweets_base = models.CharField(max_length=50)
    tweets_table = models.CharField(max_length=50)

    def __str__(self):
        return self.name
