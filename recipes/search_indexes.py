import datetime
from haystack import indexes
from recipes.models import Lesson, Recipe

class RecipeIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    lesson_title = indexes.CharField()

    def prepare_lesson_title(self, obj):
        return obj.lesson.title
    def get_model(self):
        return Recipe
