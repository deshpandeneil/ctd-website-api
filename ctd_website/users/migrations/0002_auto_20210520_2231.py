# Generated by Django 3.2 on 2021-05-20 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='price_for_junior',
        ),
        migrations.RemoveField(
            model_name='event',
            name='price_for_senior',
        ),
    ]