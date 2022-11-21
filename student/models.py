from time import time
from django.db import models
from django.contrib import admin
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, UserManager
from django import forms

# Create your models here.

class User(AbstractUser):
    first_name = None
    last_name = None

    username = models.CharField(max_length=15, unique=True, null=True) #帳號
    name = models.CharField(max_length = 12) #姓名

    IDENTITY=((0, 'student'),
              (1, 'professor'),
              (2, 'master'))
    identity = models.IntegerField(choices=IDENTITY, default=0)

    USER_NAME_FIELD = 'username'

    class Meta:
        ordering = ["id", "username"]

    def __str__(self):
        return self.username

class Project(models.Model):
    project_owner = models.ForeignKey(User, on_delete=models.CASCADE) #誰做這個專題的
    project_username = models.CharField(max_length = 12)
    project_name = models.CharField(max_length = 30) #專題名稱
    project_report = models.FileField(upload_to = "Report/", default=None)
    project_code = models.FileField(upload_to = "Code/", default=None)
    project_poster = models.ImageField(upload_to = "Poster/", default=None)
    project_professor = models.CharField(max_length = 5)#指導教授
    project_graduateLevel = models.DecimalField(max_digits = 3, decimal_places = 0, default = 112)#畢業級
    
    class Meta:
        ordering = ["project_graduateLevel", "project_owner"]

    def __str__(self):
        return self.project_name

class License(models.Model):
    license_owner = models.ForeignKey(User, null = True, on_delete=models.CASCADE)
    license_username = models.CharField(max_length = 12)
    license_name = models.CharField(max_length = 30) #證照名稱
    license_acqDate = models.DateField(default=timezone.now)#證照取得日期
    license_organizer = models.CharField(max_length = 30)#主辦單位

    LICENSE_LEVEL = (('A', 'A'),
                     ('B', 'B',))
    license_level = models.CharField(max_length = 1, choices = LICENSE_LEVEL, default = 0)

    LICENSE_PASS = ((0, '審核中'),
                      (1, '通過'),
                      (2, '未通過'),)#審核狀態

    license_pass = models.IntegerField(choices = LICENSE_PASS, default = 0)#證照是否通過審核
    license_image = models.ImageField(upload_to='image/', blank=False, null=False, default=None)

    class Meta:
        ordering = ["license_owner", "license_level"]

    def __str__(self):
        return self.license_name

class Proposal(models.Model):
    proposal_owner = models.ForeignKey(User, on_delete = models.PROTECT)
    proposal_name = models.CharField(max_length = 30) #論文名稱
    proposal_professor = models.CharField(max_length = 5)#指導教授
    proposal_graduateLevel = models.DecimalField(max_digits = 3, decimal_places = 0, default = 112)#畢業級
    proposal_postDate = models.DateField(default = timezone.now)#計畫發表日期
    proposal_postProof = models.FileField(upload_to='image/', blank=False, null=False, default=None)#發表證明
    proposal_letter = models.FileField(upload_to='Uploaded Files/', blank=False, null=False, default=None)#同意函

    #研討會或期刊
    PROPOSAL_POST = ((0, '研討會'),
                     (1, '期刊',))
    proposal_post = models.PositiveIntegerField(choices=PROPOSAL_POST, default = 0)
    proposal_seminarDate = models.DateTimeField(default=timezone.now)#研討會或期刊發行日期
    proposal_seminarName = models.CharField(max_length=20)#研討會或期刊名稱
    proposal_journalNumber = models.DecimalField(max_digits = 10, decimal_places = 0, blank=True)#期刊刊號

    def __str__(self):
        return self.proposal_name