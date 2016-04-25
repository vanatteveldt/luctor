import django; django.setup()

from recipes.models import Picture
from recipes import thumbnails

for p in Picture.objects.all():#filter(image_small__isnull=True):
    print(p.recipe.title)
    thumbnails.set_thumbnails(p)
