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
myPath='license-pass'+'/'
urlpatterns = [
    #首頁標籤
    path(myPath+'Home', views.Home.as_view(), name='Home'),
    path(myPath+'BorrowPaper', views.BorrowPaper.as_view(), name='BorrowPaper'),
    #path(myPath+'BookingCart', views.BookingCart.as_view(), name='BookingCart'),
    #登入與登出
    path(myPath+'login', views.LoginView.as_view(), name='login'),
    path(myPath+'logout', views.LogoutView.as_view(), name='logout'),
    #系助教端
    path(myPath+'ImportAndExport', views.ImportAndExport.as_view(), name = 'ImportAndExport'),#匯入匯出
    path(myPath+'CheckLicense', views.CheckLicense.as_view(), name='CheckLicense'),#證照瀏覽
    path(myPath+'DisplayLicense', views.DisplayLicense.as_view(), name='DisplayLicense'),#證照瀏覽
    path(myPath+'DisplayProject', views.DisplayProject.as_view(), name='DisplayProject'),#專題瀏覽
    path(myPath+'AuditLicense/<int:pk>', views.AuditLicense.as_view(), name='AuditLicense'),#審核
    path(myPath+'SearchStudent', views.SearchStudent.as_view(), name='SearchStudent'),#尋找特定學生
    path(myPath+'ModifyStudentInfo/<int:pk>', views.ModifyStudentInfo.as_view(), name='ModifyStudentInfo'),#修改學生資料
    path(myPath+'BookingProject/<int:pk>', views.BookingProject.as_view(), name='BookingProject'),#借用表單
    path(myPath+'BookingPaper/<int:pk>', views.BookingPaper.as_view(), name='BookingPaper'),#借用表單
    path(myPath+'BookingList', views.BookingList.as_view(), name='BookingList'),#借用申請表
    path(myPath+'ChangeBookingState/<int:pk>', views.BookingList.changeBookingState, name='ChangeBookingState'),
    path(myPath+'FinishBooking/<int:pk>', views.BookingList.finishBooking, name='FinishBooking'),#刪除已完成的借用
    #學士端
    path(myPath+'PassProject/<int:pk>', views.PassProject.as_view(), name='PassProject'), #專題
    path(myPath+'PassLicense/<int:pk>', views.PassLicense.as_view(), name='PassLicense'), #證照
    path(myPath+'UserProject/<int:pk>', views.UserProject.as_view(), name='UserProject'),
    path(myPath+'UserLicense/<int:pk>', views.UserLicense.as_view(), name='UserLicense'),
    path(myPath+'EditLicense/<int:pk>', views.EditLicense.as_view(), name='EditLicense'),
    path(myPath+'EditProject/<int:pk>', views.EditProject.as_view(), name='EditProject'),
    path(myPath+'DeleteLicense/<int:pk>', views.DeleteLicense.as_view(), name='DeleteLicense'),
    #碩士端
     path(myPath+'PassProposal/<int:pk>', views.PassProposal.as_view(), name='PassProposal'), #論文
   
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
