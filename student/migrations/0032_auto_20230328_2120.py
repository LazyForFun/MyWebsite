# Generated by Django 3.2 on 2023-03-28 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0031_alter_user_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='postDate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='postDate',
            field=models.DateField(blank=True, null=True),
        ),
    ]