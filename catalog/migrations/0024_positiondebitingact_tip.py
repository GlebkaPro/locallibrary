# Generated by Django 5.0.1 on 2024-01-10 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0023_remove_debitingact_tip'),
    ]

    operations = [
        migrations.AddField(
            model_name='positiondebitingact',
            name='Tip',
            field=models.CharField(blank=True, choices=[('а', 'Амортизация'), ('с', 'Устаревание'), ('п', 'Повреждение'), ('у', 'Утрата')], default='п', max_length=1, verbose_name='Тип списания'),
        ),
    ]
