# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-25 15:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_name', models.CharField(max_length=255, unique=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('edit_date', models.DateTimeField(auto_now=True)),
                ('edit_date_in_token', models.CharField(default='None', max_length=30)),
                ('expires', models.BooleanField(default=False)),
                ('expire_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('secret_key', models.CharField(max_length=29, unique=True)),
                ('token', models.CharField(max_length=255)),
                ('token_algo', models.CharField(default='HS256', max_length=10)),
            ],
        ),
    ]
