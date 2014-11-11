from django.contrib import admin

from recipes.models import Lesson

class LessonAdmin(admin.ModelAdmin):
    search_fields = ['title', 'text']
    list_display = ('date', 'title')

admin.site.register(Lesson, LessonAdmin)
