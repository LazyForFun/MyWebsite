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

urlpatterns = [
    path('Home', views.Home.as_view(), name='Home'),
    #登入與登出
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    #系助教端
    path('UserProject/<int:pk>', views.UserProject.index, name='UserProject'),
    path('UserLicense/<int:pk>', views.UserLicense.index, name='UserLicense'),
    path('ImportAndExport', views.ImportAndExport.Import_csv, name = 'ImportAndExport'),#匯入匯出
    path('CheckLicense', views.CheckLicense.index, name = 'CheckLicense'),#證照瀏覽
    path('DisplayLicense', views.DisplayLicense.as_view(), name = 'DisplayLicense'),#證照瀏覽
    path('DisplayProject', views.DisplayProject.as_view(), name = 'DisplayProject'),#專題瀏覽
    path('AuditLicense/<int:pk>', views.AuditLicense.as_view(), name = 'AuditLicense'),#審核
    #學士端
    path('PassProject/<int:pk>', views.PassProject.index, name = 'PassProject'), #專題
    path('PassLicense/<int:pk>', views.PassLicense.index, name = 'PassLicense'), #證照
    path('PassProposal/<int:pk>', views.PassProposal.index, name = 'PassProposal'), #證照
    path('EditLicense/<int:pk>', views.EditLicense.as_view(), name = 'EditLicense'),
    path('EditProject/<int:pk>', views.EditProject.as_view(), name = 'EditProject'),
    path('DeleteLicense/<int:pk>', views.DeleteLicense.as_view(), name = 'DeleteLicense'),
    #碩士端
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
