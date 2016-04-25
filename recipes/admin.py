from django.contrib import admin
from django import forms

from recipes.models import *

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

class CommentAdmin(admin.ModelAdmin):
    search_fields = ['user', 'text']
    list_display = ('pk', 'user', 'date', 'text', 'recipe')

admin.site.register(Comment, CommentAdmin)

class PictureAdmin(admin.ModelAdmin):
    search_fields = ['recipe', 'user']
    list_display = ('pk', 'recipe', 'user', 'image')

admin.site.register(Picture, PictureAdmin)

class LikeAdmin(admin.ModelAdmin):
    search_fields = ['recipe', 'user']
    list_display = ('pk', 'recipe', 'user', 'date')

admin.site.register(Like, LikeAdmin)
