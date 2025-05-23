# Generated by Django 5.1.3 on 2025-01-08 10:52

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bakery', '0011_newslettersubscription'),
        ('cart', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='newslettersubscription',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('unsubscribed', 'Unsubscribed')], default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status', 'payment_status'], name='bakery_orde_status_d03809_idx'),
        ),
    ]
