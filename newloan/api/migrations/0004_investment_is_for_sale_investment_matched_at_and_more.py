# Generated by Django 5.2 on 2025-04-18 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_earnings_referral_total_earnings_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='is_for_sale',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='investment',
            name='matched_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='investment',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('matched', 'Matched'), ('sold', 'Sold'), ('matured', 'Matured')], default='available', max_length=20),
        ),
    ]
