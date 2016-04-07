from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic.detail import DetailView
from django.shortcuts import redirect

from recipes.models import Lesson

from haystack.generic_views import SearchView
from haystack.forms import HighlightedSearchForm

from haystack.utils import Highlighter
from django.utils.html import strip_tags
import markdown2
from django.views.generic.base import RedirectView

class SearchView(LoginRequiredMixin, SearchView):
    """My custom search view."""

    form_class = HighlightedSearchForm
    
    def get_queryset(self):
        queryset = super(SearchView, self).get_queryset()
        # further filter queryset based on some set of criteria
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        
        return context
        

class FullTextHighlighter(Highlighter):
    max_length = 20000000
    def highlight(self, text_block):
        self.text_block = strip_tags(text_block)
        highlight_locations = self.find_highlightable_words()
        return self.render_html(highlight_locations, 0, len(text_block))
                
class LessonView(LoginRequiredMixin, DetailView):

    model = Lesson

    def get(self, request, *args, **kwargs):
        check = request.GET.get('check')
        if check:
            les = self.get_object()
            les.status = 4
            les.save()
            nles = Lesson.objects.filter(status = 3).order_by("?")[0]
            return redirect(nles)
        return super(LessonView, self).get(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super(LessonView, self).get_context_data(**kwargs)
        highlight = self.request.GET.get('highlight')
        les = context['object']
        text = les.raw_text
        
        status_name = ["Ruw", "Ruwe tekst", "Titel en datum", "Ongeverifi\xeberd", "Geverifi\xeberd"][les.status]

        ntotal = Lesson.objects.all().count()
        nchecked = Lesson.objects.filter(status = 4).count()
        
        if highlight:
            hl = FullTextHighlighter(highlight)
            text = hl.highlight(text)
        if les.parsed:
            p = les.parsed
            if highlight:
                hl = FullTextHighlighter(highlight)
            
                p = hl.highlight(p)

            
            p = p.replace("\r\n", "\n").replace("\n\n|", "\n\n|  |\n|---\n|")
            print(repr(p))
            parsed_html = markdown2.markdown(p, extras=["tables", "metadata"])
        
        context.update(**locals())
        return context

    

class CheckRedirectView(RedirectView):

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        les = Lesson.objects.filter(status = 3).order_by("?")[0]
        return les.get_absolute_url()
        return super(ArticleCounterRedirectView, self).get_redirect_url(*args, **kwargs)
