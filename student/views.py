from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, UpdateView, CreateView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings 
from django.http import HttpResponse, HttpResponseRedirect

from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail

from django.db.models.functions import ExtractYear

import os, csv, datetime, re
import pandas as pd
import django.utils.timezone as timezone
from django.utils.http import urlquote
from django.utils.crypto import get_random_string
from datetime import timedelta

from .forms import ProjectModelForm, LicenseModelForm, ProposalModelForm, LicenseEditForm, LicenseAuditForm, FinalModelForm
from .models import User, Project,License, Proposal, Booking, Paper
from . import forms
#csshare.tw@gmail.com
#cs@go.utaipei.edu.tw

# Create your views here.

limit = 10 #分頁器單個頁面的資料數
pattern = r'^(u\d{8}|csshare[0-9]+)$' #可使用的帳號格式

class Home(View):

    def get(self, request):
        return render(request, 'Home.html')
    
class Signin(View):
    def get(self, request):
        return render(request, 'registration/Signin.html')
    
    def post(self, request):
        getValue = self.request.POST
        try:
            checkUser = User.objects.get(username = getValue['username'])
        except User.DoesNotExist:
            checkUser = None
        if checkUser:
            messages.info(request, "使用者已存在!!")
            return redirect(reverse('Signin'))
        else:
            if re.match(pattern, getValue['username']):
                user = User.objects.create(name = getValue['name'], username = getValue['username'], password = make_password(getValue['password']), email = getValue['mail'], graduateLevel = int(getValue['graduateLevel']) + 1911, identity = getValue['identity'])
                user.save()
                messages.success(request, "註冊成功!!")
                return redirect(reverse('login'))
            else:
                messages.success(request, '請輸入有效的學號!!')
                return redirect(reverse('Signin'))
            
class EditPassword(LoginRequiredMixin, View):
    def get(self, request, pk):
        return render(request, 'registration/EditPassword.html')
    
    def post(self, request, pk):
        getValue = self.request.POST
        if check_password(getValue['password'], request.user.password):
            if getValue['password'] != getValue['newpassword']:
                if getValue['newpassword'] == getValue['newpassword_check']:
                    self.request.user.password = make_password(getValue['newpassword'])
                    self.request.user.save()
                    messages.success(request, "更改成功!")
                    return redirect(reverse('Home'))
                else:
                    messages.success(request, "密碼確認有誤...")

            else:
                messages.success(request, "新舊密碼不能相同")
        else:
            messages.success(request, '舊密碼不正確...')
        
        return redirect(reverse('EditPassword', kwargs={'pk':pk}))
    
class ForgetPassword(View):
    def get(self, request):
        return render(request, 'registration/ForgetPassword.html')
    
    def post(self, request):
        getValue = self.request.POST
        try:
            user = User.objects.get(username = getValue['username'], graduateLevel = int(getValue['graduateLevel']) + 1911, email = getValue['email'])
        except User.DoesNotExist:
            user = None

        if user:
            newpassword = get_random_string(length=8)
            #send_mail('資科系務系統新密碼', '你的新密碼是' + newpassword, 'ling900101@gmail.com', [user.email,], fail_silently=False)
            user.password = make_password(newpassword)
            user.save()
            messages.success(request, "重設成功，請至信箱確認新密碼!")
        else:
            messages.success(request, "輸入的資料有誤")

        return redirect(reverse('login'))

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
            return reverse('Home')
        else:
            return render(request, 'registration/Login.html', locals())

class LogoutView(View):

    def post(self, request):
        auth.logout(request)
        return redirect(reverse('Home'))

class UserProject(View):
    
    def get(self, request, pk):
        project = Project.objects.filter(user = request.user.id)
        context = {
            'project': project,
        }

        return render(request, 'UserProject.html', context)

class UserLicense(View):
    
    def get(self, request, pk):
        license = License.objects.filter(user = request.user.id)
        context = {
            'license': license,
        }

        return render(request, 'UserLicense.html', context)

