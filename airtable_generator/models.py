from django.db import models


class Config(models.Model):
    name = models.CharField(max_length=100)
    # Targets, e.g. MPs
    target_base = models.CharField(max_length=50)
    target_table = models.CharField(max_length=50)
    # Tweets base
    tweets_base = models.CharField(max_length=50)
    tweets_table = models.CharField(max_length=50)
    # API key name
    api_key_name = models.CharField(max_length=100, default="AIRTABLE_API_KEY")
    # Advocacy Campaign & action network info
    action_network_api_key_name = models.CharField(
        max_length=100, default="AN_API_KEY", null=True)
    action_network_advocacy_campaign = models.CharField(
        max_length=200, null=True)
    action_network_advocacy_campaign_records = models.IntegerField(null=True)
    action_network_advocacy_campaign_records_last_updated = models.DateTimeField(
        null=True)

    def __str__(self):
        return self.name


# class TweetClicked(models.Model):
#     tweet = models.CharField(max_length=350)
#     target_name = models.CharField(max_length=100, null=True)
#     target_twitter = models.CharField(max_length=100, null=True)
#     config = models.ForeignKey('Config')
#
#     def __str__(self):
#         return self.tweet
