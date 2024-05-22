# Generated by Django 5.0.1 on 2024-05-22 15:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0051_author_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_text', models.TextField(verbose_name='Отзыв')),
                ('review_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')),
                ('status_record', models.CharField(blank=True, choices=[('о', 'опубликован'), ('н', 'не опубликован')], default='з', max_length=1, verbose_name='Статус записи')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='catalog.event', verbose_name='Мероприятие')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
