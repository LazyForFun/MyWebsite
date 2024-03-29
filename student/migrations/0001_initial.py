# Generated by Django 3.2 on 2023-02-17 04:29

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=15, null=True, unique=True)),
                ('name', models.CharField(max_length=12)),
                ('identity', models.IntegerField(choices=[(0, 'student'), (1, 'professor'), (2, 'master')], default=0)),
                ('graduateLevel', models.DecimalField(decimal_places=0, default=2027, max_digits=3)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['id', 'username'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proposal_name', models.CharField(max_length=30)),
                ('proposal_professor', models.CharField(max_length=5)),
                ('proposal_graduateLevel', models.DecimalField(decimal_places=0, default=112, max_digits=3)),
                ('proposal_postDate', models.DateField(default=django.utils.timezone.now)),
                ('proposal_postProof', models.FileField(default=None, upload_to='image/')),
                ('proposal_letter', models.FileField(default=None, upload_to='Uploaded Files/')),
                ('proposal_post', models.PositiveIntegerField(choices=[(0, '研討會'), (1, '期刊')], default=0)),
                ('proposal_seminarDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('proposal_seminarName', models.CharField(max_length=20)),
                ('proposal_journalNumber', models.DecimalField(blank=True, decimal_places=0, max_digits=10)),
                ('proposal_owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_username', models.CharField(max_length=12)),
                ('project_name', models.CharField(max_length=30)),
                ('project_report', models.FileField(default=None, upload_to='Report/')),
                ('project_code', models.FileField(default=None, upload_to='Code/')),
                ('project_poster', models.ImageField(default=None, upload_to='Poster/')),
                ('project_professor', models.CharField(max_length=5)),
                ('project_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['project_owner'],
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_username', models.CharField(max_length=12)),
                ('license_name', models.CharField(max_length=30)),
                ('license_acqDate', models.DateField(default=django.utils.timezone.now)),
                ('license_organizer', models.CharField(max_length=30)),
                ('license_level', models.CharField(choices=[('A', 'A'), ('B', 'B')], default=0, max_length=1)),
                ('license_pass', models.IntegerField(choices=[(0, '審核中'), (1, '通過'), (2, '未通過')], default=0)),
                ('license_image', models.ImageField(default=None, upload_to='image/')),
                ('license_owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['license_owner', 'license_level'],
            },
        ),
    ]
