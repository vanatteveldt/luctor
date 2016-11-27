import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luctor.settings")
django.setup()

from recipes.models import Lesson
from django.contrib.auth.models import User
import sys, csv

users = {u.username.lower(): u for u in User.objects.all()}
aanw = {}
for a in Lesson.objects.filter(aanwezig__isnull=False).values_list("aanwezig", flat=True):
    if not a.strip(): continue
    for name in a.split(","):
        name = name.strip().lower()
        aanw[name] = aanw.get(name, 0) + 1

all = users.keys() | aanw.keys()

w = csv.writer(sys.stdout)
w.writerow(["Username", "Aantal_lessen", "Account bestaat?", "Voornaam", "Achternaam", "Email"])
for u in all:
    row = [u, aanw.get(u, 0)]
    if u in users:
        u = users[u]
        row += ["Ja", u.first_name, u.last_name, u.email]
    else:
        row += ["Nee", "", "", ""]
        
    w.writerow(row)
