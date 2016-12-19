import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luctor.settings")
django.setup()

#######################################################
from recipes.models import Lesson
import re, csv

RE_MEASURE = r'[0-9¼½¾]|gram|\bg\b|\bcup\b|\bmg\b|liter|deciliter|\bdl\b|\bl\b|\bcl\b|\bgrote\b|\bkleine\b|\btheel\b|\beetl'
STOP = "van","een","het","met","door","tot","deel","minuten","rasp","voor","fijn","volle","laten","naar","delen","oven","eelt","niet","zoals","heel","erbij","heet","alle","blok"
WW = {'maak', 'maken', 'snij', 'snijd', 'snijden', 'koken', 'bak', 'bakken', 'laat', 'laten', 'hak', 'hakken', 'vermeng', 'vermengen', 'doe', 'doen', 'breng', 'brengen', 'bestrooi', 'bestrooien', 'meng', 'mengen'}
INGREDIENTS = {x['ingredient'] for x in csv.DictReader(open("data/ingredienten.csv"))} | {"ui", "sla", "kip"}
INGREDIENTS -= {'schillen', 'dunne', 'reepjes','klein', 'beetje', 'koken', 'salade', 'gerookte', 'maken', 'bakken', 'koude', 'zoetzure', 'chinese', 'geroerbakte', 'zoete', 'gefrituurde', 'geroosterd', 'snijden'}
INGREDIENTS -= WW

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

def _isIngredient(line, debug=False, half_is_ok=False):
    if not line.strip():
        return False
    measures, others = get_measures(line)
    if debug: print(measures, others)
    ntab = line.count("\t")
    prop_measures = len(measures) / (len(others) + len(measures))

    if half_is_ok:
        return prop_measures >= 0.5 or ntab >= 1
    else:
        # first line, extra strict!
        if any(w.lower() in WW for w in others):
            return prop_measures >= 0.75 or ntab >2
        return prop_measures > 0.5 or ntab > 1
    
    return prop_measures > 0.5 or (half_is_ok and prop_measures==0.5) or ntab > 1

def isIngredient(lines, i, in_ingredient=False):
    if len(lines[i]) > 200:
        return False
    prev = len(lines) > 1 and lines[i-1].strip()
    if not prev:
        prev = len(lines) > 2 and lines[i-2].strip()
    if prev and (not _isIngredient(prev)) and len(prev) > 100:
        return False
    if len(lines) > i and i > 0 and not lines[i-1].strip() and not lines[i+1].strip():
        return False
    if _isIngredient(lines[i], half_is_ok=in_ingredient):
        return True
    if len(lines) > i and i > 0 and _isIngredient(lines[i-1]) and _isIngredient(lines[i+1]):
        return True
    
def parse_recipe(text):
    text = text.replace("|", "").replace("#", "")
    lines = text.split('\n')
    title = None
    recipes = []
    for i, line in enumerate(lines):
        in_ingredients = bool(recipes and not recipes[-1].text)
        line = line.replace("\ufeff", "").strip()
        if not line: continue
        if title is None:
            # first line is title
            title = line
        elif not recipes:
            # second line is recipe title
            recipes.append(Recipe(line))
        elif isIngredient(lines, i, in_ingredients):
            if recipes[-1].text:
                # this is a new recipe, take title from last line
                receptitle = recipes[-1].text.pop()
                recipes.append(Recipe(receptitle))
            recipes[-1].ingredients.append(line)
        else:
            recipes[-1].text.append(line)
    return title, recipes
        

def get_md(recipes):
    res = []
    for recipe in recipes:
        res.append("\n## {recipe.title}\n".format(**locals()))
        for i in recipe.ingredients:
            i = "| {} |".format(re.sub("\t+", " | ", i))
            res.append(i)
        res.append("")
        for l in recipe.text:
            res.append(l)
    return "\n".join(res)

def metadata_md(lesson):
    return "---\nTitle: {lesson.title}\nDate: {lesson.date}\n---\n".format(**locals())

    
if __name__ == '__main__':
    import sys

    try:
        if len(sys.argv)>1:
            lid = int(sys.argv[1])
        else:
            lid = None
    except:
        print(_isIngredient(' '.join(sys.argv[1:]), debug=True))
        import sys
        sys.exit()

    lessons = Lesson.objects.filter(status=3)
    if lid:
        lessons = lessons.filter(pk=lid)

    for lesson in lessons:
        #for l in Lesson.objects.filter(pk=int(sys.argv[1])).all():

        txt = lesson.raw_text
        title, recipes = parse_recipe(txt)
        md = metadata_md(lesson) + get_md(recipes)
        if lid:
            print( md)
        else:
            lesson.parsed = md
            lesson.problems = len(recipes)
            lesson.status = 3
            lesson.save()

