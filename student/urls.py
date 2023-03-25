"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import staticfiles


urlpatterns = [
    #首頁標籤
    path('', views.Home.as_view(), name='Home'),
    path('GetEntityPaper', views.GetEntityPaper.as_view(), name='GetEntityPaper'),
    path('ReturnEntityPaper', views.ReturnEntityPaper.as_view(), name='ReturnEntityPaper'),
    #登入、登出、個人資訊
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('Signin', views.Signin.as_view(), name='Signin'),#註冊
    path('EditPassword/<int:pk>', views.EditPassword.as_view(), name='EditPassword'),#編輯密碼
    path('ForgetPassword', views.ForgetPassword.as_view(), name='ForgetPassword'),
    #系助教端
    path('ImportAndExport', views.ImportAndExport.as_view(), name = 'ImportAndExport'),#匯入匯出
    #path('CheckLicense', views.CheckLicense.as_view(), name='CheckLicense'),#證照瀏覽
    path('DisplayLicense', views.DisplayLicense.as_view(), name='DisplayLicense'),#證照瀏覽
    path('DisplayProject', views.DisplayProject.as_view(), name='DisplayProject'),#專題瀏覽
    path('AuditLicense/<int:pk>', views.AuditLicense.as_view(), name='AuditLicense'),#審核
    path('SearchStudent', views.SearchStudent.as_view(), name='SearchStudent'),#尋找特定學生
    path('ModifyStudentInfo/<int:pk>', views.ModifyStudentInfo.as_view(), name='ModifyStudentInfo'),#修改學生資料
    path('DeleteStudentInfo/<int:pk>', views.ModifyStudentInfo.deleteStudent, name='DeleteStudent'),
    path('BookingList', views.BookingList.as_view(), name='BookingList'),#借用申請表
    path('HistoryBookingAnalysis', views.HistoryBookingAnalysis.as_view(), name='HistoryBookingAnalysis'),
    #學士端
    path('PassProject/<int:pk>', views.PassProject.as_view(), name='PassProject'), #專題
    path('PassLicense/<int:pk>', views.PassLicense.as_view(), name='PassLicense'), #證照
    path('UserProject/<int:pk>', views.UserProject.as_view(), name='UserProject'),
    path('UserLicense/<int:pk>', views.UserLicense.as_view(), name='UserLicense'),
    path('EditLicense/<int:pk>', views.EditLicense.as_view(), name='EditLicense'),
    path('EditProject/<int:pk>', views.EditProject.as_view(), name='EditProject'),
    path('DeleteLicense/<int:pk>', views.DeleteLicense.as_view(), name='DeleteLicense'),
    #碩士端
    path('PassProposal/<int:pk>', views.PassProposal.as_view(), name='PassProposal'), #論文
    path('PassFinal/<int:pk>', views.PassFinal.as_view(), name='PassFinal'),
    #學生共用
    path('BorrowPaper/<int:pk>', views.BorrowPaper.as_view(), name='BorrowPaper'),
    path('MakeBooking/<int:pk>', views.BorrowPaper.MakeBooking, name='MakeBooking'),#借用表單
    path('UserBooking/<int:pk>', views.UserBooking.as_view(), name='UserBooking'),#預約清單
    path('DeleteBooking/<int:pk>', views.UserBooking.deleteBooking, name='DeleteBooking'),
   
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
