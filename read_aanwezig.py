import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luctor.settings")
django.setup()

from recipes.models import Lesson
import re, csv, sys, datetime

lessons = {}

for line in csv.DictReader(sys.stdin):
    date = datetime.datetime.strptime(line['Datum'], "%Y-%m-%d")
    naam = line['Naam']
    try:
        lesson = Lesson.objects.get(date=date)
    except Lesson.DoesNotExist:
        date = date + datetime.timedelta(days=1)
        lesson = Lesson.objects.get(date=date)
    
    if lesson not in lessons:
        lessons[lesson] = set()

    lessons[lesson].add(naam)

def clean(name):
    name = name.replace(" ", "")
    return name

for lesson, names in lessons.items():
    assert not lesson.aanwezig
    aanwezig = ", ".join(clean(n) for n in names)
    lesson.aanwezig = aanwezig
    lesson.save()
