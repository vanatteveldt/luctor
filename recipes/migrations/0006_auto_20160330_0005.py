# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_lesson_raw_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='problems',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='lesson',
            name='status',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
