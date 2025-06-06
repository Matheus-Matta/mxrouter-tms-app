# Generated by Django 5.2 on 2025-05-06 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tmsapp', '0002_historicalroutearea_areatotal_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalroutearea',
            name='status',
            field=models.CharField(choices=[('active', 'Ativo'), ('disabled', 'Desabilitado')], default='active', help_text='Status da rota', max_length=10),
        ),
        migrations.AddField(
            model_name='routearea',
            name='status',
            field=models.CharField(choices=[('active', 'Ativo'), ('disabled', 'Desabilitado')], default='active', help_text='Status da rota', max_length=10),
        ),
    ]
