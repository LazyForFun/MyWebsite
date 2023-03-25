from django.contrib import admin
from .models import User, License, Project, Proposal, Booking, Paper, Year
# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(License)
admin.site.register(Proposal)
admin.site.register(Booking)
admin.site.register(Paper)
admin.site.register(Year)