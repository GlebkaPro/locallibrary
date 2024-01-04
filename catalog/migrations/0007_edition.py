# Generated by Django 4.0.8 on 2023-11-11 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_genre_name_alter_language_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Edition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Название издания', max_length=200)),
                ('publisher', models.CharField(help_text='Издательство', max_length=200)),
                ('publication_date', models.DateField(blank=True, help_text='Дата публикации', null=True)),
            ],
        ),
    ]
