from django.contrib import admin
from django import forms

from recipes.models import Lesson

class LessonAdmin(admin.ModelAdmin):
    search_fields = ['title', 'filename']
    list_display = ('title', 'date', 'filename', 'status', 'problems')

admin.site.register(Lesson, LessonAdmin)
