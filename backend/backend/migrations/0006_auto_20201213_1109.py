# Generated by Django 3.1 on 2020-12-13 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_auto_20201213_1102'),
    ]

    operations = [
        migrations.RenameField(
            model_name='decks',
            old_name='userToken',
            new_name='userID',
        ),
        migrations.RenameField(
            model_name='list',
            old_name='userToken',
            new_name='userID',
        ),
    ]