class PassProject(LoginRequiredMixin, CreateView):

    def get(self, request, pk):
        form = ProjectModelForm(initial={'user': request.user.id, 'type': 0})
        context = {
            'form': form,
        }
        return render(request, 'PassProject.html', context)
    
    def post(self, request, pk):
        form = ProjectModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            data = Project.objects.get(user=self.kwargs['pk'])
            user = User.objects.get(id=self.kwargs['pk'])
            barCode = str(user.graduateLevel-1911)+'-'+ user.username +'-'+'A'
            paper = Paper.objects.create(project = data, barCode = barCode)
            paper.save()
            barCode = str(user.graduateLevel-1911)+'-'+ user.username +'-'+'B'
            paper = Paper.objects.create(project = data, barCode=barCode)
            paper.save()
            messages.success(request, "繳交成功")
            return redirect(reverse('PassProject', kwargs={'pk': self.request.user.id}))

        context = {
            'form': form,
        }
        messages.success(request, "請勿重複繳交")
        return render(request, 'PassProject.html', context)


class PassLicense(LoginRequiredMixin, View):

    def get(self, request, pk):
        user = User.objects.get(id = pk)
        form = LicenseModelForm(initial={'user': user.id, 'username': user.name})
        
        context = {
            'form': form,
        }

        return render(request, 'PassLicense.html', context)
    
    def post(self, request, pk):
        form = LicenseModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "繳交成功")
            return redirect(reverse('PassLicense', kwargs={'pk': pk}))

        context = {
            'form': form,
        }

        return render(request, 'PassLicense.html', context)

class PassProposal(LoginRequiredMixin, View):

    def get(self, request, pk):
        user = User.objects.get(id = pk)
        form = ProposalModelForm(initial={'user': user.id})
        context = {
            'form': form,
        }

        return render(request, 'PassProposal.html', context)
    
    def post(self, request, pk):
        form = ProposalModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "繳交成功!!")
            return redirect(reverse('PassProposal', kwargs={'pk':pk}))
        
        context = {
            'form': form,
        }

        return render(request, 'PassProposal.html', context)      

class PassFinal(LoginRequiredMixin, View):

    def get(self, request, pk):
        try:
            proposal = Proposal.objects.get(user = pk)
        except Proposal.DoesNotExist:
            proposal = None
        if proposal:
            form = FinalModelForm(initial={'user':pk, 'proposal': proposal.id, 'professor':proposal.professor, 'name':proposal.name}) 
        else:
            form = FinalModelForm()
            messages.success(request, "你還沒繳交論文計畫!!")
        context = {
            'form':form
        }
        return render(request, 'PassFinal.html', context)
    
    def post(self, request, pk):
        form = FinalModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            proposal = Proposal.objects.get(user = pk)
            project = Project.objects.get(proposal = proposal.id)
            delta = project.postDate - proposal.postDate
            if delta > timedelta(days=92):
                form.save()
                data = Project.objects.get(user=self.kwargs['pk'])
                user = User.objects.get(id=self.kwargs['pk'])
                barCode = str(user.graduateLevel-1911)+'-'+ user.username +'-'+'A'
                paper = Paper.objects.create(project = data, barCode = barCode)
                paper.save()
                barCode = str(user.graduateLevel-1911)+'-'+ user.username +'-'+'B'
                paper = Paper.objects.create(project = data, barCode=barCode)
                paper.save()

                messages.success(request, "繳交成功!!")
                return redirect(reverse('PassFinal', kwargs={'pk':pk}))
            else:
                project.delete()
                messages.success(request, "學位考試與計畫發表日期應相差3個月以上!!")
        context = {
            'form':form
        }
        return render(request, 'PassFinal.html', context)

