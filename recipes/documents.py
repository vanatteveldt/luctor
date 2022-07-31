from django_elasticsearch_dsl import Document, TextField
from django_elasticsearch_dsl.registries import registry

from recipes.models import Recipe


@registry.register_document
class RecipeDocument(Document):
    lesson = TextField()

    def prepare_lesson(self, instance):
        return instance.lesson.title

    class Index:
        name = 'recipes'

    class Django:
        model = Recipe
        fields = ['title', 'ingredients', 'instructions']
