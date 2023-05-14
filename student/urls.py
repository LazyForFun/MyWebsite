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
    path('License-pass', views.Home.as_view(), name='Home'),
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
    path('DisplayProject', views.DisplayProject.as_view(), name='DisplayProject'),#報告書瀏覽
    path('DisplayProposal', views.DisplayProposal.as_view(), name='DisplayProposal'),#計畫發表瀏覽
    path('DisplayFinal', views.DisplayFinal.as_view(), name='DisplayFinal'),#學位考試瀏覽
    path('AuditLicense/<int:pk>', views.AuditLicense.as_view(), name='AuditLicense'),#審核
    path('SearchStudent', views.SearchStudent.as_view(), name='SearchStudent'),#尋找特定學生
    path('ModifyStudentInfo/<int:pk>', views.ModifyStudentInfo.as_view(), name='ModifyStudentInfo'),#修改學生資料
    path('DeleteStudentInfo/<int:pk>', views.ModifyStudentInfo.deleteStudent, name='DeleteStudent'),#刪除使用者
    path('BookingList', views.BookingList.as_view(), name='BookingList'),#借用申請表
    path('HistoryBookingAnalysis', views.HistoryBookingAnalysis.as_view(), name='HistoryBookingAnalysis'),#歷史借閱分析
    path('HistoryPaperUpdate', views.HistoryPaperUpdate.as_view(), name='HistoryPaperUpdate'),#補回歷年報告書
    #學士
    path('PassProject/<int:pk>', views.PassProject.as_view(), name='PassProject'), #專題繳交
    path('PassLicense/<int:pk>', views.PassLicense.as_view(), name='PassLicense'), #證照繳交
    path('UserProject/<int:pk>', views.UserProject.as_view(), name='UserProject'),#已繳交的專題
    path('UserLicense/<int:pk>', views.UserLicense.as_view(), name='UserLicense'),#已繳交的證照
    path('EditLicense/<int:pk>', views.EditLicense.as_view(), name='EditLicense'),#編輯證照
    path('EditProject/<int:pk>', views.EditProject.as_view(), name='EditProject'),#編輯專題
    path('DeleteLicense/<int:pk>', views.DeleteLicense.as_view(), name='DeleteLicense'),#刪除已繳交的證照
    #碩士
    path('PassProposal/<int:pk>', views.PassProposal.as_view(), name='PassProposal'), #計畫發表
    path('EditProposal/<int:pk>', views.EditProposal.as_view(), name='EditProposal'),#編輯已繳交的計畫發表
    path('PassFinal/<int:pk>', views.PassFinal.as_view(), name='PassFinal'),#學位考試
    path('EditFinal/<int:pk>', views.EditFinal.as_view(), name='EditFinal'),#編輯已繳交的學位考試
    path('UserProposalAndFinal/<int:pk>', views.UserProposalAndFinal.as_view(), name='UserProposalAndFinal'),#已繳交的計畫發表與學位考試歷程
    path('UploadCancel/<str:pk>', views.UploadCancel.as_view(), name="UploadCancel"),#取消申請表上傳
    #學生共用
    path('BorrowPaper/<int:pk>', views.BorrowPaper.as_view(), name='BorrowPaper'),#報告書列表
    path('MakeBooking/<int:pk>', views.BorrowPaper.MakeBooking, name='MakeBooking'),#借用表單
    path('UserBooking/<int:pk>', views.UserBooking.as_view(), name='UserBooking'),#已預約清單
    path('DeleteBooking/<int:pk>', views.UserBooking.deleteBooking, name='DeleteBooking'),#刪除預約
   
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
