# Generated by Django 4.2.1 on 2023-05-28 16:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PPTProject', '0008_buyticket'),
    ]

    operations = [
        migrations.RenameField(
            model_name='buyticket',
            old_name='user_id',
            new_name='username',
        ),
    ]