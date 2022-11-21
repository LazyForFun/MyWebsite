from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, UpdateView
from django .contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.conf import settings 
from django.http import HttpResponse
from django.utils.http import urlquote

import os, csv
import pandas as pd

from .forms import ProjectModelForm, LicenseModelForm, ProposalModelForm, LicenseEditForm, LicenseAuditForm
from .models import User, Project,License, Proposal
from . import forms
from . filters import ProjectFilter, LicenseFilter

# Create your views here.
class Home(View):

    def get(self, request):
        return render(request, 'Home.html')

class LoginView(View):

    def get(request):
        return render(request, 'registration/login.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('Home'))

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user.is_active is True:
            auth.login(request, user)
            return redirect(reverse('Home'))
        else:
            return render(request, 'registration/Login.html', locals())

class LogoutView(View):

    def post(self, request):
        auth.logout(request)
        return redirect(reverse('Home'))

class UserProject(View):
    
    def index(request, pk):
        project = Project.objects.filter(project_owner = request.user.id)
        context = {
            'project': project,
        }

        return render(request, 'UserProject.html', context)

class UserLicense(View):
    
    def index(request, pk):
        license = License.objects.filter(license_owner = request.user.id)
        context = {
            'license': license,
        }

        return render(request, 'UserLicense.html', context)

class PassProject(LoginRequiredMixin, View):

    def index(request, pk):
        user = User.objects.get(id = request.user.id)
        form = ProjectModelForm(initial={'project_owner': user.id, 'project_username': user.name})
        if request.method == "POST":
            form = ProjectModelForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('/Home')

        context = {
            'form': form,
        }

        return render(request, 'PassProject.html', context)

class PassLicense(LoginRequiredMixin, View):

    def index(request, pk):
        user = User.objects.get(id = request.user.id)
        form = LicenseModelForm(initial={'license_owner': user.id, 'license_username': user.name})
        if request.method == "POST":
            form = LicenseModelForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('/Home')

        context = {
            'form': form,
        }

        return render(request, 'PassLicense.html', context)

class PassProposal(LoginRequiredMixin, View):

    def index(request, pk):
        user = User.objects.get(id = request.user.id)
        form = ProposalModelForm(initial={'proposal_owner': user.id})
        if request.method == "POST":
            form = ProposalModelForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('/Home')

        context = {
            'form': form,
        }

        return render(request, 'PassProposal.html', context)

class CheckLicense(LoginRequiredMixin, View):
    
    def index(request):
        license = License.objects.filter(license_pass = 0)
        context = {
            'license': license
        }
        return render(request, 'CheckLicense.html', context)

class DisplayLicense(LoginRequiredMixin, View):

    def get(self, request):
        queryDict = {}
        getValue = self.request.GET
        if getValue:
            if 'q' in getValue:
                queryDict['license_username__icontains'] = getValue['q']
            if 'level' in getValue:
                level = getValue['level']
                if level:
                    queryDict['license_level'] = getValue['level']
            if 'pass' in getValue:
                pazz = getValue['pass']
                if pazz:
                    queryDict['license_pass'] = getValue['pass']
            license = License.objects.filter(**queryDict)
        else:
            license = License.objects.all()

        context = {
            'license': license
        }
        return render(request, 'DisplayLicense.html', context)

    def post(self, request):
        queryDict = {}
        getValue = self.request.POST
        if getValue:
            if 'q' in getValue:
                queryDict['license_username__icontains'] = getValue['q']
            if 'level' in getValue:
                level = getValue['level']
                if level:
                    queryDict['license_level'] = getValue['level']
            if 'pass' in getValue:
                pazz = getValue['pass']
                if pazz:
                    queryDict['license_pass'] = getValue['pass']
            licenses = License.objects.filter(**queryDict).values_list('license_username','license_owner__username' , 'license_name' , 'license_acqDate','license_level',)
        else:
            licenses = License.objects.all().values_list('license_username','license_owner__username' , 'license_name' , 'license_acqDate','license_level',)
        response = HttpResponse(content_type='text/csv')
        response.charset = 'utf-8-sig'
        response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("證照紀錄.csv"))         
        writer = csv.writer(response)       
                
        
        writer.writerow(['姓名','學號','證照名稱','取得日期','級別',])
        
        for license in licenses:
            writer.writerow(license)
        return response
    

class DisplayProject(LoginRequiredMixin, ListView):
        
    def get(self, request):
        queryDict = {}
        getValue = self.request.GET
        if getValue:
            if 'q' in getValue:
                queryDict['project_username__icontains'] = getValue['q']
            if 'graduateLevel' in getValue:
                queryDict['project_graduateLevel'] = getValue['graduateLevel']
            if 'professor' in getValue:
                queryDict['project_professor__icontains'] = getValue['professor']
            project = Project.objects.filter(**queryDict)
        else:
            project = Project.objects.all()

        context = {
            'project': project
        }
        return render(request, 'DisplayProject.html', context)

    def post(self, request):
        queryDict = {}
        getValue = self.request.POST
        if getValue:
            if 'q' in getValue:
                queryDict['project_username__icontains'] = getValue['q']
            if 'graduateLevel' in getValue:
                queryDict['project_graduateLevel'] = request.POST.get('graduateLevel', None)
            if 'professor' in getValue:
                queryDict['project_professor__icontains'] = getValue['professor']
            projects = Project.objects.filter(**queryDict).values_list('project_username','project_owner__username' , 'project_graduateLevel' , 'project_professor','project_name',)
        else:
            projects = Project.objects.all().values_list('project_username','project_owner__username' , 'project_graduateLevel' , 'project_professor','project_name',)
        response = HttpResponse(content_type='text/csv')
        response.charset = 'utf-8-sig'
        response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("專題紀錄.csv"))         
        writer = csv.writer(response)       
                
        
        writer.writerow(['姓名','學號','畢業級','指導教授','專題名稱',])
        
        for project in projects:
            writer.writerow(project)
        return response
    

class ImportAndExport(LoginRequiredMixin, View):
    
    def Import_csv(request):               
        try:
            if request.method == 'POST' and request.FILES['myfile']:
          
                myfile = request.FILES['myfile']  
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                uploaded_file_url = fs.url(filename) 
                exceldata = pd.read_csv("."+uploaded_file_url,encoding='utf-8')
                dbframe = exceldata
                for dbframe in dbframe.itertuples():
                    obj = User.objects.create(username=dbframe.username,password=make_password(dbframe.password), name=dbframe.name,)
                    print(type(obj))
                    obj.save()
 
                return render(request, 'Home.html', {
                    'uploaded_file_url': uploaded_file_url
                })    
        except Exception as identifier:            
            print(identifier)
     
        return render(request, 'ImportAndExport.html',{})


class AuditLicense(LoginRequiredMixin, UpdateView):
    model = License
    fileds = '__all__'
    
    
    form_class = LicenseAuditForm

    template_name = 'EditLicense.html'

    success_url = '/CheckLicense'

class EditLicense(LoginRequiredMixin, UpdateView):
    model = License
    fileds = '__all__'
    
    form_class = LicenseEditForm

    template_name = 'EditLicense.html'

    success_url = '/Home'

class EditProject(LoginRequiredMixin, UpdateView):
    model = Project
    fileds = '__all__'
    
    form_class = ProjectModelForm

    template_name = 'EditProject.html'

    success_url = '/Home'

class DeleteLicense(LoginRequiredMixin, DeleteView):
    model = License
    fileds = '__all__'

    template_name = 'DeleteLicense.html'

    success_url = '/Home'