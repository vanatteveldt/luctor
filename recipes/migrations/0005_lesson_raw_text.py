# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20160329_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='raw_text',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
