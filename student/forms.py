from django import forms
from .models import Project, License, Proposal, User, Booking
#from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field

class UserRegistration(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'name']

class ProjectModelForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['owner', 'username', 'name', 'professor', 'report', 'code', 'poster']
        widgets = {
            'owner':forms.HiddenInput(),#預設
            'username':forms.HiddenInput(),#預設
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'report': forms.FileInput(attrs={'class': 'form-control'}),
            'code': forms.FileInput(attrs={'class': 'form-control'}),
            'poster': forms.FileInput(attrs={'class': 'form-control'}),
            'professor': forms.TextInput(attrs={'class': 'form-control'}),
            
        }
        labels = {
            'name': '專題名稱',
            'report': '專題報告書',
            'professor': '指導教授',
        }

class LicenseModelForm(forms.ModelForm):

    class Meta:
        model = License
        fields = ['owner', 'username', 'name', 'level', 'acqDate', 'organizer', 'image']
        widgets = {
            'owner':forms.HiddenInput(),#預設
            'username':forms.HiddenInput(),#預設
            'name':forms.TextInput(attrs={'class': 'form-control'}),
            'level':forms.Select(attrs={'class': 'form-control'}),
            'acqDate':forms.DateInput(attrs={'class': 'form-control'}),
            'organizer':forms.TextInput(attrs={'class': 'form-control'}),
            'image':forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '證照名稱(請填全名)',
            'level': '證照級別',
            'acqDate': '取得日期',
            'organizer': '主辦單位',
            'image': '證明截圖',
        }

class ProposalModelForm(forms.ModelForm):

    class Meta:
        model = Proposal
        fields = ['owner', 'name', 'professor', 'type', 'postDate', 'postProof', 'letter',
                  'post', 'seminarName', 'seminarDate', 'journalNumber', 'username']
        widgets = {
            'owner':forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'professor': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'postDate': forms.DateInput(attrs={'class': 'form-control'}),
            'postProof': forms.FileInput(attrs={'class': 'form-control'}),
            'letter': forms.FileInput(attrs={'class': 'form-control'}),
            'post': forms.Select(attrs={'class': 'form-control'}),
            'seminarName': forms.TextInput(attrs={'class': 'form-control'}),
            'seminarDate': forms.DateInput(attrs={'class': 'form-control'}),
            'journalNumber': forms.NumberInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'username': forms.HiddenInput(),
        }
        labels = {
            'name': '論文名稱',
            'file': '專題壓縮檔案',
            'professor': '指導教授',
            'postDate':'論文發表日期',
            'type': '日碩/職碩',
            'postProof':'論文發表證明拍照/截圖',
            'letter':'同意函/接受函',
            'post':'請選擇研討會/期刊',
            'seminarName':'研討會/期刊名稱(請填全名)',
            'seminarDate':'研討會/期刊發行日期',
            'journalNumber':'期刊刊號',
        }

class LicenseEditForm(forms.ModelForm):

    class Meta:
        model = License
        fields = ['name', 'acqDate', 'organizer', 'image']
        widgets = {
            'name':forms.TextInput(attrs={'class': 'form-control'}),
            'acqDate':forms.DateInput(attrs={'class': 'form-control'}),
            'organizer':forms.TextInput(attrs={'class': 'form-control'}),
            'image':forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '證照名稱(請填全名)',
            'acqDate': '取得日期',
            'organizer': '主辦單位',
            'image': '證明截圖',
        }

class LicenseAuditForm(forms.ModelForm):

    class Meta:
        model = License
        fields = ['name', 'level', 'acqDate', 'organizer', 'pazz',]
        widgets = {
            'name':forms.TextInput(attrs={'class': 'form-control'}),
            'level':forms.Select(attrs={'class': 'form-control'}),
            'acqDate':forms.DateInput(attrs={'class': 'form-control'}),
            'organizer':forms.TextInput(attrs={'class': 'form-control'}),
            'pazz':forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '證照名稱(請填全名)',
            'level': '證照級別',
            'acqDate': '取得日期',
            'organizer': '主辦單位',
            'pazz': '審核',
        }

class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name','username','password','graduateLevel',]
        widgets = {
            'name':forms.TextInput(attrs={'class': 'form-control'}),
            'username':forms.TextInput(attrs={'class': 'form-control'}),
            'password':forms.TextInput(attrs={'class': 'form-control'}),
            'graduateLevel':forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '姓名',
            'username': '學號',
            'password': '密碼',
            'graduateLevel': '畢業級',
        }

class BookingModelForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['username', 'paperName', 'author', 'professor', 'type',]

        widgets = {
            'username':forms.TextInput(attrs={'class': 'form-control'}),
            'paperName':forms.TextInput(attrs={'class': 'form-control'}),
            'author':forms.TextInput(attrs={'class': 'form-control'}),
            'professor':forms.TextInput(attrs={'class': 'form-control'}),
            'type':forms.HiddenInput(),
        }
        labels = {
            'username': '借閱人姓名',
            'paperName': '文本名稱',
            'author': '作者',
            'professor': '指導教授',
        }