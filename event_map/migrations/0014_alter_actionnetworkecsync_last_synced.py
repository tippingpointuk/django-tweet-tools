# Generated by Django 3.2.14 on 2022-07-29 00:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('event_map', '0013_auto_20220729_0034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionnetworkecsync',
            name='last_synced',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
