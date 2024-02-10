from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin

from blog.models import Articles


# @admin.register(Articles)
# class ArticlesAdmin(admin.ModelAdmin):
#     list_display = ('title', 'slug', 'time_create', 'is_published', 'photo')
#     ordering = ['-time_create', ]


class ArticlesAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Articles
        fields = '__all__'


class ArticlesAdmin(admin.ModelAdmin):
    form = ArticlesAdminForm


admin.site.register(Articles, ArticlesAdmin)
