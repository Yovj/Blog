# Generated by Django 2.2.5 on 2019-10-27 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0009_auto_20191027_1646'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='is_great',
            field=models.BooleanField(default=0),
        ),
    ]
