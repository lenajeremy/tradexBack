# Generated by Django 3.1.2 on 2021-07-23 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userAuthentication', '0003_auto_20210723_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cover_picture',
            field=models.TextField(default='https://graphicsfamily.com/wp-content/uploads/2020/10/Abstract-Facebook-Cover-Design-Presentation-scaled.jpg'),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.TextField(default='https://img.icons8.com/bubbles/2x/user-male.png'),
        ),
    ]
