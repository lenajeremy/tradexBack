# Generated by Django 3.1.2 on 2020-11-05 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buyAndSell', '0002_auto_20201028_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='initialStock',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='account',
            name='number',
            field=models.IntegerField(default=14563710, unique=True),
        ),
    ]