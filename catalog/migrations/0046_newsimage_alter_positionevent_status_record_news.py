# Generated by Django 5.0.1 on 2024-05-12 10:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0045_bookinstance_return_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='news_images/', verbose_name='Изображение')),
            ],
        ),
        migrations.AlterField(
            model_name='positionevent',
            name='status_record',
            field=models.CharField(blank=True, choices=[('з', 'записан'), ('н', 'не записан')], default='з', max_length=1, verbose_name='Статус записи'),
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название новости')),
                ('description', models.TextField(verbose_name='Описание')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news', to='catalog.event', verbose_name='Мероприятие')),
                ('images', models.ManyToManyField(blank=True, to='catalog.newsimage', verbose_name='Изображения')),
            ],
        ),
    ]
