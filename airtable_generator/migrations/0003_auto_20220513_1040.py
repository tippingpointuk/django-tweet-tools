# Generated by Django 3.2.13 on 2022-05-13 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airtable_generator', '0002_config_api_key_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='action_network_advocacy_campaign',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='config',
            name='action_network_api_key_name',
            field=models.CharField(default='AN_API_KEY', max_length=100, null=True),
        ),
    ]