class BorrowPaper(ListView):

    def get(self, request, pk):
        queryDict = {}
        getValue = self.request.GET
        if getValue:
            if 'author' in getValue:
                queryDict['project__user__name__icontains'] = getValue['author']
            if 'name' in getValue:
                queryDict['project__name__icontains'] = getValue['name']
            if 'type' in getValue and int(getValue['type']) >= 0:
                queryDict['project__type'] = int(getValue['type'])
            if 'professor' in getValue:
                queryDict['project__professor__icontains'] = getValue['professor']
            paper = Paper.objects.filter(**queryDict)
        else:
            paper = Paper.objects.all()

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
    
    def MakeBooking(request, pk):
        paper = Paper.objects.get(id = pk)
        
        try:
            findBookingExist = Booking.objects.exclude(state = 2).get(paper = paper.id)
        except Booking.DoesNotExist:
            findBookingExist = None
        
        if findBookingExist and findBookingExist.state != 2:
            messages.success(request, "有人借走 " +  paper.name + " 囉!!")
        else:
            booking = Booking.objects.create(user=request.user, paper = paper, bookingTime = datetime.datetime.now(), bookingDate = datetime.date.today())
            messages.success(request, "借閱成功!!!")
            #send_mail('新的報告書預約', request.user.name + "在" + booking.bookingTime + "預約了 " + booking.paper.name, 'ling900101@gmail.com', ['csshare'], fail_silently=False)
            booking.save()

        return redirect(reverse('BorrowPaper', kwargs={'pk': request.user.id})  ) 
    
    
class GetEntityPaper(View):
    
    def get(self, request):
        
        booking = Booking.objects.filter(user=request.user.id, state=1)
        context = {
            'booking':booking
        }
        return render(request, 'GetEntityPaper.html', context)
    
    def post(self, request):

        try:
            paper = Paper.objects.get(barCode = request.POST['barCode'])
            changeBookingState=Booking.objects.get(paper = paper.id, state = 0)
        except Booking.DoesNotExist:
            changeBookingState=None
        if changeBookingState and changeBookingState.state == 0:
            changeBookingState.state = 1
            changeBookingState.lendTimes = changeBookingState.paper.lendTimes + 1
            changeBookingState.takingTime = datetime.datetime.now()
            changeBookingState.takingDate = datetime.date.today()
            changeBookingState.save()
            messages.success(request, "領取成功!")
        else:
            messages.success(request, "借閱預約不存在...")


        booking = Booking.objects.filter(user=request.user.id, state=1)
        context = {
            'booking':booking
        }
        return render(request, 'GetEntityPaper.html', context)
class ReturnEntityPaper(View):
    def get(self, request):
        return render(request, 'ReturnEntityPaper.html')
    def post(self, request):
        getValue = self.request.POST
        try:
            booking = Booking.objects.get(paper__barCode = getValue['barCode'], state = 1)
        except Booking.DoesNotExist:
            booking = None

        if booking:
            booking.state = 2
            booking.underTaker = User.objects.get(username = getValue['underTaker']).name
            booking.save()
            messages.success(request, "歸還成功!")
        else:
            messages.success(request, "此報告書並未被借閱...")

        return render(request, "ReturnEntityPaper.html")


class UserBooking(ListView):

    def get(self, request, pk):
        booking = Booking.objects.filter(user = request.user.id)
        
        paginator=Paginator(booking, limit)

        page=request.GET.get('page')
        
        try:
            booking=paginator.page(page)
        except PageNotAnInteger:
            booking=paginator.page(1)
        except EmptyPage:
            booking=paginator.page(paginator.num_pages)
        context = {
            'booking': booking,
        }

        return render(request, 'UserBooking.html', context)
    
    def deleteBooking(request, pk):
        booking = Booking.objects.get(id = pk)
        #send_mail('報告書預約取消', booking.paper.name + "的預約已取消!!", 'ling900101@gmail.com', [request.user.email,], fail_silently=False)
        booking.delete()
        messages.success(request, "預約已取消!")

        return HttpResponseRedirect(reverse('UserBooking', kwargs={'pk': request.user.id})  ) 


