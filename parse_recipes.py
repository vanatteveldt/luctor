import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luctor.settings")
django.setup()

#######################################################
from recipes.models import Lesson
import re, csv

RE_MEASURE = r'[0-9¼½]|gram|\bg\b|\bmg\b|liter|deciliter|\bdl\b|\bl\b|\bcl\b|\bgrote\b|\bkleine\b|\btheel\b|\beetl'
STOP = "van","een","het","met","door","tot","deel","minuten","rasp","voor","fijn","volle","laten","naar","delen","oven","eelt","niet","zoals","heel","erbij","heet","alle","blok"
INGREDIENTS = {x['ingredient'] for x in csv.DictReader(open("data/ingredienten.csv"))} | {"ui", "sla"}

INGREDIENTS -= {'schillen', 'dunne', 'reepjes','klein', 'beetje', 'koken'}

class Recipe(object):
    def __init__(self, title=None, ingredients=None, text=None):
        self.title = title
        self.ingredients = ingredients or []
        self.text = text or []

def get_measures(line):
    words = re.split('\s+', line)
    measures, others = [], []
    for word in words:
        if not word.strip():
            continue
        word = re.sub('\W', '', word)
        if re.search(RE_MEASURE, word) or word.lower() in INGREDIENTS:
            measures.append(word)
        else:
            others.append(word)
    return measures, others

def _isIngredient(line):
    if not line.strip():
        return False
    measures, others = get_measures(line)
    #print(measures, others)
    prop_measures = len(measures) / (len(others) + len(measures))
    
    return prop_measures >= 0.5 or '\t' in line

def isIngredient(lines, i):
    if _isIngredient(lines[i]):
        return True
    if len(lines) > i and i > 0 and _isIngredient(lines[i-1]) and _isIngredient(lines[i+1]):
        return True
    
def parse_recipe(text):
    lines = l.raw_text.split('\n')
    title = None
    recipes = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        if title is None:
            # first line is title
            title = line
        elif not recipes:
            # second line is recipe title
            recipes.append(Recipe(line))
        elif isIngredient(lines, i):
            if recipes[-1].text:
                # this is a new recipe, take title from last line
                title = recipes[-1].text.pop()
                recipes.append(Recipe(title))
            recipes[-1].ingredients.append(line)
        else:
            recipes[-1].text.append(line)
    return title, recipes
        

#print(isIngredient('i eetl. olijfolie per artisjok '))
#import sys;sys.exit()

import sys
lid = int(sys.argv[1])

for l in Lesson.objects.filter(pk=int(sys.argv[1])).all():
    title, recipes = parse_recipe(l)
    print("#", title)
    for recipe in recipes:
        print("\n##", recipe.title, "\n")
        for i in recipe.ingredients:
            i = "|{}|".format(re.sub("\t+", "|", i))
            print(i)
        print()
        for l in recipe.text:
            print(l)
            
