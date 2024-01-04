# Generated by Django 4.0.8 on 2023-11-11 20:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_edition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edition',
            name='publication_date',
        ),
        migrations.RemoveField(
            model_name='edition',
            name='title',
        ),
        migrations.AddField(
            model_name='bookcopy',
            name='due_back',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bookcopy',
            name='edition',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.edition'),
        ),
    ]
