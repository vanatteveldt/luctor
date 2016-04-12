from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings

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

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    lesson = models.ForeignKey(Lesson, related_name="recipes")
    ingredients = models.TextField()
    instructions = models.TextField()
    from django.conf import settings
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_recipes")
    
    @property
    def full_text(self):
        return "\n\n".join([self.ingredients, self.instructions])

    @property
    def lesson_title(self):
        return self.lesson.title
        
    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse('recipes:recipe-detail', args=[str(self.id)])

class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="comments", null=True)
    lesson = models.ForeignKey(Lesson, related_name="comments", null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="comments")
    date = models.DateTimeField(db_column='insertdate', auto_now_add=True)
    text = models.TextField()
