from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, FormView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django import forms
import logging
from recipes.models import Lesson, Recipe, Comment, Like
from recipes.search_indexes import RecipeIndex
from haystack.generic_views import SearchView
from haystack.forms import HighlightedSearchForm

from haystack.utils import Highlighter
import os
import markdown2
from django.views.generic.base import RedirectView
from .upload import process_file, get_recipes

class SearchView(LoginRequiredMixin, SearchView):
    """My custom search view."""

    form_class = HighlightedSearchForm
    
    def get_queryset(self):
        queryset = super(SearchView, self).get_queryset()
        # further filter queryset based on some set of criteria
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        
        
        your_likes = Like.objects.filter(user=self.request.user).order_by('-date')[:10]
        other_likes = Like.objects.exclude(user=self.request.user).order_by('-date')[:10]
        recent_lessons = Lesson.objects.order_by('-date')[:10]
        recent_comments = Comment.objects.order_by('-date')[:10]
        context.update(**locals())
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
        recipes = les.recipes.all()
        status_name = ["Ruw", "Ruwe tekst", "Titel en datum", "Ongeverifi\xeberd", "Geverifi\xeberd", "Gesplitst"][les.status]

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
            parsed_html = markdown2.markdown(p, extras=["tables", "metadata"])
        
        context.update(**locals())
        return context

    

class CheckRedirectView(RedirectView):

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        les = Lesson.objects.filter(status = 3).order_by("?")[0]
        return les.get_absolute_url()
        return super(ArticleCounterRedirectView, self).get_redirect_url(*args, **kwargs)

class RecipeView(LoginRequiredMixin, DetailView):
    model = Recipe

    def post(self, request, *args, **kwargs):
        comment = self.request.POST.get('comment')
        if comment:
            Comment.objects.create(recipe  = self.get_object(), user=self.request.user, text=comment)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RecipeView, self).get_context_data(**kwargs)
        recept = context['object']
        
        like = self.request.GET.get('like')
        if like is not None:
            exists = Like.objects.filter(recipe=recept, user=self.request.user).exists()
            if (like == "1"):
                if not exists:
                    Like.objects.create(recipe=recept, user=self.request.user)
            else:
                if exists:
                    Like.objects.filter(recipe=recept, user=self.request.user).delete()
            
        comments = recept.comments.all()
        
        ingredient_rows = list(row.split("|") for row in recept.ingredients.splitlines())
        highlight = self.request.GET.get('highlight')
        isliked = recept.likes.filter(pk=self.request.user.pk).exists()
        context.update(**locals())
        return context

class UploadView(CreateView):
    template_name="recipes/upload.html"
    model = Lesson
    fields = ['docfile']
    def form_valid(self, form):
        res = super(UploadView, self).form_valid(form)
        try:
            process_file(self.object)
        except Exception as e:
            logging.exception("Error on processing {}".format(self.object.docfile))
            self.error = str(e) 
            self.fn = self.object.docfile.file.name
            os.remove(self.fn)
            self.object.delete()
            return self.form_invalid(form)
            
        
        return res
        
    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)
        error = getattr(self, 'error', None)
        fn = os.path.basename(getattr(self, 'fn', ''))
        context.update(**locals())
        return context

    def get_success_url(self):
        return reverse_lazy('recipes:check', args=[self.object.id])

        
class CheckView(UpdateView):
    fields = ['title', 'date', 'parsed']
    model = Lesson
    template_name="recipes/check.html"
        
    def form_valid(self, form):
        res = super(CheckView, self).form_valid(form)
        actie = self.request.POST['actie']
        if actie == "remove":
            self.object.delete()
            return redirect('recipes:search')
        if actie == "ok": # redirect to lesson object
            for recipe in get_recipes(self.object):
                recipe.save()
                RecipeIndex().update_object(recipe)
            self.object.status = 5
            self.object.save()
            
            return res
        elif actie == "refresh":
            return self.render_to_response(self.get_context_data())
            
    

    def get_context_data(self, **kwargs):
        context = super(CheckView, self).get_context_data(**kwargs)
        recipes = list(get_recipes(self.object))
        for recipe in recipes:            
            recipe.ingredient_rows = list(row.split("|") for row in recipe.ingredients.splitlines())

        context.update(**locals())
        return context
