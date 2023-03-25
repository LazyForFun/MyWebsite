# Generated by Django 3.2 on 2023-03-22 05:15

from django.db import migrations, models
import student.validators


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0024_auto_20230321_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=15, null=True, unique=True, validators=[student.validators.validateUsername]),
        ),
    ]
