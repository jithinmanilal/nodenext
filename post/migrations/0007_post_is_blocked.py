# Generated by Django 4.2.3 on 2023-08-06 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0006_post_reported_by_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]