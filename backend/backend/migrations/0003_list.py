# Generated by Django 3.1 on 2020-10-16 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_decks'),
    ]

    operations = [
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word_list', models.CharField(max_length=100000)),
            ],
        ),
    ]
