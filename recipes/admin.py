from django.contrib import admin
from django import forms

from recipes.models import Lesson

class LessonAdmin(admin.ModelAdmin):
    search_fields = ['title', 'text']
    list_display = ('date', 'title')
    list_filter = ('date',)
    date_hierarchy = 'date'


admin.site.register(Lesson, LessonAdmin)
