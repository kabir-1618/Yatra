# Generated by Django 4.1.7 on 2023-02-28 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0016_mainevent_combo_alter_user_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='PremimumTicket',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=100)),
            ],
        ),
    ]