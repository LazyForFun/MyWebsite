from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, UpdateView, CreateView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings 
from django.http import HttpResponse

from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

import os, csv
import pandas as pd
import django.utils.timezone as timezone
from django.utils.http import urlquote

from .forms import ProjectModelForm, LicenseModelForm, ProposalModelForm, LicenseEditForm, LicenseAuditForm, BookingModelForm
from .models import User, Project,License, Proposal, Booking, Paper
from . import forms

# Create your views here.

class Home(View):

    def get(self, request):
        return render(request, 'Home.html')
    
class BorrowPaper(ListView):

    def get(self, request):
        queryDict = {}
        getValue = self.request.GET
        if getValue:
            if 'username' in getValue:
                queryDict['username__icontains'] = getValue['username']
            if 'type' in getValue and int(getValue['type']) >= 0:
                queryDict['type'] = int(getValue['type'])
            if 'professor' in getValue:
                queryDict['professor__icontains'] = getValue['professor']
            paper = Paper.objects.filter(**queryDict)
        else:
            paper = Paper.objects.none()

        limit = 10
        paginator=Paginator(paper, limit)

        page=request.GET.get('page')
        
        try:
            paper=paginator.page(page)
        except PageNotAnInteger:
            paper=paginator.page(1)
        except EmptyPage:
            paper=paginator.page(paginator.num_pages)
        context = {
            'paper': paper,
        }

        return render(request, 'BorrowPaper.html', context)
    
class BookingProject(CreateView):

    model = Booking
    fileds = '__all__'
    
    form_class = BookingModelForm

    def get_initial(self):
        pk=self.kwargs['pk']
        project = Project.objects.get(id=pk)
        initial = {'paperName': project.name, 'author': project.username, 'professor': project.professor, 'type': 2}
        return initial

    template_name = 'Booking.html'

    def get_success_url(self):
        return reverse('Home')

class BookingPaper(CreateView):

    model = Booking
    fileds = '__all__'
    
    form_class = BookingModelForm

    def get_initial(self):
        pk=self.kwargs['pk']
        proposal = Proposal.objects.get(id=pk)
        initial = {'paperName': proposal.name, 'author': proposal.username, 'professor': proposal.professor, 'type': proposal.type}
        return initial

    template_name = 'Booking.html'

    def get_success_url(self):
        return reverse('Home')

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
    
    def get(self, request, pk):
        project = Project.objects.filter(owner = request.user.id)
        context = {
            'project': project,
        }

        return render(request, 'UserProject.html', context)

class UserLicense(View):
    
    def get(self, request, pk):
        license = License.objects.filter(owner = request.user.id)
        context = {
            'license': license,
        }

        return render(request, 'UserLicense.html', context)

class PassProject(LoginRequiredMixin, CreateView):

    def get(self, request, pk):
        user = User.objects.get(id = pk)
        form = ProjectModelForm(initial={'owner': user.id, 'username': user.name})
        context = {
            'form': form,
        }
        return render(request, 'PassProject.html', context)
    
    def post(self, request, pk):
        form = ProjectModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            data = Project.objects.get(owner=self.kwargs['pk'])
            paper = Paper.objects.create(username=data.username, name=data.name, type=2, professor=data.professor)
            paper.save()
            return redirect('Home')

        context = {
            'form': form,
        }
        return render(request, 'PassProject.html', context)


class PassLicense(LoginRequiredMixin, View):

    def get(self, request, pk):
        user = User.objects.get(id = pk)
        form = LicenseModelForm(initial={'owner': user.id, 'username': user.name})
        if request.method == "POST":
            form = LicenseModelForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('Home')

        context = {
            'form': form,
        }

        return render(request, 'PassLicense.html', context)
    
    def post(self, request, pk):
        form = LicenseModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('Home')

        context = {
            'form': form,
        }

        return render(request, 'PassLicense.html', context)

