from django.db import models

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    docfile = models.FileField()
    text = models.TextField()
