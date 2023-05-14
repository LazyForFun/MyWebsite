from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, UpdateView, CreateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings 
from django.http import HttpResponse, HttpResponseRedirect, FileResponse

from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail
from django.core.files.storage import default_storage

from django.db.models.functions import ExtractYear

import os, csv, datetime, re, io, zipfile
import pandas as pd
import django.utils.timezone as timezone
from django.utils.http import urlquote
from django.utils.crypto import get_random_string
from django.utils import dateformat, formats
from datetime import timedelta

from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.widgets import markers
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from itertools import chain


from .forms import ProjectModelForm, LicenseModelForm, ProposalModelForm, LicenseEditForm, LicenseAuditForm, FinalModelForm, ProposalEditForm, FinalEditForm
from .models import User, Project,License, Proposal, Booking, Paper, Year
from . import forms
#csshare.tw@gmail.com
#cs@go.utaipei.edu.tw

# Create your views here.

limit = 10 #分頁器單個頁面的資料數
pattern = r'^(U\d{8}|G\d{8}|M\d{8}|csshare[0-9]+)$' #可使用的帳號格式

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
            new_username = getValue['username'].upper()
            if re.match(pattern, new_username):
                new_department = -1
                new_identity = -1
                if new_username[0] == 'U':
                    new_identity = 0
                elif new_username[0] == 'G':
                    new_identity = 2
                elif new_username[0] == 'M':
                    new_identity = 3

                if new_username[4:7] == '160':
                    new_department = 0
                else:
                    new_department = 1
                user = User.objects.create(name = getValue['name'], username = new_username, password = make_password(getValue['password']), email = getValue['mail'], enrollYear = int(new_username[1:4]) + 1911, identity = new_identity, department = new_department)
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
            user = User.objects.get(username = getValue['username'], enrollYear = int(getValue['enrollYear']) + 1911, email = getValue['email'])
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
    
class UserProposalAndFinal(View):
    
    def get(self, request, pk):
        proposal = Proposal.objects.filter(user = request.user.id)
        final = Project.objects.filter(user = request.user.id)
        editable = Project.objects.filter(user = request.user.id, state = 1)
        context = {
            'proposal': proposal,
            'final': final,
            'editable': editable,
        }

        return render(request, 'UserProposalAndFinal.html', context)
    
class UploadCancel(View):
    def get(self, request, pk):
        return render(request, 'UploadCancel.html')
    def post(self, request, pk):
        if pk == 'proposal':
            proposal = Proposal.objects.get(user = request.user.id, state = 0)
            proposal.state = 1
            proposal.cancelapplication = self.request.POST['cancelApplication']
            proposal.save()
        
        elif pk == 'final':
            project = Project.objects.get(user = request.user.id, state = 1)
            project.state = 2
            project.cancelapplication = self.request.POST['cancelApplication']
            paper = Paper.objects.get(project = project)
            paper.delete()
            project.save()

        return redirect(reverse('UserProposalAndFinal', kwargs={'pk': self.request.user.id}))

class PassProject(LoginRequiredMixin, CreateView):

    def get(self, request, pk):
        try:
            data = Project.objects.get(user=self.kwargs['pk'], state = 0)
        except Project.DoesNotExist:
            data = None
        if data:
            messages.success(request, "請勿重複繳交")
            return render(request, 'Home.html')
        else:
            form = ProjectModelForm(initial={'user': pk})
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
            barCode = str(user.enrollYear-1908)+'-'+ user.username
            paper = Paper.objects.create(project = data, barCode = barCode)
            paper.save()
            messages.success(request, "繳交成功")
            return redirect(reverse('UserProject', kwargs={'pk': self.request.user.id}))

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

        try:
            proposal = Proposal.objects.get(user = pk, state = 0)
        except Proposal.DoesNotExist:
            proposal = None
        if proposal:
            messages.success(request, "請勿重複繳交!!")
            return redirect(reverse('UserProposalAndFinal', kwargs={'pk':pk}))
        
        form = ProposalModelForm(initial={'user': self.request.user.id})
        context = {
            'form': form,
        }

        return render(request, 'PassProposal.html', context)
    
    def post(self, request, pk):
        
        form = ProposalModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "繳交成功!!")
            return redirect(reverse('UserProposalAndFinal', kwargs={'pk':pk}))
        
        context = {
            'form': form,
        }

        return render(request, 'PassProposal.html', context)      