class DisplayLicense(LoginRequiredMixin, View):

    def get(self, request):
        license = License.objects.all()

        paginator=Paginator(license, limit)

        page=request.GET.get('page')
        
        try:
            license=paginator.page(page)
        except PageNotAnInteger:
            license=paginator.page(1)
        except EmptyPage:
            license=paginator.page(paginator.num_pages)
        context = {
            'license': license,
        }

        return render(request, "DisplayLicense.html", context)

    def post(self, request):
        queryDict = {}
        license = License.objects.all()
        getValue = self.request.POST
        if getValue:
            '''if 'q' in getValue:
                queryDict['user_id__icontains'] = getValue['q']'''
            if 'level' in getValue:
                level = getValue['level']
                if level:
                    queryDict['level'] = getValue['level']
            if 'pazz' in getValue:
                pazz = getValue['pazz']
                if pazz:
                    queryDict['pazz'] = getValue['pazz']

        if "export" in request.POST:
            license = License.objects.filter(**queryDict).values_list('user__name','user__username' , 'name','level', 'acqDate')
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("證照紀錄.csv"))         
            writer = csv.writer(response)       
                
        
            writer.writerow(['姓名','學號','證照名稱','級別','取得日期',])
        
            for license in license:
                writer.writerow(license)
            return response
        else:
            license = License.objects.filter(**queryDict)
            
            paginator=Paginator(license, limit)

            page=request.GET.get('page')
        
            try:
                license=paginator.page(page)
            except PageNotAnInteger:
                license=paginator.page(1)
            except EmptyPage:
                license=paginator.page(paginator.num_pages)
            context = {
                'license': license,
            }

        return render(request, 'DisplayLicense.html', context)
    

