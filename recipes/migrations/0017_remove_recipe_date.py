# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-12 23:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_recipe_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='date',
        ),
    ]