# Generated by Django 5.0.1 on 2024-04-13 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0034_alter_positionevent_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookinstance',
            name='status',
            field=models.CharField(blank=True, choices=[('р', 'Выдано'), ('д', 'Продлено'), ('з', 'Зарезервировано'), ('п', 'Погашено')], default='р', help_text='Доступность книги', max_length=1, verbose_name='Статус'),
        ),
    ]
