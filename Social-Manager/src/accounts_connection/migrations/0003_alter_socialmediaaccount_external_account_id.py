# Generated by Django 5.1.1 on 2025-03-01 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts_connection', '0002_alter_socialmediaaccount_external_account_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmediaaccount',
            name='external_account_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
