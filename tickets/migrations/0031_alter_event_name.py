# Generated by Django 4.2 on 2023-04-20 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0030_alter_mainevent_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=500),
        ),
    ]