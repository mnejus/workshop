# Generated by Django 3.0.5 on 2021-02-07 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strona', '0008_kasa_rodzaj_platnosci'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kasa',
            name='rodzaj_platnosci',
            field=models.CharField(choices=[('p: naprawy', 'przychód: naprawy'), ('p: części', 'przychód: części'), ('p: inne', 'przychód: inne'), ('r: podwykonawcy', 'rozchód: podwykonawcy'), ('r: zakup części', 'rozchód: części'), ('r: materiały', 'rozchód: materiały'), ('r: narzędzia/maszyny', 'rozchód: narzędzia/maszyny'), ('r: rachunki/podatki', 'rozchód: rachunki/podatki'), ('r: spożywcze', 'rozchód: spożywcze'), ('r: wynagrodzenie', 'rozchód: wynagrodzenie'), ('r: myjnia', 'rozchód: myjnia')], default='naprawy', max_length=20),
        ),
    ]
