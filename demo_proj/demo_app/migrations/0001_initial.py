# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-06-30 08:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModelWithCustomPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('can_deliver_pizzas', 'Can deliver pizzas'),),
            },
        ),
        migrations.CreateModel(
            name='ModelWithCustomPermissionsNoDefault',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'default_permissions': (),
                'permissions': (('can_do_stuff', 'Can Do stuff'), ('can_do_more_stuff', 'Can do more stuff')),
            },
        ),
        migrations.CreateModel(
            name='ModelWithDefaultPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ModelWithEditedDefaultPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'default_permissions': ('change',),
            },
        ),
        migrations.CreateModel(
            name='ModelWithNoPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'default_permissions': (),
            },
        ),
    ]
