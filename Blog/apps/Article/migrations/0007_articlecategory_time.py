# Generated by Django 2.2.5 on 2019-10-27 08:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0006_auto_20191027_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlecategory',
            name='time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
