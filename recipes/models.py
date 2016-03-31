from django.db import models
from django.core.urlresolvers import reverse

class Lesson(models.Model):
    filename = models.CharField(max_length=200)
    docfile = models.FileField()
    raw_text = models.TextField(null=True)
    status = models.IntegerField(default=0)
    problems = models.TextField(null=True,blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['date']
        
    def get_absolute_url(self):
        return reverse('lesson-detail', args=[str(self.id)])
