# Generated by Django 4.0.8 on 2023-12-02 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0014_alter_author_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcceptAct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_date', models.DateField(default=django.utils.timezone.now, verbose_name='Текущая дата')),
                ('summa', models.CharField(max_length=100, verbose_name='Сумма')),
                ('Tip', models.CharField(blank=True, choices=[('д', 'Дарение'), ('ж', 'Пожертвование'), ('п', 'Покупка'), ('о', 'Обмен'), ('н', 'Наследование'), ('з', 'Заимствование')], default='р', max_length=1, verbose_name='Тип поступления')),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='наименование')),
            ],
        ),
        migrations.AlterField(
            model_name='bookcopy',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, help_text='Уникальный идентификатор', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='bookinstance',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, help_text='Уникальный идентификатор', primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='PositionAcceptAct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.CharField(max_length=100, verbose_name='Цена')),
                ('size', models.CharField(max_length=100, verbose_name='Количество')),
                ('AcceptAct', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.acceptact', verbose_name='Акт о приёме')),
                ('copy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.bookcopy', verbose_name='Экземпляр"')),
            ],
        ),
        migrations.CreateModel(
            name='FizPersonSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=100, verbose_name='Фамилия')),
                ('middle_name', models.CharField(max_length=100, null=True, verbose_name='Отчество')),
                ('source', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='catalog.source', verbose_name='Источник')),
            ],
        ),
        migrations.AddField(
            model_name='acceptact',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.fizpersonsource', verbose_name='Источник'),
        ),
        migrations.AddField(
            model_name='acceptact',
            name='worker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Сотрудник'),
        ),
    ]