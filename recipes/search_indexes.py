import datetime
from haystack import indexes
from recipes.models import Lesson


class LessonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    date = indexes.DateTimeField(null=True, model_attr='date')

    def get_model(self):
        return Lesson
