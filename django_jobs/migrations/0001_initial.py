# Generated by Django 3.2 on 2021-04-16 12:04

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('date', models.DateField(default=datetime.date.today)),
                ('link', models.URLField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_jobs.company')),
            ],
            options={
                'verbose_name_plural': 'Jobs',
            },
        ),
    ]
