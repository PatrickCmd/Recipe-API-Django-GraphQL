# Generated by Django 3.1.7 on 2021-03-01 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_recipe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='instructions',
            new_name='description',
        ),
    ]