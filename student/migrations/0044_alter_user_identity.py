# Generated by Django 3.2 on 2023-05-21 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0043_remove_proposal_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='identity',
            field=models.IntegerField(choices=[(0, '大學部'), (1, '管理員'), (2, '日間碩士班'), (3, '碩士在職專班'), (4, '系辦工讀生')], default=0),
        ),
    ]