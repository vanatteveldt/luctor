from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.conf import settings

from recipes.models import Lesson

import tempfile
import subprocess
import os
import re
from recipes import readdate
from django.core.files import File

def index(request):
    pietje = "bla"
    return render(request, "index.html", locals())


class UploadForm(forms.Form):
    file = forms.FileField()

class LessonForm(forms.ModelForm):
    filename = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = Lesson
        exclude = ["docfile"]
         
def upload(request):
    if request.method == 'POST':
        # is het een valide lessonform?
        lform = LessonForm(request.POST)
        if lform.is_valid():
            # copy tempfile naar media root
            fn = lform.cleaned_data["filename"]
            dest = os.path.join(settings.MEDIA_ROOT, os.path.basename(fn))
            os.rename(fn, dest)
            
            # lesson aanmaken!
            lesson = lform.save(commit=False)
            lesson.docfile = dest
            lesson.save()
            print ">>>", os.path.basename(lesson.docfile)
            return 

        # is het een valide uploadform?
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            filename, title, date, text = parse_file(form.cleaned_data['file'])

            lform = LessonForm(dict(filename = filename, title = title, date=date, text=text))
            lform.is_valid()
            
            return render(request, "upload_check.html", locals())
    else:
        form = UploadForm()
    return render(request, "upload.html", locals())

def antiword(f):
    # assume f is in memory uplaoded
    tmpd = tempfile.mkdtemp()
    tmpf = os.path.join(tmpd, f.name)
    open(tmpf, 'wb').write(f.read())
    try:
        return tmpf, subprocess.check_output(["antiword", tmpf])
    except:
        text = subprocess.check_output(["unoconv", "--import=utf8",  "--format=text", "--stdout", tmpf])
        return tmpf, text

def parse_file(f):
    fname, txt = antiword(f)
    lines = txt.split("\n")
    print lines
    header = [l for l in lines if l.strip()][0]
    m = re.match(r"(.*?) {2,}(\d.*)$", header)
    if m:
        title, dates = m.groups() 
        date = readdate.read_date(dates)
    else:
        title, date = header, None
    

    return fname, title, date, txt
