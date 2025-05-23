# Generated by Django 5.1.3 on 2025-04-26 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='size',
            field=models.CharField(choices=[('1', '1 kg (Serves 2-4)'), ('1.5', '1.5 kg (Serves 6-8)'), ('2', '2 kg (Serves 10-12)'), ('2.5', '2.5 kg (Serves 12-16)'), ('3', '3 kg (Serves 16-20)'), ('4', '4 kg (Serves 20-28)'), ('5', '5 kg (Serves 28-36)'), ('6', '6 kg (Serves 36-44)'), ('7', '7 kg (Serves 44-52)'), ('8', '8 kg (Serves 52-60)'), ('9', '9 kg (Serves 60-68)'), ('10', '10 kg (Serves 68-76)')], default='1.5', max_length=10),
        ),
    ]
