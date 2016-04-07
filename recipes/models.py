from django.db import models
from django.core.urlresolvers import reverse

_PARSE_HELP = ("Pas hier de opdeling van de kookles in recepten aan. "
               "De titel van elk recept wordt aangegeven met ## titel, en ingredienten met | ingredient |. "
               "Als je klaar bent klik dan op 'save and continue editing' en op 'view on site'")

class Lesson(models.Model):
    filename = models.CharField(max_length=200)
    docfile = models.FileField()
    raw_text = models.TextField(null=True)
    parsed = models.TextField(null=True, help_text=_PARSE_HELP) 
    status = models.IntegerField(default=0)
    problems = models.TextField(null=True,blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['date']

    def get_absolute_url(self):
        return reverse('recipes:lesson-detail', args=[str(self.id)])
