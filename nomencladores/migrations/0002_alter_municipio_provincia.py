# Generated by Django 5.1 on 2024-09-23 06:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nomencladores', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='municipio',
            name='provincia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='municipios', to='nomencladores.provincia'),
        ),
    ]
