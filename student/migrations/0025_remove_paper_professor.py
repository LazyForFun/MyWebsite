# Generated by Django 3.2 on 2023-03-21 09:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0024_auto_20230321_1737'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='professor',
        ),
    ]
