# Generated by Django 4.1.7 on 2023-04-13 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0029_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainevent',
            name='email',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
