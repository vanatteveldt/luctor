import re
from collections import defaultdict

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, RedirectView

from recipes.models import Menu, Recipe, MenuRecipe
from recipes.auth import check_share_key, get_share_key


class MenuForm(ModelForm):
    class Meta:
        model = Menu
        fields = ['name']


class MenuDeleteView(RedirectView):
    permanent = False

    def get_redirect_url(self, pk):
        m = Menu.objects.get(pk=pk)
        if not (self.request.user.is_superuser or self.request.user == m.user):
            raise PermissionDenied()
        m.delete()
        return "/"


class MenuRecipeOrderView(RedirectView):
    permanent = False

    def get_redirect_url(self, menu, recipe, direction):
        menu = Menu.objects.get(pk=int(menu))
        items = list(MenuRecipe.objects.filter(menu=menu))
        for i in items:
            print("-", i.recipe.pk, i.order, i.recipe.title)
        print([mr.recipe.pk for mr in items])
        n = [mr.recipe.pk for mr in items].index(int(recipe))
        swap_with = (n - 1) if direction == 'up' else (n + 1)
        items[n], items[swap_with] = items[swap_with], items[n]
        for i, item in enumerate(items):
            item.order = i
            item.save()
            print(i, item.recipe.title)
        return menu.get_absolute_url()


class MenuRecipeRemoveView(RedirectView):
    permanent = False

    def get_redirect_url(self, menu, recipe):
        menu = Menu.objects.get(pk=int(menu))
        recipe = Recipe.objects.get(pk=int(recipe))
        MenuRecipe.objects.get(menu=menu, recipe=recipe).delete()
        return menu.get_absolute_url()


class MenuAddRecipeView(RedirectView):
    def get_redirect_url(self):
        if not 'menu' in self.request.GET and 'recipe' in self.reqest.GET:
            raise Exception("Need a recipe and menu to be able to add one to the other...")
        menu = self.request.GET['menu']
        if menu == -1:
            m = Menu.objects.create(name="<nieuw menu>", user=self.request.user)
        else:
            m = Menu.objects.get(pk=menu)
        r = Recipe.objects.get(pk=self.request.GET['recipe'])
        if MenuRecipe.objects.filter(menu=m, recipe=r).exists():
            self.request.session['add_warning'] = 'Noot: Dit recept zat al in dit menu'
        else:
            self.request.session['add_warning'] = ''
            MenuRecipe.objects.create(menu=m, recipe=r, order=MenuRecipe.objects.filter(menu=m).count()+1)
        return m.get_absolute_url()


class MenuAddView(CreateView):
    model = Menu
    form_class = MenuForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        raise Exception("!!!!")


_PARTS = ("snufje", "teentje", "gram", "eetlepel", "eetl", "dl", "¼", "½", "takje", "stengel")
def parse_ingredient(ing):
    quant = []
    parts = ing.split()
    while parts:
        part = parts.pop(0)
        if re.match(r"^\d+$", part) or part in _PARTS or re.sub("s$", "", part) in _PARTS:
            quant.append(part)
        else:
            return " ".join(quant), " ".join([part] + parts)


class MenuDetailView(UserPassesTestMixin, DetailView):
    model = Menu

    def get(self, *args, **kwargs):
        if 'share' not in self.request.GET and self.request.user.is_authenticated:
            params = self.request.GET.copy()
            params['share'] = get_share_key(self.request.user.id, int(self.kwargs['pk']), is_menu=True)
            url = f"{self.request.path}?{params.urlencode()}"
            return redirect(url)
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ingredients = defaultdict(list)
        context = super().get_context_data(**kwargs)
        self.request.session['current_menu'] = self.object.pk
        warning = self.request.session.get('add_warning')
        self.request.session['add_warning'] = None
        recipes = MenuRecipe.objects.filter(menu=self.object)
        for recipe in recipes:
            recipe.ingredient_rows = list(row.split("|") for row in recipe.recipe.ingredients.splitlines())
            for ingrow in recipe.ingredient_rows:
                for ing in ingrow:
                    if ing.strip():
                        quant, ingredient = parse_ingredient(ing)
                        ingredients[ingredient].append(quant)

            # get share key for recipes
            share_user = self.share_user or self.request.user
            if not share_user.is_authenticated:
                raise Exception("User not authenticated (so why did they get this far?)")
            recipe.share_key = get_share_key(share_user.id, recipe.recipe_id)
        ingredients = sorted((" + ".join(q), i) for (i, q) in ingredients.items())
        context.update(**locals())
        return context

    def test_func(self):
        share = self.request.GET.get('share')
        if share:
            self.share_user = check_share_key(share)
            if not self.share_user:
                return False

        return self.get_object().can_view(self.request.user) or self.get_object().can_view(self.share_user)




