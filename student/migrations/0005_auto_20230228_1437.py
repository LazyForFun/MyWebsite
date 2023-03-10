# Generated by Django 3.2 on 2023-02-28 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_remove_proposal_graduatelevel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=12)),
                ('paperName', models.CharField(max_length=30)),
                ('professor', models.CharField(max_length=12)),
                ('type', models.IntegerField(choices=[(0, '論文'), (1, '專題報告書')], default=0)),
            ],
        ),
        migrations.AddField(
            model_name='proposal',
            name='username',
            field=models.CharField(max_length=12, null=True),
        ),
    ]