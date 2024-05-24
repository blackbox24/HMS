# Generated by Django 5.0.6 on 2024-05-24 07:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Patient', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medication', models.CharField(max_length=15, unique=True)),
                ('expiry_date', models.DateTimeField()),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Patient.patient')),
            ],
        ),
    ]
