# Generated by Django 3.0.5 on 2021-02-01 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strona', '0004_auto_20210131_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zamowienia',
            name='termin_dostawy',
            field=models.CharField(choices=[('następna trasa', 'następna trasa'), ('dzisiaj po poludniu', 'dzisiaj po poludniu'), ('jutro rano', 'jutro rano'), ('jutro po południu', 'jutro po południu'), ('kilka dni', 'kilka dni')], default='następna trasa', max_length=30),
        ),
    ]