# Generated by Django 3.2.13 on 2022-05-18 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airtable_generator', '0003_auto_20220513_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='button_classes',
            field=models.CharField(default='button', max_length=500),
        ),
    ]
