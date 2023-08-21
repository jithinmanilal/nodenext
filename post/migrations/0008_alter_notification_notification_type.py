# Generated by Django 4.2.3 on 2023-08-09 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0007_post_is_blocked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('like', 'New Like'), ('post', 'New Post'), ('follow', 'New Follow'), ('comment', 'New Comment'), ('blocked', 'Post Blocked')], max_length=20),
        ),
    ]