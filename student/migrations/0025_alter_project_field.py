# Generated by Django 3.2 on 2023-03-23 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0024_auto_20230321_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='field',
            field=models.IntegerField(choices=[(0, '軟體開發及程式設計'), (1, '網路及多媒體應用'), (2, '系統及演算法開發')], default=0),
        ),
    ]