class PassProposal(LoginRequiredMixin, View):

    def get(self, request, pk):
        user = User.objects.get(id = request.user.id)
        form = ProposalModelForm(initial={'owner': user.id})
        if request.method == "POST":
            form = ProposalModelForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                data = Proposal.objects.get(owner=self.kwargs['pk'])
                paper = Paper.objects.create(username=data.username, name=data.name, type=data.type, professor=data.professor)
                return redirect('/Home')

        context = {
            'form': form,
        }

        return render(request, 'PassProposal.html', context)

class CheckLicense(LoginRequiredMixin, View):
    
    def get(self, request):
        license = License.objects.filter(pazz = 0)
        context = {
            'license': license
        }
        return render(request, 'CheckLicense.html', context)

class DisplayLicense(LoginRequiredMixin, View):

    def get(self, request):
        license = License.objects.exclude(pazz=0)
        context={
            'license': license
        }
        return render(request, "DisplayLicense.html", context)
    '''def get(self, request):
        queryDict = {}
        getValue = self.request.GET
        if getValue:
            if 'q' in getValue:
                queryDict['username__icontains'] = getValue['q']
            if 'level' in getValue:
                level = getValue['level']
                if level:
                    queryDict['level'] = getValue['level']
            if 'pass' in getValue:
                pazz = getValue['pass']
                if pazz:
                    queryDict['pass'] = getValue['pass']
            license = License.objects.filter(**queryDict)
        else:
            license = License.objects.all()

        context = {
            'license': license
        }
        return render(request, 'DisplayLicense.html', context)'''

    def post(self, request):
        queryDict = {}
        license = License.objects.all()
        getValue = self.request.POST
        if getValue:
            if 'q' in getValue:
                queryDict['username__icontains'] = getValue['q']
            if 'level' in getValue:
                level = getValue['level']
                if level:
                    queryDict['level'] = getValue['level']
            if 'pazz' in getValue:
                pazz = getValue['pazz']
                if pazz:
                    queryDict['pazz'] = getValue['pazz']

        if "export" in request.POST:
            license = License.objects.filter(**queryDict).values_list('username','owner__username' , 'name' , 'acqDate','level',)
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("證照紀錄.csv"))         
            writer = csv.writer(response)       
                
        
            writer.writerow(['姓名','學號','級別','證照名稱','取得日期','審核'])
        
            for license in license:
                writer.writerow(license)
            return response
        else:
            license = License.objects.filter(**queryDict)
            context = {
                'license': license
            }

        return render(request, 'DisplayLicense.html', context)
    

class DisplayProject(LoginRequiredMixin, ListView):
        
    def get(self, request):
        queryDict = {}
        getValue = self.request.GET
        if getValue:
            if 'q' in getValue:
                queryDict['username__icontains'] = getValue['q']
            if 'graduateLevel' in getValue:
                queryDict['graduateLevel'] = getValue['graduateLevel']
            if 'professor' in getValue:
                queryDict['professor__icontains'] = getValue['professor']
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
                queryDict['username__icontains'] = getValue['q']
            if 'graduateLevel' in getValue:
                queryDict['graduateLevel'] = request.POST.get('graduateLevel', None)
            if 'professor' in getValue:
                queryDict['professor__icontains'] = getValue['professor']
        
        if "export" in request.POST:
            project = Project.objects.filter(**queryDict).values_list('username','owner__username' , 'graduateLevel' , 'professor','name',)
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("專題紀錄.csv"))         
            writer = csv.writer(response)       
                
        
            writer.writerow(['姓名','學號','畢業級','指導教授','專題名稱',])
        
            for project in project:
                writer.writerow(project)
            return response
        else:
            project = Project.objects.filter(**queryDict)
            context = {
                'project': project
            }
            return render(request, 'DisplayProject.html', context)

        
    

