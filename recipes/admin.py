from django.contrib import admin
from django import forms

from recipes.models import Lesson, Recipe

class LessonAdmin(admin.ModelAdmin):
    search_fields = ['title', 'filename']
    list_display = ('title', 'date', 'filename', 'status', 'problems')

admin.site.register(Lesson, LessonAdmin)

def lesson_title(recipe):
    return recipe.lesson.title

class RecipeAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ('title', lesson_title)

admin.site.register(Recipe, RecipeAdmin)
