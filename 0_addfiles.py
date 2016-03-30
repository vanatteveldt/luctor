import sys
import os
import django
django.setup()
from django.core.files import File

from recipes.models import Lesson
dir = sys.argv[1]
exts = set()
for fn in os.listdir(dir):
    if 'groenten' in fn: continue
    base, ext = os.path.splitext(fn)
    exts.add(ext)
    if ext not in ('.odt', '.doc'):
        continue
    base = base.strip()
    if Lesson.objects.filter(filename=base).exists():
        continue
    print(base, ext)
    with open(os.path.join(dir, fn), 'rb') as doc_file:
        l = Lesson.objects.create(filename=base, docfile=File(doc_file))

