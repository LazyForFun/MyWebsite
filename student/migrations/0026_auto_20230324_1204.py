# Generated by Django 3.2 on 2023-03-24 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0025_alter_project_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='takingDate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='takingTime',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='identity',
            field=models.IntegerField(choices=[(0, '學士'), (1, '管理員'), (2, '碩士')], default=0),
        ),
    ]