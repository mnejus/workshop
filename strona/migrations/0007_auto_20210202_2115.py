# Generated by Django 3.0.5 on 2021-02-02 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strona', '0006_auto_20210202_2109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zamowienia',
            name='klient',
        ),
        migrations.AddField(
            model_name='zamowienia',
            name='odbiorca',
            field=models.CharField(default=2, max_length=200),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Klient',
        ),
    ]
