# Generated by Django 3.1.2 on 2020-10-21 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0002_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='sha3',
            field=models.CharField(max_length=128),
        ),
    ]
