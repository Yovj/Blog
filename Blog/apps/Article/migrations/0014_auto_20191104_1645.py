# Generated by Django 2.2.5 on 2019-11-04 08:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0013_hot_info_view'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='hot_info_view',
            unique_together={('article_id', 'type')},
        ),
    ]