class ImportAndExport(LoginRequiredMixin, View):
    
    def get(self, request):
        return render(request, 'ImportAndExport.html')
    def post(self, request):
        if "multi" in request.POST:
            try:
                if request.FILES['myfile']:
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
 
                    return render(request, 'ImportAndExport.html', {
                        'uploaded_file_url': uploaded_file_url
                    })
            except Exception as identifier:            
                print(identifier)

        elif "single" in request.POST:
            getValue = self.request.POST
            obj = User.objects.create(username=getValue['username'], password = make_password(getValue['password']), name=getValue['name'], graduateLevel=int(getValue['graduateLevel'])+1911)
            obj.save()
        return render(request, 'ImportAndExport.html')
    '''def Import_csv(request):               
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
     
        return render(request, 'ImportAndExport.html')'''

class SearchStudent(LoginRequiredMixin, ListView):
    
    model = User

    template_name = "SearchStudent.html"

    def get_queryset(self):
        queryDict = {}
        if "q1" or "q2" in self.request.GET:
            if "q1" in self.request.GET:
                queryDict['name__icontains'] = self.request.GET['q1']
            if "q2" in self.request.GET:
                queryDict['username__icontains'] = self.request.GET['q2']
            queryset = User.objects.filter(**queryDict)
        else:
            queryset = User.objects.all()

        return queryset
            

class ModifyStudentInfo(LoginRequiredMixin, UpdateView):
    
    def get(self, request, pk):
        student = User.objects.get(pk=pk)
        context={
            'student': student
        }
        return render(request, 'ModifyStudentInfo.html', context)

    def post(self, request, pk):
        getValue = self.request.POST
        student= User.objects.get(pk=pk)
        if getValue:
            if getValue['name'] != "":
                student.name = getValue['name']
            if getValue['username'] != "":
                student.username = getValue['username']
            if not check_password(getValue['password'], student.password) and getValue['password'] != "":
                student.password = make_password(getValue['password'])
            if int(getValue['graduateLevel']) + 1911 >= timezone.now().year:
                student.graduateLevel = int(getValue['graduateLevel']) + 1911

            student.save()

        return redirect(reverse('SearchStudent'))

class AuditLicense(LoginRequiredMixin, UpdateView):
    model = License
    fileds = '__all__'
    
    form_class = LicenseAuditForm

    template_name = 'EditLicense.html'

    def get_success_url(self):
        license = License.objects.filter(pazz=0)
        if license:
            pk = license.first().id
            return reverse('AuditLicense', kwargs={'pk': pk})
        else:
            return reverse('CheckLicense')
        
class BookingList(LoginRequiredMixin, ListView):
    
    def get(self, request):
        booking = Booking.objects.all()
        context={
            'booking': booking
        }
        return render(request, 'BookingList.html', context)
    
    def finishBooking(request, pk):
        finishbooking=Booking.objects.get(id=pk)
        finishbooking.delete()

        booking = Booking.objects.all()
        context={
            'booking': booking
        }
        return render(request, 'BookingList.html', context)
    
    def changeBookingState(request, pk):
        changeBookingState=Booking.objects.get(id=pk)
        changeBookingState.state = 1
        changeBookingState.save()

        booking = Booking.objects.all()
        context={
            'booking': booking
        }
        return render(request, 'BookingList.html', context)


class EditLicense(LoginRequiredMixin, UpdateView):
    model = License
    fileds = '__all__'
    
    form_class = LicenseEditForm

    template_name = 'EditLicense.html'

    def get_success_url(self):
        return reverse('UserLicense', kwargs={'pk':self.request.user.id})

class EditProject(LoginRequiredMixin, UpdateView):
    model = Project
    fileds = '__all__'
    
    form_class = ProjectModelForm

    template_name = 'EditProject.html'

    def get_success_url(self):
        return reverse('UserProject', kwargs={'pk':self.request.user.id})
    
class DeleteLicense(LoginRequiredMixin, DeleteView):
    model = License
    fileds = '__all__'

    template_name = 'DeleteLicense.html'


    def get_success_url(self):
        return reverse('UserLicense', kwargs={'pk':self.request.user.id})