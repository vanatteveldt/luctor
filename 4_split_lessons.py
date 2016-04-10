import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luctor.settings")
django.setup()

from recipes.models import Lesson, Recipe

def get_recipes(lesson):
    recipe = None
    for line in lesson.parsed.splitlines():
        if line.startswith("##"):
            if recipe is not None:
                yield recipe
            recipe = Recipe(title=line[2:].strip(), lesson=lesson)
        elif recipe and line.strip():
            if line.strip().startswith("|"):
                recipe.ingredients += line.strip("| ") + "\n"
            else:
                recipe.instructions += line + "\n"

    yield recipe


for lesson in Lesson.objects.filter(status=4):
    print(lesson.title)
    lesson.recipes.all().delete()
    for recipe in get_recipes(lesson):
        recipe.save()
    lesson.status=5
    lesson.save()

