# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20160329_2213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='date',
        ),
        migrations.AlterField(
            model_name='lesson',
            name='docfile',
            field=models.FileField(upload_to=''),
            preserve_default=True,
        ),
    ]
