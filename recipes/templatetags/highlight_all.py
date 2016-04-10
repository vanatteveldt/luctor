
from haystack.utils import Highlighter
from django import template
from django.utils.html import strip_tags
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

class FullTextHighlighter(Highlighter):
    max_length = 20000000
    def highlight(self, text_block):
        self.text_block = strip_tags(text_block)
        highlight_locations = self.find_highlightable_words()
        return self.render_html(highlight_locations, 0, len(text_block))

def highlight_all(text, query):
    return FullTextHighlighter(query).highlight(text)
    
def highlight_all_filter(text, query):
    return mark_safe(highlight_all(conditional_escape(text), query))

register.filter('highlight_all', highlight_all_filter)
