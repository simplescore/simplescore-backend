# Generated by Django 3.1.2 on 2020-10-23 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0007_auto_20201023_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='artist',
            field=models.CharField(db_column='song_artist', max_length=100),
        ),
        migrations.AlterField(
            model_name='song',
            name='title',
            field=models.CharField(db_column='song_title', max_length=100),
        ),
    ]
