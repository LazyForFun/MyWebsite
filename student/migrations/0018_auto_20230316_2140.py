# Generated by Django 3.2 on 2023-03-16 13:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0017_auto_20230316_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='bookingTime',
            field=models.TimeField(default=datetime.datetime(2023, 3, 16, 21, 40, 54, 777318)),
        ),
        migrations.AlterField(
            model_name='booking',
            name='state',
            field=models.IntegerField(choices=[(0, '已預約'), (1, '已借閱'), (2, '已完成')], default=0),
        ),
    ]
