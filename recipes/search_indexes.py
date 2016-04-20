import datetime
from haystack import indexes
from recipes.models import Lesson, Recipe

class RecipeIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.NgramField(document=True, use_template=True)
    lesson_title = indexes.CharField()

    def prepare_lesson_title(self, obj):
        return obj.lesson.title
    def get_model(self):
        return Recipe

    def index_queryset(self, using=None):
        "Used when the entire index for model is updated."
        return self.get_model().objects.filter(lesson__status=5)
