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
from .models import User, Project,License, Proposal, Booking, Paper, Year, StudentDoc
from . import forms
#csshare.tw@gmail.com
#cs@go.utaipei.edu.tw

# Create your views here.

limit = 10 #分頁器單個頁面的資料數
pattern_student = r'^(U\d{8}|G\d{8}|M\d{8}|u\d{8}|g\d{8}|m\d{8})$' #學生可使用的帳號格式
pattern_cs = r'^(csshare[0-9]+)$' #管理者可使用的帳號格式

class Home(View):

    def get(self, request):
        return render(request, 'Home.html')
    
# Sign in view
class Signin(View):
    def get(self, request):
        return render(request, 'registration/Signin.html')
    
    def post(self, request):
        getValue = self.request.POST

        # double check password
        if getValue['password'] != getValue['passwordCheck']:
            messages.success(request, "兩次密碼不一致!!!")
            return redirect(reverse('Signin'))

        # check the username has been used
        try:
            checkUser = User.objects.get(username = getValue['username'])
        except User.DoesNotExist:
            checkUser = None

        # if username is used
        if checkUser:
            messages.info(request, "使用者已存在!!")
            return redirect(reverse('Signin'))
        # if username is not used
        # create new user
        else:
            new_username = getValue['username']
            # create manager
            if re.match(pattern_cs, new_username):
                user = User.objects.create(name = getValue['name'], username = new_username, password = make_password(getValue['password']), email = 'csshare.tw@gmail.com', enrollYear = timezone.now().year, identity = 4, department = 0)
                messages.success(request, "註冊成功!!")
                return redirect(reverse('login'))
            # create student
            elif re.match(pattern_student, new_username):
                new_department = -1
                new_identity = -1
                new_username = new_username.upper()
                # bachelor
                if new_username[0] == 'U':
                    new_identity = 0
                # master
                elif new_username[0] == 'G':
                    new_identity = 2
                # EMA
                elif new_username[0] == 'M':
                    new_identity = 3

                # cs student
                if new_username[4:7] == '160':
                    new_department = 0
                # other student
                else:
                    new_department = 1
                user = User.objects.create(name = getValue['name'], username = new_username, password = make_password(getValue['password']), email = new_username + '@go.utaipei.edu.tw', enrollYear = int(new_username[1:4]) + 1911, identity = new_identity, department = new_department)
                user.save()
                messages.success(request, "註冊成功!!")
                return redirect(reverse('login'))
            else:
                messages.success(request, '請輸入有效的學號!!')
                return redirect(reverse('Signin'))
            
# edit password view
class EditPassword(LoginRequiredMixin, View):
    def get(self, request, pk):
        return render(request, 'registration/EditPassword.html')
    
    def post(self, request, pk):
        getValue = self.request.POST

        if 'editPassword' in getValue:
            # check original password
            if check_password(getValue['password'], request.user.password):
                # new password and original password cannot be the same
                if getValue['password'] != getValue['newpassword']:
                    # double check new password
                    if getValue['newpassword'] == getValue['newpassword_check']:
                        self.request.user.password = make_password(getValue['newpassword'])
                        self.request.user.save()
                        messages.success(request, "更改成功!! 請重新登入!!")
                    else:
                        messages.success(request, "密碼確認有誤...")

                else:
                    messages.success(request, "新舊密碼不能相同")
            else:
                messages.success(request, '舊密碼不正確...')

        # edit self information
        elif 'editInfo' in getValue:
            # get new information
            # get new information if the input is not None
            user = request.user
            if getValue['name'] != '':
                user.name = getValue['name']
            if getValue['username'] != '':
                user.username = getValue['username']
            if getValue['email'] != '':
                user.email = getValue['email']

            user.save()
            messages.success(request, "更改成功!! 請重新登入")
        
        auth.logout(request)
        return redirect(reverse('login'))
    
