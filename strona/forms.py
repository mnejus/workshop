import datetime

from django import forms
from .models import Kasa, Zamowienia, Kosztorysy
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class KasaForm(forms.ModelForm):

    class Meta:
        model = Kasa
        fields = ('tytul_rozchodu_przychodu', 'kwota_rozchodu_przychodu', 'forma_platnosci', 'rodzaj_platnosci')

class KasaPobranieForm(forms.ModelForm):

    class Meta:
        model = Kasa
        fields = ('kwota_rozchodu_przychodu', )
        
class KasaEditForm(forms.ModelForm):

    class Meta:
        model = Kasa
        fields = ('data_przychodu_rozchodu', 'tytul_rozchodu_przychodu', 'kwota_rozchodu_przychodu', 'forma_platnosci', 'rodzaj_platnosci')

class AutomatyczneDodaniePozycjiKasowejForm(forms.ModelForm):

    class Meta:
        model = Kasa
        fields =()

class ZamowieniaForm(forms.ModelForm):

    class Meta:
        model = Zamowienia
        fields = ('odbiorca', 'nr_katalogowy', 'ilosc', 'forma_platnosci_zam', 'kwota_plat_przy_odbiorze', 'dostawca', 'termin_dostawy', 'wybor_statusu_zam')

class ZamowieniaEditStatusForm(forms.ModelForm):

    class Meta:
        model = Zamowienia
        fields = ('odbiorca', 'nr_katalogowy', 'ilosc', 'forma_platnosci_zam', 'kwota_plat_przy_odbiorze', 'dostawca', 'termin_dostawy', 'wybor_statusu_zam')

class AutomatZmianaFormyPlatnosciForm(forms.ModelForm):

    class Meta:
        model = Zamowienia
        fields = ()

class KosztorysyForm(forms.ModelForm):

    class Meta:
        model = Kosztorysy
        fields = ('nazwa_klienta', 'tel_klienta', 'mail_klienta', 'nr_vin', 'marka_model', 'opis_kosztorysu')

class KosztorysEditForm(forms.ModelForm):

    class Meta:
        model = Kosztorysy
        fields = ('nazwa_klienta', 'tel_klienta', 'mail_klienta', 'nr_vin', 'marka_model', 'opis_kosztorysu', 'status_kosztorysu', 'powod_odrzucenia')


