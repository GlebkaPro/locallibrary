# Generated by Django 5.0.1 on 2024-05-05 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0036_request_reason_alter_bookinstance_current_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookinstance',
            name='status',
            field=models.CharField(blank=True, choices=[('р', 'Выдано'), ('д', 'Продлено'), ('з', 'Зарезервировано'), ('п', 'Погашено'), ('о', 'Просрочено')], default='р', help_text='Доступность книги', max_length=1, verbose_name='Статус'),
        ),
    ]