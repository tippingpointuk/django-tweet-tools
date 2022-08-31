from django.db import models


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    campaign_url = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    total_records = models.IntegerField(default=0)
    last_updated = models.DateTimeField()
    boost_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class CampaignGroup(models.Model):
    name = models.CharField(max_length=100)
    campaigns = models.ManyToManyField(Campaign)

    def __str__(self):
        return self.name
