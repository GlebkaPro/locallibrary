# Generated by Django 5.0.1 on 2024-05-14 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0050_alter_bookexemplar_bbk_alter_bookexemplar_isbn_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='authors/', verbose_name='Изображение'),
        ),
    ]