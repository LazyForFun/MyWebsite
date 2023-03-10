from .models import Project, License
from django import forms
import django_filters

class ProjectFilter(django_filters.FilterSet):

    project_username = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput()
    )

    project_professor = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput()
    )

    class Meta:
        model = Project
        fields = ('project_username', 'project_professor',)

class LicenseFilter(django_filters.FilterSet):

    license_username = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput()
    )

    class Meta:
        model = License
        fields = ('license_username', 'license_pass', 'license_level',)