class ForgetPassword(View):
    def get(self, request):
        return render(request, 'registration/ForgetPassword.html')
    
    def post(self, request):
        getValue = self.request.POST
        # get user object with the input information
        try:
            user = User.objects.get(username = getValue['username'], enrollYear = int(getValue['enrollYear']) + 1911, email = getValue['email'])
        except User.DoesNotExist:
            user = None

        # if the user exist
        # random generate a new password with lentgh 8
        # send the new password to the email of user
        if user:
            newpassword = get_random_string(length=8)
            send_mail('資科系務系統新密碼', '你的新密碼是' + newpassword, 'csshare.go@gmail.com', [user.email,], fail_silently=False)
            user.password = make_password(newpassword)
            user.save()
            messages.success(request, "重設成功，請至學校信箱確認新密碼!")
        else:
            messages.success(request, "輸入的資料有誤")

        return redirect(reverse('login'))

class LoginView(View):

    def get(request):
        return render(request, 'registration/login.html')

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse('Home'))

        username = request.POST['username']
        password = request.POST['password']
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
        # get projects update by current user
        project = Project.objects.filter(user = request.user.id)
        context = {
            'project': project,
        }

        return render(request, 'UserProject.html', context)

class UserLicense(View):
    
    def get(self, request, pk):
        # get licenses update by current user
        license = License.objects.filter(user = request.user.id)
        context = {
            'license': license,
        }

        return render(request, 'UserLicense.html', context)
    
class UserProposalAndFinal(View):
    
    def get(self, request, pk):
        # get proposal and oral examination update by current user
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
        # delete proposal
        if pk == 'proposal':
            # get the proposal object
            proposal = Proposal.objects.get(user = request.user.id, state = 0)
            proposal.state = 1
            # save  the cancellation application form
            myfile = request.FILES['cancelApplication']
            proposal.cancelapplication = myfile
            proposal.save()
        # delete oral examination
        elif pk == 'final':
            # get the final object
            project = Project.objects.get(user = request.user.id, state = 1)
            project.state = 2
            # save  the cancellation application form
            myfile = request.FILES['cancelApplication']
            project.cancelapplication = myfile
            paper = Paper.objects.get(project = project)
            # delete the paper
            paper.delete()
            project.save()

            doc = StudentDoc.objects.get(user = request.user.id)
            doc.delete()

        return redirect(reverse('UserProposalAndFinal', kwargs={'pk': self.request.user.id}))

