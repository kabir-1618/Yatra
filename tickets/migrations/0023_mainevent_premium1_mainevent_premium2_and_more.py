# Generated by Django 4.1.7 on 2023-03-02 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0022_eventregister_paid_eventregister_pay_there_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainevent',
            name='premium1',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mainevent',
            name='premium2',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mainevent',
            name='premium3',
            field=models.BooleanField(default=False),
        ),
    ]
