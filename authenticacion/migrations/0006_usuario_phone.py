# Generated by Django 5.1 on 2024-09-23 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticacion', '0005_usuario_verify_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='phone',
            field=models.CharField(blank=True, null=True, unique=True, verbose_name='phone number'),
        ),
    ]
