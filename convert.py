import lxml.html
from lxml.cssselect import CSSSelector
import re

def strip(s):
    return re.sub("\s+", " ", s).strip()

def get_dagtitel(paras):
    
    while True:
        p = paras.pop(0)
        text = p.text_content()
        if text.strip():
            return strip(text)

def is_titel(para):
    if para.cssselect("u"):
        text = "".join([u.text_content().strip() for u in para.cssselect("u")])
        if text:
            return True
        
    if para.tag.lower() == 'h1': return True
    if para.tag.lower() == 'h2': return True

    
def get_recepten(paras):
    while paras:
        titel = get_titel(paras)
        recipe = list(get_recipe(paras))
        while not recipe[-1].strip(): recipe = recipe[:-1]
        
        yield titel, recipe
        
        skip_empties(paras)

def skip_empties(paras):
    while paras and not paras[0].text_content().strip():
        paras.pop(0)
    
        
def get_titel(paras):
    while True:
        p = paras.pop(0)
        text = strip(p.text_content())
        if is_titel(p):
            return strip(text)
        elif text:
            raise Exception("Expected title, got: {text!r}".format(**locals()))      
        
def get_recipe(paras):
    skip_empties(paras)
    result = []
    while paras and (not result or not is_titel(paras[0])):
        p = paras.pop(0)
        result.append(strip(p.text_content()))
    return result


        
def read_html(fn):
    e = lxml.html.parse(open(fn))
    sel = CSSSelector('h1, h2, h3, h4, p')
    paras = list(sel(e))

    dagtitel = get_dagtitel(paras)
    recepten = list(get_recepten(paras))

    print "**",dagtitel,"**\n\n"
    for titel, recept in recepten:
        print u"*{titel}*\n{recept}\n\n".format(**locals())

    
        
if __name__ == '__main__':
    import sys
    read_html(sys.argv[1])
