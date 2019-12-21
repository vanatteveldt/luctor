# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2019-12-21 20:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0021_lesson_aanwezig'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True, db_column='insertdate')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menus', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MenuRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=1)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Menu')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe')),
            ],
        ),
        migrations.AddField(
            model_name='like',
            name='favorite',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='menurecipe',
            unique_together=set([('recipe', 'menu')]),
        ),
    ]
