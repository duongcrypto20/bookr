from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User

class Comment8orAdminSite(AdminSite):
    site_header = 'c8admin'
    index_title = 'c8admin'
    title_header = 'c8admin'
    logout_template = 'comment8or/logged_out.html'

admin_site = Comment8orAdminSite(name='c8admin')
admin_site.register(User)
admin_site.register(Group)