class DisplayProject(LoginRequiredMixin, ListView):
        
    def get(self, request):
        
        project = Project.objects.all()

        paginator=Paginator(project, limit)

        page=request.GET.get('page')
        
        try:
            project=paginator.page(page)
        except PageNotAnInteger:
            project=paginator.page(1)
        except EmptyPage:
            project=paginator.page(paginator.num_pages)

        year = timezone.now().year - 1906
        context = {
            'project': project,
            'range': range(90, year)
        }

        return render(request, 'DisplayProject.html', context)

    def post(self, request):
        queryDict = {}
        getValue = self.request.POST
        if getValue:
            if 'username' in getValue:
                queryDict['user__name__icontains'] = getValue['username']
            if 'graduateLevel' in getValue:    
                queryDict['user__graduateLevel'] = int(getValue['graduateLevel'])
            if 'professor' in getValue:
                queryDict['professor__icontains'] = getValue['professor']
        
        if "export" in request.POST:
            project = Project.objects.filter(**queryDict).values_list('user__name','user__username', 'professor','name',)
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("專題紀錄.csv"))         
            writer = csv.writer(response)       
                
        
            writer.writerow(['姓名','學號','指導教授','專題名稱',])
        
            for project in project:
                writer.writerow(project)
            return response
        else:
            project = Project.objects.filter(**queryDict)
            
            paginator=Paginator(project, limit)

            page=request.GET.get('page')
        
            try:
                project=paginator.page(page)
            except PageNotAnInteger:
                project=paginator.page(1)
            except EmptyPage:
                project=paginator.page(paginator.num_pages)
            
            context = {
                'project': project,
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

                    messages.success(request, "新增成功!")
                    return render(request, 'ImportAndExport.html', {
                        'uploaded_file_url': uploaded_file_url
                    })
            except Exception as identifier:            
                print(identifier)

        elif "single" in request.POST:
            getValue = self.request.POST
            try:
                user = User.objects.get(username = getValue['username'])
            except User.DoesNotExist:
                user = None

            if user:
                messages.success(request, "已存在的使用者!!")
            else:
                if re.match(pattern, getValue['username']):
                    user = User.objects.create(username=getValue['username'], password = make_password(getValue['password']), name=getValue['name'], graduateLevel=int(getValue['graduateLevel'])+1911, email = getValue['email'])
                    user.save()
                    messages.success(request, "新增成功!")
                else:
                    messages.success(request, "無效的學號!!")
                
        return render(request, 'ImportAndExport.html')

class SearchStudent(LoginRequiredMixin, ListView):
    
    model = User

    template_name = "SearchStudent.html"

    def get_queryset(self):
        queryDict = {}
        if self.request.GET:
            if "name" in self.request.GET:
                queryDict['name__icontains'] = self.request.GET['name']
            if "username" in self.request.GET:
                queryDict['username__icontains'] = self.request.GET['username']
            if 'graduateLevel' in self.request.GET and self.request.GET['graduateLevel'] != '':
                queryDict['graduateLevel'] = int(self.request.GET['graduateLevel']) + 1911
            queryset = User.objects.filter(**queryDict)
        else:
            queryset = User.objects.all()

        paginator=Paginator(queryset, limit)

        page=self.request.GET.get('page')
        
        try:
            queryset=paginator.page(page)
        except PageNotAnInteger:
            queryset=paginator.page(1)
        except EmptyPage:
            queryset=paginator.page(paginator.num_pages)
        

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
    
    def deleteStudent(request, pk):
        user = User.objects.get(id=pk)
        user.delete()
        return redirect(reverse('SearchStudent'))
    
class BookingList(LoginRequiredMixin, ListView):
    
    model = Booking

    template_name = "BookingList.html"

    def get_queryset(self):
        queryDict = {}
        if self.request.GET:
            if "name" in self.request.GET:
                queryDict['user__name__icontains'] = self.request.GET['name']
            if "username" in self.request.GET:
                queryDict['user__username__icontains'] = self.request.GET['username']
            if 'state' in self.request.GET and self.request.GET['state'] != '':
                queryDict['state'] = self.request.GET['state']
            
            queryset = Booking.objects.filter(**queryDict)
        else:
            queryset = Booking.objects.all()

        paginator=Paginator(queryset, limit)

        page=self.request.GET.get('page')
        
        try:
            queryset=paginator.page(page)
        except PageNotAnInteger:
            queryset=paginator.page(1)
        except EmptyPage:
            queryset=paginator.page(paginator.num_pages)
        

        return queryset
    
class HistoryBookingAnalysis(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'HistoryBookingAnalysis.html')
    
    def post(self, request):
        queryDict={}
        getValue = self.request.POST
        if getValue:
            if 'graduateYear' in getValue and getValue['graduateYear'] != '':
                queryDict['project__user__graduateLevel'] = int(getValue['graduateYear']) + 1911
            if 'type' in getValue and getValue['type'] != '':
                queryDict['project__type'] = int(getValue['type'])
            if 'name' in getValue:
                queryDict['project__name__icontains'] = getValue['name']
            if 'field' in getValue and getValue['field'] != '':
                queryDict['project__field'] = getValue['field']

            if 'bookingYear' in getValue and getValue['bookingYear'] != '':
                paper_id = Booking.objects.annotate(year = ExtractYear('bookingDate')).filter(year = int(getValue['bookingYear']) + 1911).values_list('paper__project__id', flat = True).distinct
                paper = Paper.objects.exclude(lendTimes = 0).filter(id__in = paper_id()).filter(**queryDict)
                for i in paper:
                    print(i.project.name)
            else:
                paper = Paper.objects.exclude(lendTimes = 0).filter(**queryDict)

        paginator=Paginator(paper, limit)

        page=self.request.GET.get('page')
        
        try:
            paper=paginator.page(page)
        except PageNotAnInteger:
            paper=paginator.page(1)
        except EmptyPage:
            paper=paginator.page(paginator.num_pages)

        context = {
            'paper': paper
        }
        return render(request, 'HistoryBookingAnalysis.html', context)

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
            return reverse('DisplayLicense')

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