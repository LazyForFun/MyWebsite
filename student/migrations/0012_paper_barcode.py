# Generated by Django 3.2 on 2023-03-13 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_auto_20230313_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='barCode',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
