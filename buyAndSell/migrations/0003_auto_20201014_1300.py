# Generated by Django 3.1.2 on 2020-10-14 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buyAndSell', '0002_auto_20201014_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='number',
            field=models.IntegerField(default=98317992, unique=True),
        ),
    ]
