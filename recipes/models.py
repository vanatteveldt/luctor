from django.db import models

class Lesson(models.Model):
    filename = models.CharField(max_length=200)
    docfile = models.FileField()
    raw_text = models.TextField(null=True)
    status = models.IntegerField(default=0)
    problems = models.TextField(null=True)
    title = models.CharField(max_length=255, null=True)
    date = models.DateField(null=True)
