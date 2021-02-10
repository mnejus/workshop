# Generated by Django 3.0.5 on 2021-02-02 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('strona', '0005_auto_20210201_2201'),
    ]

    operations = [
        migrations.CreateModel(
            name='Klient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('odbiorca', models.CharField(max_length=200)),
                ('pojazd', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['-odbiorca'],
            },
        ),
        migrations.RemoveField(
            model_name='zamowienia',
            name='odbiorca',
        ),
        migrations.AddField(
            model_name='zamowienia',
            name='klient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='strona.Klient'),
            preserve_default=False,
        ),
    ]
