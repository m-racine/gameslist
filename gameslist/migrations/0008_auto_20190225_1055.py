# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-25 15:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0007_gameinstance_gametoinstance'),
    ]

    operations = [
        migrations.RenameField('Note', 'text', 'note'),
        migrations.RenameField('AlternateName', 'text', 'name'),
    ]