# Generated by Django 3.2 on 2024-02-04 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_ingredients_ingredient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(db_index=True, max_length=200, unique=True, verbose_name='Название'),
        ),
    ]