class PassProject(LoginRequiredMixin, CreateView):

    def get(self, request, pk):
        # get the project object
        # bachelor can update only 1 project 
        try:
            data = Project.objects.get(user=self.kwargs['pk'], state = 0)
        except Project.DoesNotExist:
            data = None
        print(data)
        # bachelor has updated a project
        if data:
            messages.success(request, "請勿重複繳交")
            return render(request, 'Home.html')
        # no project has been updated
        else:
            # initial a form for update project
            form = ProjectModelForm(initial={'user': pk})
            context = {
                'form': form,
            }
            return render(request, 'PassProject.html', context)
    
    def post(self, request, pk):
        # get the form
        form = ProjectModelForm(request.POST, request.FILES)
        # get updated file
        myFile =  request.FILES['report']
        # the updated file should be .pdf file
        if myFile.content_type != 'application/pdf':
            messages.success(request, "請上傳pdf檔!!!")
            return render(request, 'PassProject.html', context={'form': form})
        # all information in the form should be balid
        if form.is_valid():
            form.save()
            # create paper object according to the updated information
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
        # get the user object
        user = User.objects.get(id = pk)
        # create a new form for update license
        form = LicenseModelForm(initial={'user': user.id, 'username': user.name})
        
        context = {
            'form': form,
        }

        return render(request, 'PassLicense.html', context)
    
    def post(self, request, pk):
        # get the form
        form = LicenseModelForm(request.POST, request.FILES)
        # create the license object if the form is valid
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
        # get the proposal object
        # master can only update one proposal
        try:
            proposal = Proposal.objects.get(user = pk, state = 0)
        except Proposal.DoesNotExist:
            proposal = None
        # user has update a proposal
        if proposal:
            messages.success(request, "請勿重複繳交!!")
            return redirect(reverse('UserProposalAndFinal', kwargs={'pk':pk}))
        
        # create a new form for update proposal
        form = ProposalModelForm(initial={'user': self.request.user.id})
        context = {
            'form': form,
        }

        return render(request, 'PassProposal.html', context)
    
    def post(self, request, pk):
        # get the form
        form = ProposalModelForm(request.POST)
        # create proposal object if the form is valid
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
        # get the oral examination object
        try:
            data = Project.objects.get(user = pk, state = 1)
        except Project.DoesNotExist:
            data = None
        # master can only submit one paper
        if data:
            messages.success(request, "請勿重複繳交!!")
            return redirect(reverse('UserProposalAndFinal', kwargs={'pk':pk}))
        # master should submit proposal before submit paper
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
        # get the form
        form = FinalModelForm(request.POST, request.FILES)
        # create paper object if the form is valid
        if form.is_valid():
            form.save()
            proposal = Proposal.objects.get(user = pk, state = 0)
            project = Project.objects.get(proposal = proposal.id, state = 1)
            delta = project.postDate - proposal.postDate
            # paper can be submit after submit proposal, the interval shoud be at least 3 month
            if delta > timedelta(days=92):
                form.save()
                data = Project.objects.get(user=self.kwargs['pk'], state = 1)
                user = User.objects.get(id=self.kwargs['pk'])
                barCode = str(user.enrollYear-1910)+'-'+ user.username
                paper = Paper.objects.create(project = data, barCode = barCode)
                paper.save()

                doc = StudentDoc.objects.create(user = user)
                doc.save()

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
        # condition dict
        queryDict = {}
        getValue = self.request.GET
        # get selected condition
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
            
            # filter object satisfy all condition
            paper = Paper.objects.filter(**queryDict)
        else:
            paper = Paper.objects.all()

        # show objects with at most limit objects in each page
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
        # get the selected paper object
        paper = Paper.objects.get(id = pk)
        # find paper has not been borrowed
        try:
            findBookingExist = Booking.objects.exclude(state = 2).get(paper = paper.id)
        except Booking.DoesNotExist:
            findBookingExist = None
        
        # paper has been borrow
        if findBookingExist:
            if findBookingExist.user == request.user:
                messages.success(request, "你已經借走這份報告書/論文囉!!!")
            else:
                messages.success(request, "有人借走 " +  paper.project.name + " 囉!!!")
        else:
            # create year object
            try:
                year = Year.objects.get(year = (int(timezone.now().year) - 1911))
            except Year.DoesNotExist:
                year = None
            
            if not year:
                year = Year.objects.create(year = (int(timezone.now().year) - 1911))
                year.save()
            # create booking object
            booking = Booking.objects.create(user=request.user, paper = paper, bookingDate = timezone.now(), year = year)
            messages.success(request, "預約成功，請至資訊科學系辦公室借用!!!")
            # send email to department assistant
            send_mail('新的報告書預約', request.user.name + "在" + booking.bookingTime + "預約了 " + booking.paper.name, 'csshare.go@gmail.com', ['csshare.tw@gmail.com'], fail_silently=False)
            booking.save()
            

        return redirect(reverse('BorrowPaper', kwargs={'pk': request.user.id})  ) 
    
    
class GetEntityPaper(View):
    
    def get(self, request):
        # paper has been borrowed
        booking = Booking.objects.filter(state=1)
        context = {
            'booking':booking
        }
        return render(request, 'GetEntityPaper.html', context)
    
    def post(self, request):
        # get the barcode of the paper
        try:
            paper = Paper.objects.get(barCode = request.POST['barCode'])
        except Paper.DoesNotExist:
            messages.success(request, "無效的條碼...")
            return render(request, 'GetEntityPaper.html')
        # get booking object
        try:
            changeBookingState=Booking.objects.get(paper = paper.id, state = 0)
        except Booking.DoesNotExist:
            changeBookingState=None
        # change the state of the booking object
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
        # get the booking object
        try:
            booking = Booking.objects.get(paper__barCode = getValue['barCode'], state = 1)
        except Booking.DoesNotExist:
            booking = None

        # change the booking object to finish
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
        # get booking object of the user
        booking = Booking.objects.filter(user = request.user.id)
        # paginator
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
        # get booking
        booking = Booking.objects.get(id = pk)
        # cancel the booking
        send_mail('報告書預約取消', booking.paper.name + "的預約已取消!!", 'csshare.go@gmail.com', [request.user.email,], fail_silently=False)
        booking.delete()
        messages.success(request, "預約已取消!")

        return HttpResponseRedirect(reverse('UserBooking', kwargs={'pk': request.user.id})  ) 


