# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-26 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0012_user_created_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='event_reminder_time',
            field=models.IntegerField(
                choices=[(0, 'No reminder'), (1, '1 day'), (3, '3 days'),
                         (7, '7 days')], default=1,
                verbose_name='Event Reminder Time'),
        ),
    ]