class PassFinal(LoginRequiredMixin, View):

    def get(self, request, pk):
        try:
            data = Project.objects.get(user = pk, state = 1)
        except Project.DoesNotExist:
            data = None
        if data:
            messages.success(request, "請勿重複繳交!!")
            return redirect(reverse('UserProposalAndFinal', kwargs={'pk':pk}))
        try:
            proposal = Proposal.objects.get(user = pk, state = 0)
        except Proposal.DoesNotExist:
            proposal = None
        if proposal:
            form = FinalModelForm(initial={'user':pk, 'proposal': proposal.id, 'professor':proposal.professor, 'name':proposal.name, 'state':1}) 
        else:
            form = FinalModelForm()
            messages.success(request, "你還沒繳交論文計畫!!")
            return redirect(reverse('PassProposal', kwargs={'pk':pk}))
        context = {
            'form':form
        }
        return render(request, 'PassFinal.html', context)
    
    def post(self, request, pk):
        form = FinalModelForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            proposal = Proposal.objects.get(user = pk, state = 0)
            project = Project.objects.get(proposal = proposal.id, state = 1)
            delta = project.postDate - proposal.postDate
            if delta > timedelta(days=92):
                form.save()
                data = Project.objects.get(user=self.kwargs['pk'], state = 1)
                user = User.objects.get(id=self.kwargs['pk'])
                barCode = str(user.enrollYear-1910)+'-'+ user.username
                paper = Paper.objects.create(project = data, barCode = barCode)
                paper.save()

                messages.success(request, "繳交成功!!")
                return redirect(reverse('UserProposalAndFinal', kwargs={'pk':pk}))
            else:
                project.delete()
                messages.success(request, "學位考試與計畫發表日期須相差3個月以上!!")
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
                queryDict['project__user__identity'] = int(getValue['type'])
            if 'professor' in getValue:
                queryDict['project__professor__icontains'] = getValue['professor']
            if 'field' in getValue and int(getValue['field']) >= 0:
                queryDict['project__field'] = int(getValue['field'])
            
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
        
        if findBookingExist:
            messages.success(request, "有人借走 " +  paper.project.name + " 囉!!")
        else:
            try:
                year = Year.objects.get(year = (int(timezone.now().year) - 1911))
            except Year.DoesNotExist:
                year = None
            
            if not year:
                year = Year.objects.create(year = (int(timezone.now().year) - 1911))
                year.save()
            booking = Booking.objects.create(user=request.user, paper = paper, bookingDate = timezone.now(), year = year)
            messages.success(request, "預約成功，請至資訊科學系辦公室借用!!!")
            #send_mail('新的報告書預約', request.user.name + "在" + booking.bookingTime + "預約了 " + booking.paper.name, 'ling900101@gmail.com', ['csshare'], fail_silently=False)
            booking.save()
            

        return redirect(reverse('BorrowPaper', kwargs={'pk': request.user.id})  ) 
    
    