class DisplayLicense(LoginRequiredMixin, View):

    def get(self, request):
        # get all license object
        license = License.objects.all()
        # paginator
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
        # filter
        queryDict = {}
        license = License.objects.all()
        getValue = self.request.POST
        # filter license object satisfy the condition
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

        # export selected license object to csv file
        if "export" in getValue:
            # filter license object
            license = License.objects.filter(**queryDict).values_list('user__name','user__username' , 'name','level', 'acqDate')
            # csv file
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("證照紀錄.csv"))         
            writer = csv.writer(response)       
                
            # write title to csv file
            writer.writerow(['姓名','學號','證照名稱','級別','取得日期',])
            # write data to csv file
            for license in license:
                writer.writerow(license)
            return response
        elif 'search' in getValue:
            # filter license object and show
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
        # download license proof
        elif 'download' in getValue:
            # filter license object
            license = License.objects.filter(**queryDict)
            # zip file
            file_zip = io.BytesIO()
            user_count = {}

            with zipfile.ZipFile(file_zip, 'w') as zf:
                # pack proof and set proper filename
                # (student number)-(student name)-number
                for i in license:
                    user_key = i.user.username + '-' + i.user.name
                    if user_key in user_count:
                        user_count[user_key] += 1
                    else:
                        user_count[user_key] = 1
                    image_data = default_storage.open(i.image.name, 'rb').read()
                    filename = user_key + '-' + str(user_count[user_key]) + '.jpg'
                    zf.writestr(filename, image_data)
            # download zip file
            file_zip.seek(0)
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="證照証明截圖.zip"'
            response.write(file_zip.read())
            return response
    

class DisplayProject(LoginRequiredMixin, ListView):
        
    def get(self, request):
        # get project object
        project = Project.objects.filter(state = 0)
        # paginator
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
        # condition dict
        queryDict = {}
        getValue = self.request.POST
        # collect conditions
        if getValue:
            if 'username' in getValue:
                queryDict['user__name__icontains'] = getValue['username']
            if 'enrollYear' in getValue and getValue['enrollYear'] != '':
                queryDict['user__enrollYear'] = int(getValue['enrollYear']) + 1911
            if 'professor' in getValue:
                queryDict['professor__icontains'] = getValue['professor']
            if 'field' in getValue and getValue['field'] != '':
                queryDict['field'] = getValue['field']
        # export select project object to csv file
        if "export" in getValue:
            # filter project object
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
            # filter project object
            project = Project.objects.filter(**queryDict, state = 0)
            # paginator
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
            # filter project object
            project = Project.objects.filter(**queryDict)
            # zip file
            file_zip = io.BytesIO()
            # write select project object into zip file
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
        # not implemented
        elif 'download_selected' in getValue:
            return render(request, 'DisplayProject.html', context)

