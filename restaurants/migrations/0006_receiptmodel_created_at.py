# Generated by Django 4.2.4 on 2023-09-01 12:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("restaurants", "0005_remove_receiptmodel_printers"),
    ]

    operations = [
        migrations.AddField(
            model_name="receiptmodel",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
