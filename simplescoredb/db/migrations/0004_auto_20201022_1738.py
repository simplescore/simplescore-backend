# Generated by Django 3.1.2 on 2020-10-22 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0003_auto_20201021_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='sha3',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