class DisplayProposal(LoginRequiredMixin, ListView):
        
    def get(self, request):
        # get all proposal objects
        proposal = Proposal.objects.all()
        # paginator
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
        # condition dict
        queryDict = {}
        getValue = self.request.POST
        # collect conditios if any
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
        # export proposal object to csv file
        if "export" in getValue:
            # filter proposal object
            proposal = Proposal.objects.filter(**queryDict).values_list('user__name','user__username', 'professor', 'name')
            # csv file
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("計畫發表紀錄.csv"))         
            writer = csv.writer(response)       
                
            # write title into csv file
            writer.writerow(['姓名','學號','指導教授','計畫發表題目', '學制'])
            # write proposal object into csv file
            for proposal in proposal:
                writer.writerow(proposal)
            return response
        # search proposal object satisfied given condition
        elif 'search' in getValue:
            # filter proposal object
            proposal = Proposal.objects.filter(**queryDict)
            # paginator
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
        # download proposal cancel application
        elif 'download' in getValue:
            # filter proposal object
            proposal = Proposal.objects.filter(**queryDict, state = 1)
            # zip file
            file_zip = io.BytesIO()
            user_count = {}
            # put all cancel application into zip file with proper name
            # (student name)-(student name)-number
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
        # filter oral test object
        project = Project.objects.exclude(state = 0)
        # paginator
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
        # condition dict
        queryDict = {}
        getValue = self.request.POST
        # collect condition if any
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
        # export oral test object into csv file
        if "export" in getValue:
            # filter oral test object with selected attribute
            project = Project.objects.filter(**queryDict).exclude(state = 0).values_list('user__name','user__username', 'professor', 'name')
            # csv file
            response = HttpResponse(content_type='text/csv')
            response.charset = 'utf-8-sig'
            response['Content-Disposition'] = 'attachment; filename="%s"'%(urlquote("學位考試紀錄.csv"))         
            writer = csv.writer(response)       
                
            # write title into csv file
            writer.writerow(['姓名','學號','指導教授','計畫發表題目', '學制'])
            # write project object into csv file
            for project in project:
                writer.writerow(project)
            return response
        elif 'search' in getValue:
            # filter oral test object
            project = Project.objects.filter(**queryDict).exclude(state = 0)
            # paginator
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
        # download cancel application
        elif 'download' in getValue:
            # filter oral test object
            project = Project.objects.filter(**queryDict, state = 2)
            # zip file
            file_zip = io.BytesIO()
            user_count = {}
            # put selected oral test cancel application into zip file with proper file name
            # (student number)-(student name)- number
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
        
class EditStudentDoc(LoginRequiredMixin, ListView):

    def get(self, request, pk):
        # get oral test document object
        doc = StudentDoc.objects.get(user = pk)
        context = {
            'doc':doc,
        }
        return render(request, 'EditStudentDoc.html', context)
    
    def ChangeStudentDocState(request, pk, choice):
        # get oral test document object
        doc = StudentDoc.objects.get(id = pk)
        # change doument state
        if choice == 0:
            doc.qualifiedId = not doc.qualifiedId
        if choice == 1:
            doc.evaluationForm = not doc.evaluationForm
        if choice == 2:
            doc.assesmentResult = not doc.assesmentResult
        if choice == 3:
            doc.confirmation = not doc.confirmation

        doc.save()

        return redirect(reverse('EditStudentDoc', kwargs={'pk':doc.user.id}))
        
    
        
class ImportAndExport(LoginRequiredMixin, View):
    
    def get(self, request):
        return render(request, 'ImportAndExport.html')
    def post(self, request):
        # create multiple student account
        # inputs: .xlsx file
        if "multi" in request.POST:
            try:
                if request.FILES['myfile']:
                    # get .xlsx file
                    myfile = request.FILES['myfile']  
                    fs = FileSystemStorage()
                    filename = fs.save(myfile.name, myfile)
                    uploaded_file_url = fs.url(filename)
                    # read data from file 
                    exceldata = pd.read_csv("."+uploaded_file_url,encoding='utf-8')
                    # split excel data by titles
                    dbframe = exceldata
                    # create account
                    for dbframe in dbframe.itertuples():
                        obj = User.objects.create(username=dbframe.username,password=make_password(dbframe.password), name=dbframe.name,)
                        obj.save()

                    messages.success(request, "新增成功!")
                    return render(request, 'ImportAndExport.html', {
                        'uploaded_file_url': uploaded_file_url
                    })
            except Exception as identifier:            
                print(identifier)
        # create one student account
        elif "single" in request.POST:
            getValue = self.request.POST
            # check the student number has used
            try:
                user = User.objects.get(username = getValue['username'])
            except User.DoesNotExist:
                user = None
            # student number has been registered
            if user:
                messages.success(request, "已存在的使用者!!")
            # create account
            else:
                # enroll year
                new_enrollYear = int(getValue['username'][1:4])
                # check student number is valid
                if re.match(pattern_student, getValue['username']):
                    # create user object
                    user = User.objects.create(username=getValue['username'], password = make_password(getValue['password']), name=getValue['name'], enrollYear=new_enrollYear+1911, email = getValue['email'])
                    user.save()
                    messages.success(request, "新增成功!")
                else:
                    messages.success(request, "無效的學號!!")
                
        return render(request, 'ImportAndExport.html')

