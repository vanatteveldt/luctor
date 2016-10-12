from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, FormView, FormMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import redirect
from django import forms
from django.contrib.auth.models import User
import logging
from recipes.models import Lesson, Recipe, Comment, Like, Picture
from recipes.search_indexes import RecipeIndex
from haystack.generic_views import SearchView
from haystack.forms import HighlightedSearchForm
from django.core.files.base import ContentFile

from haystack.utils import Highlighter
import os
import re
import json
import hashlib
import markdown2
from django.views.generic.base import RedirectView
from .upload import process_file, get_recipes
from PIL import Image
from io import BytesIO
from itertools import islice
from django.conf import settings

def autocomplete_names():
    namen = set()
    for aanwezig in Lesson.objects.exclude(aanwezig__isnull=True).exclude(aanwezig__exact='').values_list("aanwezig", flat=True):
        namen |= {x.strip() for x in aanwezig.split(",")}
    return json.dumps(list(namen))

def recent_user_lessons(user):
    for l in Lesson.objects.order_by('-date'):
        if l.can_view(user):
            yield l
    
def recent_user_comments(user):
    for c in Comment.objects.order_by('-date'):
        if c.recipe.lesson.can_view(user):
            yield c
    
def all_user_recipes(user):
    for l in Lesson.objects.all():
        if l.can_view(user):
            yield from l.recipes.values_list("pk", flat=True)

def get_hash(user_id, lesson_id):
    h = hashlib.sha1()
    h.update(settings.SECRET_KEY.encode("utf-8"))
    h.update(bytes(int(user_id)))
    h.update(bytes(int(lesson_id)))
    return  h.hexdigest()
            
def get_share_key(user_id, lesson_id):
    hash = get_hash(user_id, lesson_id)
    return "{user_id}-{lesson_id}-{hash}".format(**locals())

def check_share_key(key):
    m = re.match(r"(\d+)-(\d+)-(.*)", key)
    if not m:
        return False
    user_id, lesson_id, hash = m.groups()
    check_hash = get_hash(user_id, lesson_id)
    return hash == check_hash

class SearchView(LoginRequiredMixin, SearchView):
    """My custom search view."""

    form_class = HighlightedSearchForm
    
    def get_queryset(self):
        queryset = super(SearchView, self).get_queryset()
        # further filter queryset based on some set of criteria
        if not self.request.user.is_superuser:
            # This is *not* a very nice way to do this...
            ids = list(all_user_recipes(self.request.user))
            queryset = queryset.filter(id__in=ids)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        your_likes = Like.objects.filter(user=self.request.user).order_by('-date')[:10]
        #other_likes = Like.objects.exclude(user=self.request.user).order_by('-date')[:10]
        recent_lessons = islice(recent_user_lessons(self.request.user), 10)
        recent_comments =  islice(recent_user_comments(self.request.user), 10)
        context.update(**locals())
        return context

                                  

class FullTextHighlighter(Highlighter):
    max_length = 20000000
    def highlight(self, text_block):
        self.text_block = strip_tags(text_block)
        highlight_locations = self.find_highlightable_words()
        return self.render_html(highlight_locations, 0, len(text_block))

class ChangeAanwezigView(UpdateView):
    model = Lesson
    fields = ['aanwezig']
    def form_valid(self, form):
        names = form.instance.aanwezig.split(",")
        names = {n.strip().title() for n in names}
        form.instance.aanwezig = ",".join(sorted(names))
        return super(ChangeAanwezigView, self).form_valid(form)

                                  
class LessonView(UserPassesTestMixin, DetailView):

    model = Lesson

    def test_func(self):
        return self.get_object().can_view(self.request.user)

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

        aanwezigform = ChangeAanwezigView().get_form_class()(instance=self.object)
        aanwezig_autocomplete = autocomplete_names()

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

class DeletePictureView(RedirectView):
    permanent = False
    def get_redirect_url(self, pk):
        p = Picture.objects.get(pk=pk)
        if not ( self.request.user.is_superuser or self.request.user == p.user):
            raise PermissionDenied()
        recept = p.recipe
        p.delete()
        return recept.get_absolute_url()
    
    
class LikePictureView(RedirectView):
    permanent = False
    def get_redirect_url(self, pk):
        p = Picture.objects.get(pk=pk)
        p.favourite = not p.favourite
        p.save()
        return p.recipe.get_absolute_url()

def create_thumbnail(inf, size=300):
    im = Image.open(inf)
    im.thumbnail((size,size), Image.ANTIALIAS)
    f = BytesIO()
    im.save(f, format='jpeg')
    bytes = f.getvalue()
    return bytes
        
def save_thumbnail(source_field, destination_field, size=300):
    inf = source_field.file.name
    fn = os.path.splitext(os.path.basename(inf))[0]
    outf = "{fn}-small-{size}.jpg".format(**locals())
    bytes = create_thumbnail(inf, size)
    destination_field.save(outf, ContentFile(bytes))
   
        
class AddPictureView(CreateView):
    model = Picture
    fields = ['image']
        
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.recipe_id = self.kwargs['pk']

        res = super(AddPictureView, self).form_valid(form)
        thumbnails.set_thubmnails(self.object)
        return res
        
    def form_invalid(self, form):
        return redirect(self.get_success_url())
    def get_success_url(self):
        return reverse('recipes:recipe-detail', kwargs=self.kwargs)
    
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'image']
    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        text = cleaned_data.get("text")
        image = cleaned_data.get("image")
        if not (text or image):
            raise forms.ValidationError("No comment or image provided!")

class RecipeView(UserPassesTestMixin, DetailView):
    model = Recipe
    form_class = CommentForm


    def test_func(self):
        share =self.request.GET.get('share')
        if share and check_share_key(share):
            return True
        return self.get_object().lesson.can_view(self.request.user)
    
    def post(self, request, *args, **kwargs):

        form_kwargs = {
            'data': self.request.POST,
            'files': self.request.FILES,
        }
        form = CommentForm(**form_kwargs)
        if form.is_valid():
            form.instance.user = self.request.user
            form.instance.recipe = self.get_object()
            form.save()
        return self.get(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        if 'share' not in self.request.GET and self.request.user.is_authenticated:
            params = self.request.GET.copy()
            params['share'] = get_share_key(self.request.user.id, int(self.kwargs['pk']))
            url = "{}?{}".format(self.request.path, params.urlencode())
            return redirect(url)

        return super().get(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(RecipeView, self).get_context_data(**kwargs)
        recept = context['object']
        can_view_lesson = recept.lesson.can_view(self.request.user)
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

        commentform = CommentForm()
        pictureform = AddPictureView().get_form_class()()
        
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
    fields = ['title', 'date', 'parsed', 'aanwezig']
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

        aanwezig_autocomplete = autocomplete_names()
        context.update(**locals())
        return context

class UserDetailView(UserPassesTestMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.id == self.get_object().id
    
    def form_valid(self, form):
        self.object = form.save()
        return redirect('recipes:user-details', pk=self.object.id)
