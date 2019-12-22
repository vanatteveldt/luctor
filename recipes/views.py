import json
import logging
import os
from datetime import datetime
from itertools import islice

import markdown2
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import redirect
from django.utils.html import strip_tags
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from haystack.forms import HighlightedSearchForm
from haystack.generic_views import SearchView
from haystack.utils import Highlighter
from ipware.ip import get_ip

from recipes import thumbnails
from recipes.models import Lesson, Recipe, Comment, Like, Picture, Menu
from recipes.search_indexes import RecipeIndex
from .auth import check_share_key, get_share_key
from .menu import MenuForm
from .upload import process_file, get_recipes

log = logging.getLogger('luctor.views')
_STATUS_NAMES = ("Ruw", "Ruwe tekst", "Titel en datum", "Ongeverifi\xeberd", "Geverifi\xeberd", "Gesplitst")


def autocomplete_names():
    namen = set()
    for aanwezig in (Lesson.objects.exclude(aanwezig__isnull=True).exclude(aanwezig__exact='')
                           .values_list("aanwezig", flat=True)):
        namen |= {x.strip() for x in aanwezig.split(",")}
    return json.dumps(list(namen))


def recent_user_lessons(user):
    for les in Lesson.objects.order_by('-date'):
        if les.can_view(user):
            yield les


def recent_user_comments(user):
    for c in Comment.objects.order_by('-date'):
        if c.recipe.lesson.can_view(user):
            yield c


def all_user_recipes(user):
    for les in Lesson.objects.all():
        if les.can_view(user):
            yield from les.recipes.values_list("pk", flat=True)


class RecipeSearchView(LoginRequiredMixin, SearchView):
    """My custom search view."""

    form_class = HighlightedSearchForm

    def get_queryset(self):
        queryset = super(RecipeSearchView, self).get_queryset()
        # further filter queryset based on some set of criteria
        if not self.request.user.is_superuser:
            # This is *not* a very nice way to do this...
            ids = list(all_user_recipes(self.request.user))
            queryset = queryset.filter(id__in=ids)
        return queryset

    def get_context_data(self, **kwargs):
        if 'toggle_like' in self.request.GET:
            like = Like.objects.get(pk=self.request.GET['toggle_like'])
            like.favorite = not like.favorite
            like.save()

        context = super(RecipeSearchView, self).get_context_data(**kwargs)
        your_likes = Like.objects.filter(user=self.request.user).filter(favorite=True).order_by('-date')[:10]
        your_recent = (Like.objects.filter(user=self.request.user).filter(favorite=False)
                           .order_by('-favorite', '-date')[:10])
        menus = Menu.objects.filter(user=self.request.user).order_by('-date')[:10]
        menu_form = MenuForm()
        # other_likes = Like.objects.exclude(user=self.request.user).order_by('-date')[:10]
        recent_lessons = list(islice(recent_user_lessons(self.request.user), 10))
        # recent_comments =  list(islice(recent_user_comments(self.request.user), 10))
        for les in recent_lessons:
            les.has_picture = les.recipes.filter(pictures__isnull=False).exists()
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
            nles = Lesson.objects.filter(status=3).order_by("?")[0]
            return redirect(nles)
        return super(LessonView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LessonView, self).get_context_data(**kwargs)
        highlight = self.request.GET.get('highlight')
        les = context['object']
        text = les.raw_text
        recipes = les.recipes.all()
        status_name = _STATUS_NAMES[les.status]

        aanwezigform = ChangeAanwezigView().get_form_class()(instance=self.object)
        aanwezig_autocomplete = autocomplete_names()

        ntotal = Lesson.objects.all().count()
        nchecked = Lesson.objects.filter(status=4).count()

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
        les = Lesson.objects.filter(status=3).order_by("?")[0]
        return les.get_absolute_url()


class DeletePictureView(RedirectView):
    permanent = False

    def get_redirect_url(self, pk):
        p = Picture.objects.get(pk=pk)
        if not (self.request.user.is_superuser or self.request.user == p.user):
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


class AddPictureView(CreateView):
    model = Picture
    fields = ['image']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.recipe_id = self.kwargs['pk']

        res = super(AddPictureView, self).form_valid(form)
        thumbnails.set_thumbnails(self.object)
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
        share_key = self.request.GET.get('share')
        if share_key:
            self.share_user = check_share_key(share_key)
            if not self.share_user:
                log.warning(f"Invalid hash: {share_key}")
                return False
        les = self.get_object().lesson
        return les.can_view(self.request.user) or les.can_view(self.share_user)

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

    def _log_recipe_access(self):
        r = Recipe.objects.get(pk=self.kwargs['pk'])
        ip = get_ip(self.request)
        if self.request.user.is_authenticated():
            log.info("[{ip}] USER {self.request.user.username} ACCESS {r.pk}:{r.title}".format(**locals()))
        else:
            share = self.request.GET.get('share')
            share_userid = share.split("-")[0]
            try:
                share_user = User.objects.get(pk=share_userid).username
            except User.DoesNotExist:
                share_user = "?"

            log.info("[{ip}] ANONYMOUS ACCESS SHARED-BY {share_userid}:{share_user} TO {r.pk}:{r.title}"
                     .format(**locals()))

    def get(self, *args, **kwargs):
        if 'share' not in self.request.GET and self.request.user.is_authenticated:
            params = self.request.GET.copy()
            params['share'] = get_share_key(self.request.user.id, int(self.kwargs['pk']))
            url = "{}?{}".format(self.request.path, params.urlencode())
            return redirect(url)
        self._log_recipe_access()
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RecipeView, self).get_context_data(**kwargs)
        recept = context['object']
        can_view_lesson = recept.lesson.can_view(self.request.user)
        if self.request.user.is_authenticated:
            like = self.request.GET.get('like')
            try:
                les = Like.objects.get(recipe=recept, user=self.request.user)
                if like is not None:
                    les.favorite = (like == "1")
                les.date = datetime.now()
                les.save()
            except Like.DoesNotExist:
                les = Like.objects.create(recipe=recept, user=self.request.user, favorite=(like == "1"))
            isliked = les.favorite

        ingredient_rows = list(row.split("|") for row in recept.ingredients.splitlines())
        highlight = self.request.GET.get('highlight')

        # comments = recept.comments.all()
        commentform = CommentForm()
        pictureform = AddPictureView().get_form_class()()

        menus = Menu.objects.filter(user=self.request.user) if self.request.user.is_authenticated else None
        current_menu = self.request.session.get('current_menu', -1)

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
        if actie == "ok":  # redirect to lesson object
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

    def get_object(self, *args, **kargs):
        if 'pk' not in self.kwargs:
            self.kwargs['pk'] = self.request.user.pk
        return super().get_object(*args, **kargs)



