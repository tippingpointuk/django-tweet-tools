# Generated by Django 3.2.13 on 2022-05-18 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airtable_generator', '0005_remove_config_button_classes'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='action_network_advocacy_campaign_records',
            field=models.IntegerField(null=True),
        ),
    ]