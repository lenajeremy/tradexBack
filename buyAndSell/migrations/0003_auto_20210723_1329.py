# Generated by Django 3.1.2 on 2021-07-23 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buyAndSell', '0002_auto_20210719_0333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='number',
            field=models.IntegerField(default=35788424, unique=True),
        ),
    ]