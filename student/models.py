from time import time
from datetime import date
from django.db import models
from django.contrib import admin
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django import forms
import datetime

# Create your models here.

class User(AbstractUser):
    first_name = None
    last_name = None

    username = models.CharField(max_length=15, unique=True, null=True) #帳號
    name = models.CharField(max_length = 12) #姓名

    IDENTITY=((0, '學士'),
              (1, '管理員'),
              (2, '碩士'))
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
    user = models.OneToOneField(User, null = True, on_delete=models.PROTECT)
    name = models.CharField(max_length = 30) #論文名稱
    professor = models.CharField(max_length = 5)#指導教授
    postDate = models.DateField(default=timezone.now)#發表日期
    TYPE = ((1, '日間碩士班'),
            (2, '碩士在職專班'),)
    type = models.IntegerField(choices=TYPE, default=0)

    
    def __str__(self):
        return self.name
    
class Project(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, unique=True) #誰做這個專題的
    proposal = models.OneToOneField(Proposal, on_delete=models.PROTECT, blank = True, null = True)
    name = models.CharField(max_length = 30) #專題名稱
    report = models.FileField(upload_to = "Report/", default=None)#報告書電子檔
    poster = models.ImageField(upload_to = "Poster/", default=None)#海報或發表證明
    professor = models.CharField(max_length = 5)#指導教授
    
    FIELD = ((0, '軟體開發及程式設計'),
             (1, '網路及多媒體應用'),
             (2, '系統及演算法開發',))
    field = models.IntegerField(choices=FIELD, default=0)

    postDate = models.DateField(default = timezone.now, blank=True, null = True)#計畫發表日期
    letter = models.FileField(upload_to='Uploaded Files/', blank=True, null=True, default=None)#同意函

    TYPE = ((0, '大學部'),
            (1, '日間碩士班'),
            (2, '碩士在職專班'),)
    type = models.IntegerField(choices=TYPE, default=0)

    #研討會或期刊
    POST = ((0, '研討會'),
            (1, '期刊'),)
    post = models.PositiveIntegerField(choices=POST, default = 0, blank=True, null = True)
    seminarDate = models.DateTimeField(blank=True, null = True)#研討會或期刊發行日期
    seminarName = models.CharField(max_length=20, blank=True, null = True)#研討會或期刊名稱
    journalNumber = models.DecimalField(max_digits = 10, decimal_places = 0, blank=True, null = True)#期刊刊號

    class Meta:
        ordering = ["user"]

    def __str__(self):
        return self.name
    
class Paper(models.Model):
    project = models.ForeignKey(Project, null = True, on_delete=models.PROTECT)
    barCode = models.CharField(max_length=20, null=True)
    lendTimes = models.IntegerField(default=0)


    def __str__(self):
        return self.barCode
    
    class Meta:
        ordering = ['lendTimes']
    
class Booking(models.Model):
    user = models.ForeignKey(User, null = True, on_delete=models.PROTECT)
    paper = models.ForeignKey(Paper, null = True, on_delete=models.PROTECT)

    underTaker = models.CharField(null = True, blank = True, max_length=10)
    
    STATE = ((0, '已預約'),
             (1, '已借閱'),
             (2, '已歸還'))
    state = models.IntegerField(choices = STATE, default = 0)
    bookingDate = models.DateField(null = True)
    bookingTime = models.TimeField(null = True)
    takingDate = models.DateField(null = True, blank = True)
    takingTime = models.TimeField(null = True, blank = True)

    
    def __str__(self):
        return self.user.name
    
    class Meta:
        ordering = ['state', '-id']