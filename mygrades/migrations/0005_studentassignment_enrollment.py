# Generated by Django 2.2 on 2019-11-08 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mygrades', '0004_auto_20191108_0537'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentassignment',
            name='enrollment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mygrades.Enrollment'),
        ),
    ]
