# Generated by Django 5.1 on 2024-09-19 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticacion', '0004_usuario_customer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='verify_email',
            field=models.BooleanField(default=False, verbose_name='verify email'),
        ),
    ]