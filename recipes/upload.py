from rawtext import get_text
from parse_recipes import parse_recipe, get_md
from title import read_dateline
from split_lesson import get_recipes

def process_file(lesson):
    fn = lesson.docfile.file.name
    ok, txt = get_text(fn)
    if not ok:
        raise Exception(txt)
    lesson.raw_text = txt
    title, recipes = parse_recipe(lesson.raw_text)
    lesson.parsed = get_md(recipes)
    lesson.title, lesson.date = read_dateline(title)
    lesson.status=3
    lesson.save()
    
