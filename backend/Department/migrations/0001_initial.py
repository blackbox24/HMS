# Generated by Django 5.0.6 on 2024-05-24 06:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Hospital', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_name', models.CharField(max_length=30)),
                ('hospital_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Hospital.hospital')),
            ],
        ),
    ]
