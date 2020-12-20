# Generated by Django 3.1 on 2020-12-16 21:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='error',
            name='related_correction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='errors', to='backend.correction'),
            preserve_default=False,
        ),
    ]
