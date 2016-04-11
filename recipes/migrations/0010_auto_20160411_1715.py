# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-11 17:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0009_auto_20160410_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='likes',
            field=models.ManyToManyField(related_name='liked_recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='recipes.Lesson'),
        ),
    ]
