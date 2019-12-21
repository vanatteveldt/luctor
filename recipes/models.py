import logging

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from ipware.ip import get_ip


auth_log = logging.getLogger('luctor.auth')

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
    aanwezig = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.title or '(no title)'
    
    class Meta:
        ordering = ['date']

    def get_absolute_url(self):
        return reverse('recipes:lesson-detail', args=[str(self.id)])

    @property
    def aanwezige_namen(self):
        if not self.aanwezig: return []
        return [x.strip().lower() for x in self.aanwezig.split(",")]

    def can_view(self, user):
        return user.is_superuser or (user.username.lower() in self.aanwezige_namen)


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    lesson = models.ForeignKey(Lesson, related_name="recipes")
    ingredients = models.TextField()
    instructions = models.TextField()
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_recipes", through='Like')
    
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


class Picture(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="pictures")
    image = models.ImageField()
    image_small = models.ImageField(null=True)
    image_thumb = models.ImageField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="pictures")
    date = models.DateTimeField(db_column='insertdate', auto_now_add=True)
    favourite = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-favourite', 'date']


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="comments")
    date = models.DateTimeField(db_column='insertdate', auto_now_add=True)
    image = models.ImageField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['date']


class Like(models.Model):
    recipe = models.ForeignKey(Recipe)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(db_column='insertdate', auto_now_add=True)
    favorite = models.BooleanField(default=True)  # for false, gives recent views

    class Meta:
        unique_together = ('recipe', 'user')


def log_login(sender, user, request, **kwargs):
    ip = get_ip(request)
    auth_log.info("[{ip}] LOGIN USER {user}".format(**locals()))


user_logged_in.connect(log_login)


@receiver(pre_delete, sender=Lesson)
def lesson_pre_delete(sender, instance, **kwargs):
    from recipes.search_indexes import RecipeIndex  # lazy load to avoid circular import
    for recipe in instance.recipes.all():
        RecipeIndex().remove_object(recipe)


class Menu(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="menus")
    date = models.DateTimeField(db_column='insertdate', auto_now_add=True)


class MenuRecipe(models.Model):
    menu = models.ForeignKey(Menu)
    recipe = models.ForeignKey(Recipe)
    order = models.IntegerField(default=1)

    class Meta:
        unique_together = ('recipe', 'menu')