class GetEntityPaper(View):
    
    def get(self, request):
        
        booking = Booking.objects.filter(state=1)
        context = {
            'booking':booking
        }
        return render(request, 'GetEntityPaper.html', context)
    
    def post(self, request):

        try:
            paper = Paper.objects.get(barCode = request.POST['barCode'])
        except Paper.DoesNotExist:
            messages.success(request, "無效的條碼...")
            return render(request, 'GetEntityPaper.html')
        try:
            changeBookingState=Booking.objects.get(paper = paper.id, state = 0)
        except Booking.DoesNotExist:
            changeBookingState=None
        if changeBookingState and changeBookingState.state == 0:
            changeBookingState.state = 1
            changeBookingState.takingDate = timezone.now()
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
            booking.underTaker = getValue['underTaker']
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
            if 'name' in getValue:
                queryDict['user__name__icontains'] = getValue['name']
            if 'username' in getValue:
                queryDict['user__username__icontains'] = getValue['username']
            if 'enrollYear' in getValue and getValue['enrollYear'] != '':
                queryDict['user__enrollYear'] = int(getValue['enrollYear']) + 1911
            if 'level' in getValue and getValue['level'] != '':
                queryDict['level'] = getValue['level']
            if 'pazz' in getValue and getValue['pazz'] != '':
                queryDict['pazz'] = getValue['pazz']
        else:
            license = License.objects.all()

        if "export" in getValue:
            license = License.objects.filter(**queryDict).values_list('user__name','user__username' , 'name','level', 'acqDate')
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("證照紀錄.csv"))         
            writer = csv.writer(response)       
                
        
            writer.writerow(['姓名','學號','證照名稱','級別','取得日期',])
        
            for license in license:
                writer.writerow(license)
            return response
        elif 'search' in getValue:
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

        elif 'download' in getValue:
            license = License.objects.filter(**queryDict)

            file_zip = io.BytesIO()
            user_count = {}

            with zipfile.ZipFile(file_zip, 'w') as zf:
                for i in license:
                    user_key = i.user.username + '-' + i.user.name
                    if user_key in user_count:
                        user_count[user_key] += 1
                    else:
                        user_count[user_key] = 1
                    image_data = default_storage.open(i.image.name, 'rb').read()
                    filename = user_key + '-' + str(user_count[user_key]) + '.jpg'
                    zf.writestr(filename, image_data)

            file_zip.seek(0)
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="證照証明截圖.zip"'
            response.write(file_zip.read())
            return response
    

class DisplayProject(LoginRequiredMixin, ListView):
        
    def get(self, request):
        
        project = Project.objects.filter(state = 0)

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

    def post(self, request):
        queryDict = {}
        getValue = self.request.POST
        if getValue:
            if 'username' in getValue:
                queryDict['user__name__icontains'] = getValue['username']
            if 'enrollYear' in getValue and getValue['enrollYear'] != '':
                queryDict['user__enrollYear'] = int(getValue['enrollYear']) + 1911
            if 'professor' in getValue:
                queryDict['professor__icontains'] = getValue['professor']
            if 'field' in getValue and getValue['field'] != '':
                queryDict['field'] = getValue['field']
        
        if "export" in getValue:
            project = Project.objects.filter(**queryDict, user__identity = 0).values_list('user__name','user__username', 'professor', 'name', 'field')
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("專題紀錄.csv"))         
            writer = csv.writer(response)       
                
        
            writer.writerow(['姓名','學號','指導教授','報告書題目', '領域'])
        
            for project in project:
                writer.writerow(project)
            return response
        elif 'search' in getValue:
            project = Project.objects.filter(**queryDict, state = 0)
            
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
        
        elif 'download' in getValue:
            project = Project.objects.filter(**queryDict)
            
            file_zip = io.BytesIO()

            with zipfile.ZipFile(file_zip, 'w') as zf:
                for i in project:
                    try:
                        poster_data = default_storage.open(i.poster.name, 'rb').read()
                    except PermissionError:
                        continue
                    zf.writestr(i.user.username + '.jpg', poster_data)

            file_zip.seek(0)
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="專題海報.zip"'
            response.write(file_zip.read())
            return response

