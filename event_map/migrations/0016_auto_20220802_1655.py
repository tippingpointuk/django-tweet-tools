# Generated by Django 3.2.14 on 2022-08-02 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_map', '0015_eventmap_action_network_ec_syncs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventmap',
            name='action_network_ec_syncs',
            field=models.ManyToManyField(null=True, to='event_map.ActionNetworkECSync'),
        ),
        migrations.AlterField(
            model_name='eventmap',
            name='airtable_syncs',
            field=models.ManyToManyField(null=True, to='event_map.AirtableSync'),
        ),
    ]