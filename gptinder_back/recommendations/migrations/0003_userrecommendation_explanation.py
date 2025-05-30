# Generated by Django 5.1.7 on 2025-04-23 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommendations', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrecommendation',
            name='explanation',
            field=models.TextField(blank=True, help_text='Personalized explanation of why these users might be interested in talking to each other', null=True, verbose_name='Explanation'),
        ),
    ]
