# Generated by Django 2.2 on 2019-10-11 12:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mygrades', '0004_enrollment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='curriculum',
            options={'ordering': ['grade_level']},
        ),
    ]