class SearchStudent(LoginRequiredMixin, ListView):
    # specified object
    model = User

    template_name = "SearchStudent.html"

    def get_queryset(self):
        # condition dict
        queryDict = {}
        # get condition if any
        # __icontains: get the object which contain the condition
        if self.request.GET:
            if "name" in self.request.GET:
                queryDict['name__icontains'] = self.request.GET['name']
            if "username" in self.request.GET:
                queryDict['username__icontains'] = self.request.GET['username']
            if 'enrollYear' in self.request.GET and self.request.GET['enrollYear'] != '':
                queryDict['enrollYear'] = int(self.request.GET['enrollYear']) + 1911
            queryset = User.objects.filter(**queryDict)
        else:
            # select user
            queryset = User.objects.all()
        # paginator
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
        # get user object
        student = User.objects.get(pk=pk)
        context={
            'student': student
        }
        return render(request, 'ModifyStudentInfo.html', context)

    def post(self, request, pk):
        getValue = self.request.POST
        # get user object
        student= User.objects.get(pk=pk)
        # modify student information with entered information if any
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
        # get user object and delete
        user = User.objects.get(id=pk)
        user.delete()
        return redirect(reverse('SearchStudent'))
    
class BookingList(LoginRequiredMixin, ListView):
    
    model = Booking

    template_name = "BookingList.html"

    def get_queryset(self):
        # condition dict
        queryDict = {}
        # get condition if any
        if self.request.GET:
            if "name" in self.request.GET:
                queryDict['user__name__icontains'] = self.request.GET['name']
            if "username" in self.request.GET:
                queryDict['user__username__icontains'] = self.request.GET['username']
            if 'state' in self.request.GET and self.request.GET['state'] != '':
                queryDict['state'] = self.request.GET['state']
            # filter booking object
            queryset = Booking.objects.filter(**queryDict)
        else:
            queryset = Booking.objects.all()
        # paginator
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
        # condition dict for search
        queryDict = {}
        # condition dict for draw chart
        drawDict = {}
        getValue = self.request.POST
        # get selected condition if any
        # condition can be used to search or draw analysis chart
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
        # filter booking
        booking = Booking.objects.filter(**queryDict).values_list('paper__project__name').distinct
        # filter paper has at least one booking
        paper = Paper.objects.filter(project__name__in = booking())
        # count how many times the paper has been lend
        for i in paper:
            i.lendTimes = Booking.objects.filter(paper = i, **queryDict).count()
            i.save()

        '''draw charts'''

        if 'draw' in getValue:
            drawingTitleLine1 = Drawing(200, 100)
            drawingTitleLine2 = Drawing(200, 100)
            # pdf file
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer)
            pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))
            # set title
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
            # draw title
            drawingPieChart1 = Drawing(400, 200)
            drawingPieChart2 = Drawing(400, 200)

            # draw Pie Chart
            # set Pie Chart attribute
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
        
            if getValue['bookingYear'] == '':
                # array to store values of each year
                BookingForSingalYear = []
                BookingForAccumulate = []
                category1 = []
                category2 = []
                years = Year.objects.all()
                acc = 0
                # get how many bookings in each year
                for year in years:
                    count = Booking.objects.filter(year = year, **drawDict).count()
                    BookingForSingalYear.append(count)
                    acc += count
                    BookingForAccumulate.append(acc)
                    category1.append(str(year.year) + '(' + str(count) + '次)')
                    category2.append(str(year.year) + '(' + str(acc) + '次)')
                # set data
                pc1.data = BookingForSingalYear
                pc2.data = BookingForAccumulate
                pc1.labels = category1
                pc2.labels = category2
                pc1.slices.fontSize = pc2.slices.fontSize = 18
                pc1.slices.fontName = pc2.slices.fontName = 'SimSun'
                # draw Pie Chart
                drawingPieChart1.add(pc1)
                drawingPieChart2.add(pc2)
                renderPDF.draw(drawingPieChart1, pdf, 150, 500)
                renderPDF.draw(drawingPieChart2, pdf, 150, 200)
                # set Chart title
                drawingChartName1 = Drawing(400, 200)
                drawingChartName2 = Drawing(400, 200)
                # draw chart title
                chartName1 = String(50, 50, '各年份借閱次數', fontName="SimSun", fontSize=30)
                chartName2 = String(50, 50, '歷年累計借閱次數', fontName="SimSun", fontSize=30)
                drawingChartName1.add(chartName1)
                drawingChartName2.add(chartName2)
                renderPDF.draw(drawingChartName1, pdf, 125, 400)
                renderPDF.draw(drawingChartName2, pdf, 125, 100)
            # draw chart of a specified year
            else:
                # no condition is selected
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
                # type is selected
                elif getValue['type'] != '' and getValue['field'] == '':
                    # array to store value
                    classByField = []
                    # get value of each field
                    for field in range(3):
                        count = Booking.objects.filter(year__year = getValue['bookingYear'], paper__project__field = field).count()
                        classByField.append(count)
                    category2 = ['軟體開發及程式設計(' + str(classByField[0]) + '次)', '網路及多媒體應用(' + str(classByField[1]) + '次)', '系統及演算法開發(' + str(classByField[2]) + '次)']
                    # set chart data and label
                    pc2.data = classByField
                    pc2.labels = category2
                    # draw chart
                    drawingPieChart2.add(pc2)
                    renderPDF.draw(drawingPieChart2, pdf, 150, 500)
                    # set chart title
                    drawingChartName2 = Drawing(400, 200)
                    # draw chart title
                    chartName2 = String(50, 50, '以領域分類借閱次數', fontName="SimSun", fontSize=30)
                    drawingChartName2.add(chartName2)
                    renderPDF.draw(drawingChartName2, pdf, 100, 400)
                # field is selected
                elif getValue['type'] == '' and getValue['field'] != '':
                    # array to store value
                    classByType = []
                    # get value of each type
                    for type in range(3):
                        count = Booking.objects.filter(year__year = getValue['bookingYear'], paper__project__user__identity = type).count()
                        classByType.append(count)
                    category2 = ['大學部(' + str(classByType[0]) + '次)', '日間碩士班(' + str(classByType[1]) + '次)', '在職碩士專班(' + str(classByType[2]) + '次)']
                    # set chart data and label
                    pc2.data = classByType
                    pc2.labels = category2
                    # draw chart
                    drawingPieChart2.add(pc2)
                    renderPDF.draw(drawingPieChart2, pdf, 150, 500)
                    # set chart title
                    drawingChartName2 = Drawing(400, 200)
                    # draw chart title
                    chartName2 = String(50, 50, '以學制分類借閱次數', fontName="SimSun", fontSize=30)
                    drawingChartName2.add(chartName2)
                    renderPDF.draw(drawingChartName2, pdf, 100, 400)
                    
            # save pdf and download
            pdf.save()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename="分析圖.pdf")
        
        else:
            # show selected paper
            # paginator
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
        # update multiple paper
        if "multi" in request.POST:
            try:
                # get csv file
                if request.FILES['myfile']:
                    myfile = request.FILES['myfile']  
                    fs = FileSystemStorage()
                    filename = fs.save(myfile.name, myfile)
                    uploaded_file_url = fs.url(filename) 
                    exceldata = pd.read_csv("."+uploaded_file_url,encoding='utf-8')
                    dbframe = exceldata
                    # iterate through all rows
                    for dbframe in dbframe.itertuples():
                        # create user if not exist
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
                        # check is master or bachelor
                        if user.identity != 0:
                            myState = 1
                        else:
                            myState = 0
                        # create project object if not exist
                        try:
                            project = Project.objects.get(user = user)
                        except Project.DoesNotExist:
                            project = Project.objects.create(user = user, name = dbframe.paperName, professor = dbframe.professor, field = dbframe.field, state = myState)
                            project.save()
                        # set year for barcode
                        if user.identity == 0:
                            title = user.enrollYear - 1911 + 3
                        elif user.identity == 2 or user.identity == 3:
                            title = user.enrollYear - 1911 + 1
                        # create paper object if not exist
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
        # update 1 paper
        elif "single" in request.POST:
            getValue = self.request.POST
            # enroll year is required
            if getValue['enrollYear'] == '':
                return render(request, 'HistoryPaperUpdate.html')
            # get target student
            # if this student has not account, create an account for this student
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
            # check is  bachelor or master
            if user.identity != 0:
                myState = 1
            else:
                myState = 0
            # create project object if not exist
            try:
                project = Project.objects.get(user = user)
            except Project.DoesNotExist:    
                project = Project.objects.create(user = user, name = getValue['paperName'], professor = getValue['professor'], field = 0, state = myState)
                project.save()
            # set year for barcode
            if user.identity == 0:
                title = user.enrollYear - 1911 + 3
            elif user.identity == 2 or user.identity == 3:
                title = user.enrollYear - 1911 + 1
            # create paper object if not exist
            try:
                paper = Paper.objects.get(project = project)
            except Paper.DoesNotExist:
                paper = Paper.objects.create(project = project, barCode = str(title) + '-' + user.username)
                paper.save()

            messages.success(request, "上傳成功!")
                
        return render(request, 'HistoryPaperUpdate.html')


