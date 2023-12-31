# Generated by Django 4.0.8 on 2023-12-26 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0015_acceptact_source_alter_bookcopy_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='positionacceptact',
            name='AcceptAct',
        ),
        migrations.AddField(
            model_name='positionacceptact',
            name='accept_act',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='position_accept_acts', to='catalog.acceptact', verbose_name='Акт о приёме'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='positionacceptact',
            name='copy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.bookcopy', verbose_name='Экземпляр'),
        ),
    ]
