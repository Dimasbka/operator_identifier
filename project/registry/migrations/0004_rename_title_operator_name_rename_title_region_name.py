# Generated by Django 5.0.1 on 2024-02-06 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0003_region_alter_operator_options_alter_range_region'),
    ]

    operations = [
        migrations.RenameField(
            model_name='operator',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='region',
            old_name='title',
            new_name='name',
        ),
    ]
