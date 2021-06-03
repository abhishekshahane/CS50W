# Generated by Django 3.2 on 2021-05-04 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='picture_url',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
