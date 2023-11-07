# Generated by Django 4.2.1 on 2023-11-07 19:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0027_alter_bookinstance_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='middle_name',
            field=models.CharField(max_length=100, null=True, verbose_name='Отчество'),
        ),
        migrations.AddField(
            model_name='bookinstance',
            name='current_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Текущая дата'),
        ),
        migrations.AddField(
            model_name='bookinstance',
            name='renewal_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата возврата'),
        ),
        migrations.AlterField(
            model_name='author',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рождения'),
        ),
        migrations.AlterField(
            model_name='author',
            name='date_of_death',
            field=models.DateField(blank=True, null=True, verbose_name='Дата смерти'),
        ),
        migrations.AlterField(
            model_name='author',
            name='first_name',
            field=models.CharField(max_length=100, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='author',
            name='last_name',
            field=models.CharField(max_length=100, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(help_text='13-значный <a href="https://www.isbn-international.org/content/what-isbn">номер ISBN</a>', max_length=18, unique=True, verbose_name='ISBN'),
        ),
        migrations.AlterField(
            model_name='bookinstance',
            name='book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='catalog.book', verbose_name='Книга'),
        ),
        migrations.AlterField(
            model_name='bookinstance',
            name='borrower',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Заёмщик'),
        ),
        migrations.AlterField(
            model_name='bookinstance',
            name='due_back',
            field=models.DateField(blank=True, null=True, verbose_name='Дата возврата'),
        ),
        migrations.AlterField(
            model_name='bookinstance',
            name='status',
            field=models.CharField(blank=True, choices=[('р', 'Выдано'), ('д', 'Доступно'), ('з', 'Зарезервировано'), ('п', 'Погашено')], default='р', help_text='Доступность книги', max_length=1, verbose_name='Статус'),
        ),
        migrations.CreateModel(
            name='BookCopy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='Уникальный идентификатор для этой конкретной книги во всей библиотеке', primary_key=True, serialize=False)),
                ('imprint', models.CharField(max_length=200, null=True, verbose_name='Штамп')),
                ('status', models.CharField(blank=True, choices=[('р', 'Выдано'), ('д', 'Доступно'), ('з', 'Зарезервировано')], default='д', help_text='Доступность книги', max_length=1, verbose_name='Статус')),
                ('book', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='catalog.book', verbose_name='Книга')),
            ],
        ),
        migrations.AddField(
            model_name='bookinstance',
            name='loan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.bookcopy'),
        ),
    ]