class DisplayProposal(LoginRequiredMixin, ListView):
        
    def get(self, request):
        
        proposal = Proposal.objects.all()

        paginator=Paginator(proposal, limit)

        page=request.GET.get('page')
        
        try:
            proposal=paginator.page(page)
        except PageNotAnInteger:
            proposal=paginator.page(1)
        except EmptyPage:
            proposal=paginator.page(paginator.num_pages)

        context = {
            'proposal': proposal,
        }

        return render(request, 'DisplayProposal.html', context)

    def post(self, request):
        queryDict = {}
        getValue = self.request.POST
        if getValue:
            if 'username' in getValue:
                queryDict['user__name__icontains'] = getValue['username']
            if 'enrollYear' in getValue and getValue['enrollYear'] != '':
                queryDict['user__enrollYear'] = int(getValue['enrollYear']) + 1911
            if 'professor' in getValue:
                queryDict['professor__icontains'] = getValue['professor']
            if 'type' in getValue and getValue['type'] != '':
                queryDict['user__identity'] = getValue['type']
            if 'field' in getValue and getValue['field'] != '':
                queryDict['field'] = getValue['field']
        
        if "export" in getValue:
            proposal = Proposal.objects.filter(**queryDict).values_list('user__name','user__username', 'professor', 'name')
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("計畫發表紀錄.csv"))         
            writer = csv.writer(response)       
                
        
            writer.writerow(['姓名','學號','指導教授','計畫發表題目', '學制'])
        
            for proposal in proposal:
                writer.writerow(proposal)
            return response
        elif 'search' in getValue:
            proposal = Proposal.objects.filter(**queryDict)
            
            paginator=Paginator(proposal, limit)

            page=request.GET.get('page')
        
            try:
                proposal=paginator.page(page)
            except PageNotAnInteger:
                proposal=paginator.page(1)
            except EmptyPage:
                proposal=paginator.page(paginator.num_pages)
            
            context = {
                'proposal': proposal,
            }
            
            return render(request, 'DisplayProposal.html', context)
        
        elif 'download' in getValue:
            proposal = Proposal.objects.filter(**queryDict, state = 1)
            
            file_zip = io.BytesIO()
            user_count = {}

            with zipfile.ZipFile(file_zip, 'w') as zf:
                for i in proposal:
                    user_key = i.user.username + '-' + i.user.name
                    if user_key in user_count:
                        user_count[user_key] += 1
                    else:
                        user_count[user_key] = 1
                    try:
                        image_data = default_storage.open(i.cancelapplication.name, 'rb').read()
                    except PermissionError:
                        continue
                    filename = user_key + '-' + str(user_count[user_key]) + '.jpg'
                    zf.writestr(filename, image_data)

            file_zip.seek(0)
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="計畫發表取消表.zip"'
            response.write(file_zip.read())
            return response
        