class AuditLicense(LoginRequiredMixin, UpdateView):
    # specified target object
    model = License
    fileds = '__all__'
    # target form
    form_class = LicenseAuditForm
    # target template
    template_name = 'AuditLicense.html'

    def get_success_url(self):
        # change license state
        # pass is pressed
        if 'pazz' in self.request.POST:
            self.object.pazz = 1
            self.object.save()
        # fail is pressed
        elif 'fail' in self.request.POST:
            self.object.pazz = 2
            self.object.save()
        # get license object that has not been audit
        license = License.objects.filter(pazz=0)
        # if there exist license has not been audit
        # take one license and refresh the page
        if license:
            pk = license.first().id
            return reverse('AuditLicense', kwargs={'pk': pk})
        else:
            return reverse('DisplayLicense')

class EditLicense(LoginRequiredMixin, UpdateView):
    # specified target object
    model = License
    fileds = '__all__'
    # target form
    form_class = LicenseEditForm
    # target template
    template_name = 'EditLicense.html'

    def get_success_url(self):
        messages.success(self.request, "編輯成功")
        return reverse('UserLicense', kwargs={'pk':self.request.user.id})

class EditProject(LoginRequiredMixin, UpdateView):
    # specified target object
    model = Project
    fileds = '__all__'
    # target form
    form_class = ProjectModelForm
    # target template
    template_name = 'EditProject.html'

    def get_success_url(self):
        return reverse('UserProject', kwargs={'pk':self.request.user.id})
    
class EditProposal(LoginRequiredMixin, UpdateView):
    # target object
    model = Proposal
    fileds = '__all__'
    # target form
    form_class = ProposalEditForm
    # target template
    template_name = 'EditProposal.html'

    def get_success_url(self):
        return reverse('UserProposalAndFinal', kwargs={'pk':self.request.user.id})
    
class EditFinal(LoginRequiredMixin, UpdateView):
    # target object
    model = Project
    fileds = '__all__'
    # target form
    form_class = FinalEditForm
    # target template
    template_name = 'EditFinal.html'

    def get_success_url(self):
        return reverse('UserProposalAndFinal', kwargs={'pk':self.request.user.id})
    
class DeleteLicense(LoginRequiredMixin, DeleteView):
    # target object
    model = License
    fileds = '__all__'
    # target template
    template_name = 'DeleteLicense.html'

    def get_success_url(self):
        return reverse('UserLicense', kwargs={'pk':self.request.user.id})