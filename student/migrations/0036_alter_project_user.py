# Generated by Django 3.2 on 2023-04-24 04:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0035_auto_20230424_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
