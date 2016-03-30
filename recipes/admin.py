from django.contrib import admin
from django import forms

from recipes.models import Lesson

class LessonAdmin(admin.ModelAdmin):
    search_fields = ['filename']
    list_display = ('filename', 'status', 'problems')

admin.site.register(Lesson, LessonAdmin)
