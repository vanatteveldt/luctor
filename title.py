import django; django.setup()
from recipes.models import Lesson
import re
import datetime
months = ["jan", "feb", "maa", "apr", "mei", "jun" ,"jul", "aug", "sep" ,"okt", "nov", "dec"]

def get_title_line(l):
    for line in l.raw_text.splitlines():
        line = line.strip()
        if line and '[-- Image: Object1 --]' not in line:
            return line
    raise Exception()

def read_dateline(dateline):
    if "\t" in dateline:
        title, date = dateline.split("\t", 1)
    elif "   " in dateline:
        title, date = dateline.split("   ", 1)
    else:
        raise Exception("Could not parse {dateline}".format(**locals()))
    title = title.strip()
    date = date.strip()
    date = read_date(date)
    return title, date
    
def read_date(date):
    date = date.replace("\t", " ")
    match = re.search(r"(\d+) *([a-zA-Z\.]+) *(\d{4})", date)
    if match:
        j, m, d = match.groups()
        m = m.lower().strip()[:3]
        if m not in months:
            raise Exception("Cannot parse month {m} in {date}".format(**locals()))
        m = months.index(m) + 1
        j, d = int(j), int(d)
        return datetime.date(d,m,j)

    match = re.search(r"(\d+)-(\d+)-(\d+)", date)
    if match:
        j, m, d = [int(x) for x in match.groups()]
        
        return datetime.date(d,m,j)
    raise Exception("Format not recognized")

        
for lesson in Lesson.objects.filter(status=1):
    l = get_title_line(lesson)
    try:
        title, date = read_dateline(l)
    except Exception as e:
        lesson.status = 1
        lesson.problems = "Cannot parse date: {date} ({e})".format(**locals())
        lesson.save()
        continue

    lesson.status=2
    lesson.title = title
    lesson.date = date
    lesson.save()
    
    
    #date2 = date.split("-")[-1]
