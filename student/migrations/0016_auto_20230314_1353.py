# Generated by Django 3.2 on 2023-03-14 05:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0015_auto_20230313_2004'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='takingTime',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='bookingTime',
            field=models.TimeField(default=datetime.datetime(2023, 3, 14, 13, 53, 45, 149245)),
        ),
    ]
