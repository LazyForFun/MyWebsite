from socket import fromshare
from django import forms
from .models import Project, License, Proposal, User
#from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Layout, Div, Submit, Row, Column, Field

class UserRegistration(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'name']

class ProjectModelForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['project_owner', 'project_username', 'project_name', 'project_professor', 'project_graduateLevel', 'project_report', 'project_code', 'project_poster']
        widgets = {
            'project_owner':forms.HiddenInput(),#預設
            'project_username':forms.HiddenInput(),#預設
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_report': forms.FileInput(attrs={'class': 'form-control'}),
            'project_code': forms.FileInput(attrs={'class': 'form-control'}),
            'project_poster': forms.FileInput(attrs={'class': 'form-control'}),
            'project_graduateLevel': forms.NumberInput(attrs={'class': 'form-control'}),
            'project_professor': forms.TextInput(attrs={'class': 'form-control'}),
            
        }
        labels = {
            'project_name': '專題名稱',
            'project_report': '專題報告書',
            'project_professor': '指導教授',
            'project_graduateLevel': '畢業級',
        }

class LicenseModelForm(forms.ModelForm):

    class Meta:
        model = License
        fields = ['license_owner', 'license_username', 'license_name', 'license_level', 'license_acqDate', 'license_organizer', 'license_image']
        widgets = {
            'license_owner':forms.HiddenInput(),#預設
            'license_username':forms.HiddenInput(),#預設
            'license_name':forms.TextInput(attrs={'class': 'form-control'}),
            'license_level':forms.Select(attrs={'class': 'form-control'}),
            'license_acqDate':forms.DateInput(attrs={'class': 'form-control'}),
            'license_organizer':forms.TextInput(attrs={'class': 'form-control'}),
            'license_image':forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'license_name': '證照名稱(請填全名)',
            'license_level': '證照級別',
            'license_acqDate': '取得日期',
            'license_organizer': '主辦單位',
            'license_image': '證明截圖',
        }

class ProposalModelForm(forms.ModelForm):

    class Meta:
        model = Proposal
        fields = ['proposal_owner', 'proposal_name', 'proposal_professor', 'proposal_graduateLevel', 'proposal_postDate', 'proposal_postProof', 'proposal_letter',
                  'proposal_post', 'proposal_seminarName', 'proposal_seminarDate', 'proposal_journalNumber']
        widgets = {
            'proposal_owner':forms.HiddenInput(),
            'proposal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'proposal_professor': forms.TextInput(attrs={'class': 'form-control'}),
            'proposal_graduateLevel': forms.NumberInput(attrs={'class': 'form-control'}),
            'proposal_postDate': forms.DateInput(attrs={'class': 'form-control'}),
            'proposal_postProof': forms.FileInput(attrs={'class': 'form-control'}),
            'proposal_letter': forms.FileInput(attrs={'class': 'form-control'}),
            'proposal_post': forms.Select(attrs={'class': 'form-control'}),
            'proposal_seminarName': forms.TextInput(attrs={'class': 'form-control'}),
            'proposal_seminarDate': forms.DateInput(attrs={'class': 'form-control'}),
            'proposal_journalNumber': forms.NumberInput(attrs={'class': 'form-control'}),
            'proposal_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'proposal_name': '論文名稱',
            'proposal_file': '專題壓縮檔案',
            'proposal_professor': '指導教授',
            'proposal_graduateLevel':'畢業級',
            'proposal_postDate':'論文發表日期',
            'proposal_postProof':'論文發表證明拍照/截圖',
            'proposal_letter':'同意函/接受函',
            'proposal_post':'請選擇研討會/期刊',
            'proposal_seminarName':'研討會/期刊名稱(請填全名)',
            'proposal_seminarDate':'研討會/期刊發行日期',
            'proposal_journalNumber':'期刊刊號',
        }

class LicenseEditForm(forms.ModelForm):

    class Meta:
        model = License
        fields = ['license_name', 'license_acqDate', 'license_organizer', 'license_image']
        widgets = {
            'license_name':forms.TextInput(attrs={'class': 'form-control'}),
            'license_acqDate':forms.DateInput(attrs={'class': 'form-control'}),
            'license_organizer':forms.TextInput(attrs={'class': 'form-control'}),
            'license_image':forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'license_name': '證照名稱(請填全名)',
            'license_acqDate': '取得日期',
            'license_organizer': '主辦單位',
            'license_image': '證明截圖',
        }

class LicenseAuditForm(forms.ModelForm):

    class Meta:
        model = License
        fields = ['license_name', 'license_level', 'license_acqDate', 'license_organizer', 'license_pass',]
        widgets = {
            'license_name':forms.TextInput(attrs={'class': 'form-control'}),
            'license_level':forms.Select(attrs={'class': 'form-control'}),
            'license_acqDate':forms.DateInput(attrs={'class': 'form-control'}),
            'license_organizer':forms.TextInput(attrs={'class': 'form-control'}),
            'license_pass':forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'license_name': '證照名稱(請填全名)',
            'license_level': '證照級別',
            'license_acqDate': '取得日期',
            'license_organizer': '主辦單位',
            'license_pass': '審核',
        }