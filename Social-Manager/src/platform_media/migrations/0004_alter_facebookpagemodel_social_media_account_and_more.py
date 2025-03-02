# Generated by Django 5.1.1 on 2025-03-02 20:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts_connection', '0003_alter_socialmediaaccount_external_account_id'),
        ('platform_media', '0003_alter_facebookpagemodel_social_media_account_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facebookpagemodel',
            name='social_media_account',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='accounts_connection.socialmediaaccount'),
        ),
        migrations.AlterField(
            model_name='facebookusermodel',
            name='social_media_account',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='accounts_connection.socialmediaaccount'),
        ),
    ]
