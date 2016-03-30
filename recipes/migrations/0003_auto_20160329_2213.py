# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20141111_1140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lesson',
            old_name='title',
            new_name='filename',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='text',
        ),
    ]