class DisplayFinal(LoginRequiredMixin, ListView):
        
    def get(self, request):
        
        project = Project.objects.exclude(state = 0)

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

        return render(request, 'DisplayFinal.html', context)

    def post(self, request):
        queryDict = {}
        getValue = self.request.POST
        if getValue:
            if 'username' in getValue:
                queryDict['user__name__icontains'] = getValue['username']
            if 'enrollYear' in getValue and getValue['enrollYear'] != '':
                queryDict['user__enrollYear'] = int(getValue['enrollYear']) + 1911
            if 'professor' in getValue:
                queryDict['professor__icontains'] = getValue['professor']
            if 'type' in getValue and getValue['type'] != '':
                queryDict['user__identity'] = getValue['type']
            if 'field' in getValue and getValue['field'] != '':
                queryDict['field'] = getValue['field']
        
        if "export" in getValue:
            project = Project.objects.filter(**queryDict).exclude(state = 0).values_list('user__name','user__username', 'professor', 'name')
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("學位考試紀錄.csv"))         
            writer = csv.writer(response)       
                
        
            writer.writerow(['姓名','學號','指導教授','計畫發表題目', '學制'])
        
            for project in project:
                writer.writerow(project)
            return response
        elif 'search' in getValue:
            project = Project.objects.filter(**queryDict).exclude(state = 0)
            
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
            
            return render(request, 'DisplayFinal.html', context)
        
        elif 'download' in getValue:
            project = Project.objects.filter(**queryDict, state = 2)
            
            file_zip = io.BytesIO()
            user_count = {}

            with zipfile.ZipFile(file_zip, 'w') as zf:
                for i in project:
                    user_key = i.user.username + '-' + i.user.name
                    if user_key in user_count:
                        user_count[user_key] += 1
                    else:
                        user_count[user_key] = 1
                    image_data = default_storage.open(i.cancelapplication.name, 'rb').read()
                    filename = user_key + '-' + str(user_count[user_key]) + '.jpg'
                    zf.writestr(filename, image_data)

            file_zip.seek(0)
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="學位考試取消表.zip"'
            response.write(file_zip.read())
            return response
        
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
                new_enrollYear = int(getValue['username'][1:4])
                if re.match(pattern, getValue['username']):
                    user = User.objects.create(username=getValue['username'], password = make_password(getValue['password']), name=getValue['name'], enrollYear=new_enrollYear+1911, email = getValue['email'])
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
            if 'enrollYear' in self.request.GET and self.request.GET['enrollYear'] != '':
                queryDict['enrollYear'] = int(self.request.GET['enrollYear']) + 1911
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
            if getValue['enrollYear'] != '':
                student.enrollYear = int(getValue['enrollYear']) + 1911
            student.identity = getValue['identity']
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
        queryDict = {}
        drawDict = {}
        getValue = self.request.POST
        if getValue:
            if 'bookingYear' in getValue and getValue['bookingYear'] != '':
                queryDict['year__year'] = int(getValue['bookingYear'])
            if 'graduateYear' in getValue and getValue['graduateYear'] != '':
                queryDict['paper__project__user__enrollYear'] = int(getValue['enrollYear']) + 1911
            if 'type' in getValue and getValue['type'] != '':
                queryDict['paper__project__user__identity'] = int(getValue['type'])
                drawDict['paper__project__user__identity'] = int(getValue['type'])
            if 'name' in getValue:
                queryDict['paper__project__name__icontains'] = getValue['name']
            if 'field' in getValue and getValue['field'] != '':
                queryDict['paper__project__field'] = int(getValue['field'])
                drawDict['paper__project__field'] = int(getValue['field'])

        booking = Booking.objects.filter(**queryDict).values_list('paper__project__name').distinct
        paper = Paper.objects.filter(project__name__in = booking())
        for i in paper:
            i.lendTimes = Booking.objects.filter(paper = i, **queryDict).count()
            i.save()

        '''分隔篩選資料與畫圖'''

        if 'draw' in getValue:
            drawingTitleLine1 = Drawing(200, 100)
            drawingTitleLine2 = Drawing(200, 100)
            
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer)
            pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))

            titleType = ''
            if getValue['type'] == '0':
                titleType = '大學部'
            elif getValue['type'] == '1':
                titleType = '日間碩士班'
            elif getValue['type'] == '2':
                titleType = '碩士在職專班'
            titleField = ''
            if getValue['field'] == '0':
                titleField = '軟體開發及程式設計'
            elif getValue['field'] == '1':
                titleField = '網路及多媒體應用'
            elif getValue['field'] == '2':
                titleField = '系統及演算法開發'
            titleLine1 = String(50, 50, str(getValue['bookingYear']) + "學年度" + titleType, fontName="SimSun", fontSize=25)
            titleLine2 = String(50, 50, titleField + "借閱分析", fontName="SimSun", fontSize=25)
            drawingTitleLine1.add(titleLine1)
            drawingTitleLine2.add(titleLine2)
            renderPDF.draw(drawingTitleLine1, pdf, 0, 700)
            renderPDF.draw(drawingTitleLine2, pdf, 0, 670)
            #設定標題

            drawingPieChart1 = Drawing(400, 200)
            drawingPieChart2 = Drawing(400, 200)

            pc1 = Pie()
            pc2 = Pie()
            pc1.sideLabels = True
            pc2.sideLabels = True
            pc1.x = pc2.x = 65
            pc1.y = pc2.y = 15
            pc1.width = pc2.width = 150
            pc1.height = pc2.height = 150
            pc1.slices.fontSize = pc2.slices.fontSize = 16
            pc1.slices.fontName = pc2.slices.fontName = 'SimSun'
            #圓餅圖設定
            if getValue['bookingYear'] == '':
                BookingForSingalYear = []
                BookingForAccumulate = []
                category1 = []
                category2 = []
                years = Year.objects.all()
                acc = 0
                for year in years:
                    count = Booking.objects.filter(year = year, **drawDict).count()
                    BookingForSingalYear.append(count)
                    acc += count
                    BookingForAccumulate.append(acc)
                    category1.append(str(year.year) + '(' + str(count) + '次)')
                    category2.append(str(year.year) + '(' + str(acc) + '次)')

                pc1.data = BookingForSingalYear
                pc2.data = BookingForAccumulate
                pc1.labels = category1
                pc2.labels = category2
                pc1.slices.fontSize = pc2.slices.fontSize = 18
                pc1.slices.fontName = pc2.slices.fontName = 'SimSun'

                drawingPieChart1.add(pc1)
                drawingPieChart2.add(pc2)
                renderPDF.draw(drawingPieChart1, pdf, 150, 500)
                renderPDF.draw(drawingPieChart2, pdf, 150, 200)

                drawingChartName1 = Drawing(400, 200)
                drawingChartName2 = Drawing(400, 200)

                chartName1 = String(50, 50, '各年份借閱次數', fontName="SimSun", fontSize=30)
                chartName2 = String(50, 50, '歷年累計借閱次數', fontName="SimSun", fontSize=30)
                drawingChartName1.add(chartName1)
                drawingChartName2.add(chartName2)
                renderPDF.draw(drawingChartName1, pdf, 125, 400)
                renderPDF.draw(drawingChartName2, pdf, 125, 100)
                
            else:
                if getValue['type'] == getValue['field'] == '':
                    classByType = []
                    classByField = []
                    for type in range(3):
                        count = Booking.objects.filter(year__year = getValue['bookingYear'], paper__project__user__identity = type).count()
                        classByType.append(count)
                    for field in range(3):
                        count = Booking.objects.filter(year__year = getValue['bookingYear'], paper__project__field = field).count()
                        classByField.append(count)
                    category1 = ['大學部(' + str(classByType[0]) + '次)', '日間碩士班(' + str(classByType[1]) + '次)', '在職碩士專班(' + str(classByType[2]) + '次)']
                    category2 = ['軟體開發及程式設計(' + str(classByField[0]) + '次)', '網路及多媒體應用(' + str(classByField[1]) + '次)', '系統及演算法開發(' + str(classByField[2]) + '次)']

                    pc1.data = classByType
                    pc2.data = classByField
                    pc1.labels = category1
                    pc2.labels = category2

                    drawingPieChart1.add(pc1)
                    drawingPieChart2.add(pc2)
                    renderPDF.draw(drawingPieChart1, pdf, 150, 500)
                    renderPDF.draw(drawingPieChart2, pdf, 150, 200)

                    drawingChartName1 = Drawing(400, 200)
                    drawingChartName2 = Drawing(400, 200)

                    chartName1 = String(50, 50, '以學制分類借閱次數', fontName="SimSun", fontSize=30)
                    chartName2 = String(50, 50, '以領域分類借閱次數', fontName="SimSun", fontSize=30)
                    drawingChartName1.add(chartName1)
                    drawingChartName2.add(chartName2)
                    renderPDF.draw(drawingChartName1, pdf, 125, 400)
                    renderPDF.draw(drawingChartName2, pdf, 125, 100)
                
                elif getValue['type'] != '' and getValue['field'] == '':
                    classByField = []
                    for field in range(3):
                        count = Booking.objects.filter(year__year = getValue['bookingYear'], paper__project__field = field).count()
                        classByField.append(count)
                    category2 = ['軟體開發及程式設計(' + str(classByField[0]) + '次)', '網路及多媒體應用(' + str(classByField[1]) + '次)', '系統及演算法開發(' + str(classByField[2]) + '次)']

                    pc2.data = classByField
                    pc2.labels = category2

                    drawingPieChart2.add(pc2)
                    renderPDF.draw(drawingPieChart2, pdf, 150, 500)

                    drawingChartName2 = Drawing(400, 200)

                    chartName2 = String(50, 50, '以領域分類借閱次數', fontName="SimSun", fontSize=30)
                    drawingChartName2.add(chartName2)
                    renderPDF.draw(drawingChartName2, pdf, 100, 400)

                elif getValue['type'] == '' and getValue['field'] != '':
                    classByType = []
                    for type in range(3):
                        count = Booking.objects.filter(year__year = getValue['bookingYear'], paper__project__user__identity = type).count()
                        classByType.append(count)
                    category2 = ['大學部(' + str(classByType[0]) + '次)', '日間碩士班(' + str(classByType[1]) + '次)', '在職碩士專班(' + str(classByType[2]) + '次)']

                    pc2.data = classByType
                    pc2.labels = category2

                    drawingPieChart2.add(pc2)
                    renderPDF.draw(drawingPieChart2, pdf, 150, 500)

                    drawingChartName2 = Drawing(400, 200)

                    chartName2 = String(50, 50, '以學制分類借閱次數', fontName="SimSun", fontSize=30)
                    drawingChartName2.add(chartName2)
                    renderPDF.draw(drawingChartName2, pdf, 100, 400)
                    
            
            pdf.save()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename="分析圖.pdf")
        
        else:
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
        
