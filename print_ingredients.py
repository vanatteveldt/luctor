import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luctor.settings")
django.setup()

#######################################################
from recipes.models import Lesson
import re

RE_MEASURE = r'[0-9¼½]|gram|\bg\b|\bmg\b|liter|deciliter|\bdl\b|\bl\b|\bcl\b|\bgrote\b|\bkleine\b|\btheel\b|\beetl'
STOP = "van","een","het","met","door","tot","deel","minuten","rasp","voor","fijn","volle","laten","naar","delen","oven","eelt","niet","zoals","heel","erbij","heet","alle","blok",'schillen', 'dunne', 'reepjes','klein', 'beetje', 'koken'

def get_measures(line):
    words = re.split('\s+', line)
    measures, others = [], []
    for word in words:
        word = re.sub('\W', '', word)
        if re.search(RE_MEASURE, word):
            measures.append(word)
        else:
            others.append(word)
    return measures, others

def isIngredient(line):
    measures, others = get_measures(line)
    prop_measures = len(measures) / (len(others) + len(measures))
    return prop_measures > 0.25 or '\t' in line

ingcount = {}

for l in Lesson.objects.all():
    lines = l.raw_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue

        
        if isIngredient(line):
            _, ingredients = get_measures(line)
            for i in ingredients:
                if len(i)> 3 and i.islower() and i not in STOP:
                    ingcount[i] = ingcount.get(i,0) + 1

ingredients = set()
for i, n in sorted(ingcount.items(), key=lambda x:x[1]):
    if n >= 5:
        ingredients.add(i)
        
            
