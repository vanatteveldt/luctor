from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic.detail import DetailView

from recipes.models import Lesson

from haystack.generic_views import SearchView
from haystack.forms import HighlightedSearchForm

from haystack.utils import Highlighter
from django.utils.html import strip_tags
        
class SearchView(LoginRequiredMixin, SearchView):
    """My custom search view."""

    form_class = HighlightedSearchForm
    
    def get_queryset(self):
        queryset = super(SearchView, self).get_queryset()
        # further filter queryset based on some set of criteria
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        print( "!", context)
        # do something
        print(dir(context['paginator']))
        return context
        

class FullTextHighlighter(Highlighter):
    max_length = 20000000
    def highlight(self, text_block):
        self.text_block = strip_tags(text_block)
        highlight_locations = self.find_highlightable_words()
        return self.render_html(highlight_locations, 0, len(text_block))
                
class LessonView(LoginRequiredMixin, DetailView):

    model = Lesson

    def get_context_data(self, **kwargs):
        context = super(LessonView, self).get_context_data(**kwargs)
        highlight = self.request.GET.get('highlight')
        les = context['object']
        text = les.raw_text
        if highlight:
            hl = FullTextHighlighter(highlight)
            text = hl.highlight(text)
        if les.parsed:
            import markdown2
            p = les.parsed
            if highlight:
                hl = FullTextHighlighter(highlight)
            
                p = hl.highlight(p)
                        
            parsed_html = markdown2.markdown(p, extras=["tables"])
        
        context.update(**locals())
        return context