class HistoryPaperUpdate(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'HistoryPaperUpdate.html')
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
                        try:
                            user = User.objects.get(username=dbframe.username)
                        except User.DoesNotExist:
                            if dbframe.username[0] == 'U':
                                id = 0
                            elif dbframe.username[0] == 'G':
                                id = 2
                            elif dbframe.username[0] == 'M':
                                id = 3
                            user = User.objects.create(username = dbframe.username, password = make_password(dbframe.username), name=dbframe.name, enrollYear = int(dbframe.enrollYear) + 1911, email = dbframe.username + "@go.utaipei.edu.tw", department = 0, identity = id)
                            user.save()

                        if user.identity != 0:
                            myState = 1
                        else:
                            myState = 0

                        try:
                            project = Project.objects.get(user = user)
                        except Project.DoesNotExist:
                            project = Project.objects.create(user = user, name = dbframe.paperName, professor = dbframe.professor, field = 0, state = myState)
                            project.save()

                        if user.identity == 0:
                            title = user.enrollYear - 1911 + 3
                        elif user.identity == 2 or user.identity == 3:
                            title = user.enrollYear - 1911 + 1
                        try:
                            paper = Paper.objects.get(project = project)
                        except Paper.DoesNotExist:
                            paper = Paper.objects.create(project = project, barCode = str(title) + '-' + user.username)
                            paper.save()

                    messages.success(request, "上傳成功!")
                    return render(request, 'HistoryPaperUpdate.html', {
                        'uploaded_file_url': uploaded_file_url
                    })
            except Exception as identifier:            
                print(identifier)

        elif "single" in request.POST:
            getValue = self.request.POST

            if getValue['enrollYear'] == '':
                return render(request, 'HistoryPaperUpdate.html')

            try:
                user = User.objects.get(username = getValue['username'])
            except User.DoesNotExist:
                if getValue['username'][0] == 'U':
                    id = 0
                elif getValue['username'][0] == 'G':
                    id = 2
                elif getValue['username'][0] == 'M':
                    id = 3
                user = User.objects.create(username = getValue['username'], password = make_password(getValue['username']), name=getValue['name'], enrollYear = int(getValue['enrollYear']) + 1911, email = getValue['username'] + "@go.utaipei.edu.tw", department = 0, identity = id)
                user.save()

            if user.identity != 0:
                myState = 1
            else:
                myState = 0
            try:
                project = Project.objects.get(user = user)
            except Project.DoesNotExist:    
                project = Project.objects.create(user = user, name = getValue['paperName'], professor = getValue['professor'], field = 0, state = myState)
                project.save()

            if user.identity == 0:
                title = user.enrollYear - 1911 + 3
            elif user.identity == 2 or user.identity == 3:
                title = user.enrollYear - 1911 + 1

            try:
                paper = Paper.objects.get(project = project)
            except Paper.DoesNotExist:
                paper = Paper.objects.create(project = project, barCode = str(title) + '-' + user.username)
                paper.save()

            messages.success(request, "上傳成功!")
                
        return render(request, 'HistoryPaperUpdate.html')


class AuditLicense(LoginRequiredMixin, UpdateView):
    model = License
    fileds = '__all__'
    
    form_class = LicenseAuditForm

    template_name = 'AuditLicense.html'

    def get_success_url(self):
        if 'pazz' in self.request.POST:
            self.object.pazz = 1
            self.object.save()
        elif 'fail' in self.request.POST:
            self.object.pazz = 2
            self.object.save()

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
    
class EditProposal(LoginRequiredMixin, UpdateView):
    model = Proposal
    fileds = '__all__'
    
    form_class = ProposalEditForm

    template_name = 'EditProposal.html'

    def get_success_url(self):
        return reverse('UserProposalAndFinal', kwargs={'pk':self.request.user.id})
    
class EditFinal(LoginRequiredMixin, UpdateView):
    model = Project
    fileds = '__all__'
    
    form_class = FinalEditForm

    template_name = 'EditFinal.html'

    def get_success_url(self):
        return reverse('UserProposalAndFinal', kwargs={'pk':self.request.user.id})
    
class DeleteLicense(LoginRequiredMixin, DeleteView):
    model = License
    fileds = '__all__'

    template_name = 'DeleteLicense.html'

    def get_success_url(self):
        return reverse('UserLicense', kwargs={'pk':self.request.user.id})