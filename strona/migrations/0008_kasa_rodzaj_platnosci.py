# Generated by Django 3.0.5 on 2021-02-07 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strona', '0007_auto_20210202_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='kasa',
            name='rodzaj_platnosci',
            field=models.CharField(choices=[('naprawy', 'przychód: naprawy'), ('części', 'przychód: części'), ('inne', 'przychód: inne'), ('podwykonawcy', 'rozchód: podwykonawcy'), ('zakup części', 'rozchód: części'), ('materiały', 'rozchód: materiały'), ('narzędzia/maszyny', 'rozchód: narzędzia/maszyny'), ('rachunki/podatki', 'rozchód: rachunki/podatki'), ('spożywcze', 'rozchód: spożywcze'), ('wynagrodzenie', 'rozchód: wynagrodzenie'), ('myjnia', 'rozchód: myjnia')], default='naprawy', max_length=20),
        ),
    ]