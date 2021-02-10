from django.db import models
from django.utils import timezone
from django.urls import reverse

class Kasa(models.Model):
	pracownik = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	data_przychodu_rozchodu = models.DateTimeField(default=timezone.now)
	tytul_rozchodu_przychodu = models.CharField(max_length=200)
	kwota_rozchodu_przychodu = models.IntegerField()
	WYBOR_STATUSU = (
		('ok', 'Zaksięgowany'),
		('czeka', 'Niezaksięgowany'),
	)
	status_rozchodu_przychodu = models.CharField(max_length=5, choices=WYBOR_STATUSU, blank=False, default='czeka')
	WYBOR_PLATNOSCI = (
		('kasa', 'do/z kasy'),
		('konto', 'wpłata/wypłata z konta'),
		('inne', 'inne'),
	)
	forma_platnosci = models.CharField(max_length=10, choices=WYBOR_PLATNOSCI, blank=False, default='kasa')
	WYB_RODZ_PLAT = (
		('p: naprawy', 'przychód: naprawy'),
		('p: części', 'przychód: części'),
		('p: inne', 'przychód: inne'),
		('r: podwykonawcy', 'rozchód: podwykonawcy'),
		('r: zakup części', 'rozchód: części'),
		('r: materiały', 'rozchód: materiały'),
		('r: narzędzia/maszyny', 'rozchód: narzędzia/maszyny'),
		('r: rachunki/podatki', 'rozchód: rachunki/podatki'),
		('r: spożywcze', 'rozchód: spożywcze'),
		('r: wynagrodzenie', 'rozchód: wynagrodzenie'),
		('r: myjnia', 'rozchód: myjnia'),
		('pobranie', 'pobranie gotówki'),
		('wpłata', 'wpłata gotówki'),
	)
	rodzaj_platnosci = models.CharField(max_length=20, choices=WYB_RODZ_PLAT, blank=False, default='p: naprawy')
	
	class Meta:
		ordering = ['-data_przychodu_rozchodu']
		
	def get_absolute_url(self):
		return reverse('kasa-detail', args=[str(self.id)])
		
	def __str__(self):
		return f'{self.data_przychodu_rozchodu}, {self.tytul_rozchodu_przychodu}, {self.kwota_rozchodu_przychodu}, {self.pracownik}, {self.status_rozchodu_przychodu}'

class Zamowienia(models.Model):
	pracownik_zam = models.ForeignKey('auth.User', on_delete=models.CASCADE)	
	odbiorca = models.CharField(max_length=200)
	nr_katalogowy = models.CharField(max_length=200)
	ilosc = models.PositiveIntegerField(default=1)
	WYBOR_PLATNOSCI_ZAM = (
		('przelew', 'przelew'),
		('pobranie', 'płatne przy odbiorze'),
		('opłacone', 'opłacone'),
	)
	forma_platnosci_zam = models.CharField(max_length=10, choices=WYBOR_PLATNOSCI_ZAM, blank=False, default='przelew')
	kwota_plat_przy_odbiorze = models.IntegerField(default=0)
	WYBOR_DOSTAWCA = (
		('IC', 'InterCars'),
		('GR', 'Gordon'),
		('AL', 'AutoLand'),
		('APP', 'AutoPartner Płock'),
		('APG', 'Auto-Partner Gdańsk'),
		('AUTKO', 'Autko'),
		('XPartner', 'XPartner'),
		('Allegro', 'Allegro'),
		('CerMotor', 'Cermotor'),
		('Inne', 'Inne'),
	)
	dostawca = models.CharField(max_length=10, choices=WYBOR_DOSTAWCA, blank=False)
	data_zamowienia = models.DateTimeField(default=timezone.now)
	WYBOR_TERMINU = (
		('następna trasa', 'następna trasa'),
		('dzisiaj po poludniu', 'dzisiaj po poludniu'),
		('jutro rano', 'jutro rano'),
		('jutro po południu', 'jutro po południu'),
		('kilka dni', 'kilka dni'),
	)
	termin_dostawy = models.CharField(max_length=30, choices=WYBOR_TERMINU, blank=False, default='następna trasa')
	WYBOR_STATUSU = (
		('czeka', 'czekamy na dostawę'),
		('dostarczony', 'dostarczony'),
		('niedostarczony', 'niedostarczony-korekta'),
		('użyty', 'użyty'),
		('magazyn', 'magazyn'),
		('zwrot', 'zwrot'),
	)
	wybor_statusu_zam = models.CharField(max_length=30, choices=WYBOR_STATUSU, blank=False, default='czeka')

	class Meta:
		ordering = ['-data_zamowienia']
		
	def __str__(self):
		return f'{self.data_zamowienia}, {self.odbiorca}, {self.nr_katalogowy}, {self.wybor_statusu_zam}'

class Kosztorysy(models.Model):
	pracownik = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	data_zgloszenia = models.DateTimeField(default=timezone.now)
	nazwa_klienta = models.CharField(max_length=200)
	tel_klienta = models.CharField(max_length=20, blank=True)
	mail_klienta = models.EmailField(max_length=200, blank=True)
	nr_vin = models.CharField(max_length=17)
	marka_model = models.CharField(max_length=200, blank=True)
	opis_kosztorysu = models.TextField()
	WYBOR_STATUSU = (
		('czeka', 'czeka'),
		('wprowadzony', 'wprowadzony do Integry'),
		('w trakcie', 'w trakcie wyceny'),
		('czeka na sprawdzenie', 'wyceniony - do sprawdzenia'),
		('sprawdzony: OK', 'sprawdzony: OK'),
		('sprawdzony: POPRAWIONY', 'sprawdzony, poprawiony'),
		('wysłany', 'wysłany klientowi'),
		('zatwierdzony, umówiony', 'zatwierdzony, umówiony'),
		('niezaakceptowany', 'niezaakceptowany przez klienta'),
	)
	status_kosztorysu = models.CharField(max_length=30, choices=WYBOR_STATUSU, blank=False, default='czeka')
	powod_odrzucenia = models.TextField(blank=True)

	class Meta:
		ordering = ['-data_zgloszenia']

	def __str__(self):
		return f'{self.data_zgloszenia}, {self.nr_vin}, {self.status_kosztorysu}'

class Obroty(models.Model):
	data_od = models.DateField()
	data_do = models.DateField()
	nazwisko_mech = models.CharField(max_length=100)
	imie_mech = models.CharField(max_length=100)
	obrot_towary = models.IntegerField()
	obrot_uslugi = models.IntegerField()

	class Meta:
		ordering = ['-data_od', '-obrot_uslugi']

	def __str__(self):
		return f'{self.data_od}, {self.data_do}, {self.nazwisko_mech}, {self.obrot_towary}, {self.obrot_uslugi}'