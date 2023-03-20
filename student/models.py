from time import time
from datetime import date
from django.db import models
from django.contrib import admin
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, UserManager
from django import forms
import datetime

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
    graduateLevel = models.DecimalField(max_digits = 4, decimal_places = 0, default = timezone.now().year + 4)#畢業級

    USER_NAME_FIELD = 'username'

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username

    def not_graduated(self):
        return self.graduateLevel + 2 >= timezone.now().year

    def get_graduate_year(self):
        return (self.graduateLevel - 1911)


class Project(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, unique=True) #誰做這個專題的
    name = models.CharField(max_length = 30) #專題名稱
    report = models.FileField(upload_to = "Report/", default=None)
    poster = models.ImageField(upload_to = "Poster/", default=None)
    professor = models.CharField(max_length = 5)#指導教授
    
    FIELD = ((0, '軟體開發及程式設計'),
            (1, '網路及多媒體應用'))
    field = models.IntegerField(choices=FIELD, default=0)

    class Meta:
        ordering = ["user"]

    def __str__(self):
        return self.name

class License(models.Model):
    user = models.ForeignKey(User, null = True, on_delete=models.PROTECT)
    name = models.CharField(max_length = 30) #證照名稱
    acqDate = models.DateField(default=timezone.now)#證照取得日期
    organizer = models.CharField(max_length = 30)#主辦單位

    LEVEL = (('A', 'A'),
             ('B', 'B',))
    level = models.CharField(max_length = 1, choices = LEVEL, default = 0)

    PASS = ((0, '審核中'),
            (1, '通過'),
            (2, '未通過'),)#審核狀態

    pazz = models.IntegerField(choices = PASS, default = 0)#證照是否通過審核
    image = models.ImageField(upload_to='image/', blank=False, null=False, default=None)

    class Meta:
        ordering = ["user__username", "level"]

    def __str__(self):
        return self.name

class Proposal(models.Model):
    user = models.ForeignKey(User, null = True, on_delete=models.PROTECT)
    name = models.CharField(max_length = 30) #論文名稱
    professor = models.CharField(max_length = 5)#指導教授
    postDate = models.DateField(default = timezone.now)#計畫發表日期
    postProof = models.FileField(upload_to='image/', blank=False, null=False, default=None)#發表證明
    letter = models.FileField(upload_to='Uploaded Files/', blank=False, null=False, default=None)#同意函

    TYPE = ((0, '日間碩士班'),
            (1, '碩士在職專班'),)
    type = models.IntegerField(choices=TYPE, default=0)

    #研討會或期刊
    POST = ((0, '研討會'),
            (1, '期刊'),)
    post = models.PositiveIntegerField(choices=POST, default = 0)
    seminarDate = models.DateTimeField(default=timezone.now)#研討會或期刊發行日期
    seminarName = models.CharField(max_length=20)#研討會或期刊名稱
    journalNumber = models.DecimalField(max_digits = 10, decimal_places = 0, blank=True)#期刊刊號

    def __str__(self):
        return self.name
    
class Paper(models.Model):
    author = models.CharField(max_length=12)
    name = models.CharField(max_length=30)
    TYPE = ((0, '日間碩士班論文'),
            (1, '碩士在職專班論文'),
            (2, '大學部專題報告書'),)
    type = models.IntegerField(choices=TYPE, default = 0)
    barCode = models.CharField(max_length=20, null=True)

    professor = models.CharField(max_length=12)

    def __str__(self):
        return self.name
    
class Booking(models.Model):
    user = models.ForeignKey(User, null = True, on_delete=models.PROTECT)
    paper = models.ForeignKey(Paper, null = True, on_delete=models.PROTECT)
    
    STATE = ((0, '已預約'),
             (1, '已借閱'),
             (2, '已完成'))
    state = models.IntegerField(choices = STATE, default = 0)
    bookingDate = models.DateField(default=timezone.now())
    bookingTime = models.TimeField(default=datetime.datetime.now())
    takingDate = models.DateField(default=timezone.now())
    takingTime = models.TimeField(null = True)

    
    def __str__(self):
        return self.user.name
    
    class Meta:
        ordering = ['-id']