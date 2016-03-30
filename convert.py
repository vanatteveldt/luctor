import django; django.setup()

import subprocess
from luctor import settings
from recipes.models import Lesson

for l in Lesson.objects.filter(status=0):
    fn = l.docfile.file.file.name
    print(fn)
    cmd = ["antiword", "-f", fn]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode == 0:
        l.status = 1
        l.raw_text = txt
        l.save()
    else:
        l.problems = "{err}".format(**locals())
        l.save()

