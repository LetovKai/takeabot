# Generated by Django 4.2.8 on 2024-01-24 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_email_verify_alter_user_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='autoprice',
            field=models.IntegerField(db_index=True, default=20),
        ),
        migrations.AddField(
            model_name='user',
            name='invoice',
            field=models.IntegerField(db_index=True, default=20),
        ),
    ]