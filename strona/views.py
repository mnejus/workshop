import datetime
#import RPi.GPIO as GPIO
import time

from django.shortcuts import render, redirect, get_object_or_404
from .models import Kasa, Zamowienia, Kosztorysy, Obroty
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from .forms import KasaForm, KasaEditForm, KasaPobranieForm, ZamowieniaForm, KosztorysyForm
from .forms import KosztorysEditForm, ZamowieniaEditStatusForm, AutomatZmianaFormyPlatnosciForm, AutomatyczneDodaniePozycjiKasowejForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from django.contrib import messages

#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#kasaRelay = 13
#GPIO.setup(kasaRelay, GPIO.OUT) 


@login_required
def index(request):
    return render(request, 'index.html', {})

@login_required
def kasa_list(request):
    form = KasaForm()
    pozycje = Kasa.objects.all()
    suma_kasa = Kasa.objects.filter(forma_platnosci__contains='kasa').aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
    zam_pobr = Zamowienia.objects.filter(forma_platnosci_zam__exact='pobranie')
    liczba_zamowien_pobraniowych = Zamowienia.objects.filter(forma_platnosci_zam__exact='pobranie').count()

    if 'platnosc' in request.POST:
        if request.method == "POST":
            form = KasaForm(request.POST)
            if form.is_valid():
                kasa = form.save(commit=False)
                kasa.pracownik = request.user
                kasa.data_przychodu_rozchodu = timezone.now()
                kasa.save()
#                GPIO.output(kasaRelay, GPIO.HIGH)
#                time.sleep(1.0)
#                GPIO.output(kasaRelay, GPIO.LOW)
                return redirect('kasa_list')
            else:
                form = KasaForm()

#    elif 'otworz_kase' in request.POST:
#	    if request.method == "POST":
#		    GPIO.output(kasaRelay, GPIO.HIGH)
#		    time.sleep(1.0)
#		    GPIO.output(kasaRelay, GPIO.LOW)
	
    
    return render(request, 'kasa.html', {'pozycje':pozycje, 'form':form, 'suma_kasa':suma_kasa, 'zam_pobr':zam_pobr, 'liczba_zamowien_pobraniowych':liczba_zamowien_pobraniowych, })

@login_required
def kosztorysy_list(request):
	form = KosztorysyForm()
	kosztorysy = Kosztorysy.objects.all()

	if 'nowy_kosztorys' in request.POST:
		if request.method == "POST":
			form = KosztorysyForm(request.POST)
			if form.is_valid():
				kosztorys = form.save(commit=False)
				kosztorys.pracownik = request.user
				kosztorys.data_zgloszenia = timezone.now()
				kosztorys.save()
				return redirect('kosztorysy_list')
			else:
				form = KosztorysyForm
	
	context = {
		'form':form,
		'kosztorysy':kosztorysy,
	}
	
	return render(request, 'kosztorysy.html', context)

@login_required
def kasa_pobranie(request, pk):
	zamowienie = get_object_or_404(Zamowienia, pk=pk)
	form = KasaPobranieForm()
	form2 = AutomatZmianaFormyPlatnosciForm()

	if request.method == 'POST':
		form = KasaPobranieForm(request.POST)
		form2 = AutomatZmianaFormyPlatnosciForm(request.POST, instance=zamowienie)
		if (form.is_valid()) & (form2.is_valid()):
			kasa = form.save(commit=False)
			kasa.pracownik = request.user
			kasa.data_przychodu_rozchodu = timezone.now()
			kasa.tytul_rozchodu_przychodu = zamowienie.nr_katalogowy
			kasa.save()
			zamowienie = form2.save(commit=False)
			zamowienie.pracownik_zam = request.user
			zamowienie.data_zamowienia = zamowienie.data_zamowienia
			zamowienie.forma_platnosci_zam = "opłacone"
			zamowienie.save()
			return redirect('kasa_list')
		else:
			form = KasaPobranieForm()
			form2 = AutomatZmianaFormyPlatnosciForm(request.POST, instance=zamowienie)
	
	context = {
		'zamowienie': zamowienie,
		'form': form,
		'form2': form2,
	}

	return render(request, 'kasa_pobrania.html', context)

@login_required
def kasa_edit(request, pk):
    kasa = get_object_or_404(Kasa, pk=pk)
    form = KasaEditForm()

    if request.method == 'POST':
	    form = KasaEditForm(request.POST, instance=kasa)
	
	    if form.is_valid():
		    kasa = form.save(commit=False)
		    kasa.pracownik = request.user
		    kasa.data_przychodu_rozchodu = kasa.data_przychodu_rozchodu
		    kasa.save()
		    return redirect('kasa_list')
    else:
	    form = KasaEditForm(instance=kasa)

    context = {
		'kasa':kasa,
		'form':form,
    }
		    
    return render(request, 'kasa_detail.html', {'form':form,})

class KasaDelete(LoginRequiredMixin, DeleteView):
    model = Kasa
    template_name = 'kasa_confirm_delete.html'
    success_url = reverse_lazy('kasa_list')

@login_required
def kosztorys_edit(request, pk):
	kosztorys = get_object_or_404(Kosztorysy, pk=pk)
	form = KosztorysEditForm()

	if request.method == 'POST':
		form = KosztorysEditForm(request.POST, instance=kosztorys)
		if form.is_valid():
			kosztorys = form.save(commit=False)
			kosztorys.pracownik = request.user
			kosztorys.data_zgloszenia = kosztorys.data_zgloszenia
			kosztorys.save()
			if (kosztorys.status_kosztorysu == 'niezaakceptowany') & (kosztorys.powod_odrzucenia == ''):	
				return redirect('kosztorys_edit', pk=kosztorys.pk)
			else:
				return redirect('kosztorysy_list')
	else:
		form = KosztorysEditForm(instance=kosztorys)

	context = {
		'kosztorys':kosztorys,
		'form':form,
	}

	return render(request, 'kosztorys_detail.html', context)

class KosztorysDelete(LoginRequiredMixin, DeleteView):
    model = Kosztorysy
    template_name = 'kosztorys_confirm_delete.html'
    success_url = reverse_lazy('kosztorysy_list')

@login_required
def zamowienia_list(request):
	liczba_zamowien_niedostarczonych = Zamowienia.objects.filter(wybor_statusu_zam__exact='czeka').count()
	zamowienia_all = Zamowienia.objects.all()
	form_zam = ZamowieniaForm()
	wybor_sortowania = ''
	zakres_dat = ''
	jutro = timezone.now().date() + datetime.timedelta(days=1)

	if 'dodawanie_zamowienia' in request.POST:
		if request.method == "POST":
			form = ZamowieniaForm(request.POST)
			form2 = AutomatyczneDodaniePozycjiKasowejForm(request.POST)
			if form.is_valid():
				zamowienia = form.save(commit=False)
				zamowienia.pracownik_zam = request.user
				zamowienia.data_zamowienia = timezone.now()
				zamowienia.save()
				if (zamowienia.forma_platnosci_zam == "opłacone") & (form2.is_valid()):
					kasa = form2.save(commit=False)
					kasa.pracownik = request.user
					kasa.data_przychodu_rozchodu = timezone.now()
					kasa.tytul_rozchodu_przychodu = zamowienia.odbiorca + " (" + zamowienia.nr_katalogowy + ")"
					kasa.kwota_rozchodu_przychodu = zamowienia.kwota_plat_przy_odbiorze
					kasa.forma_platnosci = "konto"
					kasa.save()
				return redirect('zamowienia_list')
			else:
				form = ZamowieniaForm()
		
    
	elif 'sortowanie' in request.POST:    
		if request.method == "POST":
			wybor_sortowania = request.POST['wybor_sort']
			zakres_dat = request.POST['zakres_dat']
			if (wybor_sortowania != '') & (zakres_dat != ''):
				zamowienia_all = Zamowienia.objects.filter(data_zamowienia__range=[zakres_dat, jutro]).order_by(wybor_sortowania)
			elif (wybor_sortowania != '') & (zakres_dat == ''):
				zamowienia_all = Zamowienia.objects.all().order_by(wybor_sortowania)
			elif (wybor_sortowania == '') & (zakres_dat != ''):
				zamowienia_all = Zamowienia.objects.filter(data_zamowienia__range=[zakres_dat, jutro])

	elif 'odbiorca' in request.POST:
		if request.method == "POST":
			wybor_odbiorcy = request.POST['wybor_odbiorca']

	context = {
		'zamowienia_all':zamowienia_all,
		'form_zam':form_zam, 
		'liczba_zamowien_niedostarczonych':liczba_zamowien_niedostarczonych, 
		'wybor_sortowania':wybor_sortowania,
		'zakres_dat':zakres_dat,
    }

    
	return render(request, 'zamowienia.html', context)


@login_required
def zamowienia_edit(request, pk):
	zamowienia = get_object_or_404(Zamowienia, pk=pk)
	form = ZamowieniaEditStatusForm()

	if request.method == 'POST':
		form = ZamowieniaEditStatusForm(request.POST, instance=zamowienia)

		if form.is_valid():
			zamowienia = form.save(commit=False)
			zamowienia.pracownik_zam = request.user
			zamowienia.data_zamowienia = zamowienia.data_zamowienia
			zamowienia.save()
			return redirect('zamowienia_list')
	else:
		form = ZamowieniaEditStatusForm(instance=zamowienia)

	return render(request, 'zamowienia_edit.html', {'form':form,})

class ZamowienieDelete(LoginRequiredMixin, DeleteView):
    model = Zamowienia
    template_name = 'zamowienie_confirm_delete.html'
    success_url = reverse_lazy('zamowienia_list')

@login_required
def obroty_list(request):
	data_od = ''
	data_do = ''
	jutro = timezone.now().date() + datetime.timedelta(days=1)
	today = datetime.date.today()
	obrot_towary = Obroty.objects.filter(data_od__year=today.year, data_od__month=today.month).aggregate(Sum('obrot_towary')).get('obrot_towary__sum', 0.00)
	obrot_uslugi = Obroty.objects.filter(data_od__year=today.year, data_od__month=today.month).aggregate(Sum('obrot_uslugi')).get('obrot_uslugi__sum', 0.00)
	obroty = Obroty.objects.filter(data_od__year=today.year, data_od__month=today.month)
	miesiac = today
	biezacy_rok = str(datetime.date.today().year) #zamiana integer na string, żeby można było połączyć z myślnikami
	biezacy_miesiac = str(datetime.date.today().month)
	month_start = biezacy_rok + '-' + biezacy_miesiac + '-' + '01'
	#obliczenie średniej sprzedaży usług w danym miesiącu (suma wszystkich mechaników / (wszystkich mechaników - kierownik))
	liczba_mech_miesiac = Obroty.objects.filter(data_od__year=today.year, data_od__month=today.month).count()
	if liczba_mech_miesiac == 1:
		sredni_obrot_uslugi = obrot_uslugi / (liczba_mech_miesiac)
	elif liczba_mech_miesiac >= 1:	
		sredni_obrot_uslugi = obrot_uslugi / (liczba_mech_miesiac - 1)
	else:
		sredni_obrot_uslugi = ''

	#domyślnie w module obroty będzie wyświetlane zestawienie z bieżącego miesiąca
	sum_przychod_naprawy = Kasa.objects.filter(rodzaj_platnosci__contains='p: naprawy').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_przychod_naprawy == None:
		sum_przychod_naprawy = 0
	sum_przychod_czesci = Kasa.objects.filter(rodzaj_platnosci__contains='p: części').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_przychod_czesci == None:
		sum_przychod_czesci = 0
	sum_przychod_inne = Kasa.objects.filter(rodzaj_platnosci__contains='p: inne').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_przychod_inne == None:
		sum_przychod_inne = 0
	sum_rozchod_podwykonawcy = Kasa.objects.filter(rodzaj_platnosci__contains='r: podwykonawcy').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_rozchod_podwykonawcy == None:
		sum_rozchod_podwykonawcy = 0
	sum_rozchod_czesci = Kasa.objects.filter(rodzaj_platnosci__contains='r: zakup części').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_rozchod_czesci == None:
		sum_rozchod_czesci = 0
	sum_rozchod_materialy = Kasa.objects.filter(rodzaj_platnosci__contains='r: materiały').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_rozchod_materialy == None:
		sum_rozchod_materialy = 0
	sum_rozchod_narzedzia = Kasa.objects.filter(rodzaj_platnosci__contains='r: narzędzia/maszyny').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_rozchod_narzedzia == None:
		sum_rozchod_narzedzia = 0
	sum_rozchod_rachunki = Kasa.objects.filter(rodzaj_platnosci__contains='r: rachunki/podatki').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_rozchod_rachunki == None:
		sum_rozchod_rachunki = 0
	sum_rozchod_spozywcze = Kasa.objects.filter(rodzaj_platnosci__contains='r: spożywcze').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_rozchod_spozywcze == None:
		sum_rozchod_spozywcze = 0
	sum_rozchod_myjnia = Kasa.objects.filter(rodzaj_platnosci__contains='r: myjnia').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_rozchod_myjnia == None:
		sum_rozchod_myjnia = 0
	sum_rozchod_wynagrodzenie = Kasa.objects.filter(rodzaj_platnosci__contains='r: wynagrodzenie').filter(data_przychodu_rozchodu__range=[month_start, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
	if sum_rozchod_wynagrodzenie == None:
		sum_rozchod_wynagrodzenie = 0

	sum_przychod = sum_przychod_naprawy + sum_przychod_czesci + sum_przychod_inne
	sum_rozchod = sum_rozchod_podwykonawcy + sum_rozchod_czesci + sum_rozchod_materialy + sum_rozchod_narzedzia + sum_rozchod_rachunki + sum_rozchod_spozywcze + sum_rozchod_myjnia + sum_rozchod_wynagrodzenie
	dochod = sum_przychod + sum_rozchod

	if 'filtr' in request.POST:
		if request.method == 'POST': 
			data_od = request.POST['data_od']
			data_do = request.POST['data_do']
			if (data_od == '') & (data_do == ''):
				pass
			elif (data_od != '') & (data_do == ''):
				data_od = str(data_od) + '-01' #z formularza pobieramy miesiac i rok (format: 2021-01), musimy dodać pierwszy dzień miesiąca
				sum_przychod_naprawy = Kasa.objects.filter(rodzaj_platnosci__contains='p: naprawy').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_przychod_naprawy == None:
					sum_przychod_naprawy = 0
				sum_przychod_czesci = Kasa.objects.filter(rodzaj_platnosci__contains='p: części').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_przychod_czesci == None:
					sum_przychod_czesci = 0
				sum_przychod_inne = Kasa.objects.filter(rodzaj_platnosci__contains='p: inne').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_przychod_inne == None:
					sum_przychod_inne = 0
				sum_rozchod_podwykonawcy = Kasa.objects.filter(rodzaj_platnosci__contains='r: podwykonawcy').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_podwykonawcy == None:
					sum_rozchod_podwykonawcy = 0
				sum_rozchod_czesci = Kasa.objects.filter(rodzaj_platnosci__contains='r: zakup części').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_czesci == None:
					sum_rozchod_czesci = 0
				sum_rozchod_materialy = Kasa.objects.filter(rodzaj_platnosci__contains='r: materiały').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_materialy == None:
					sum_rozchod_materialy = 0
				sum_rozchod_narzedzia = Kasa.objects.filter(rodzaj_platnosci__contains='r: narzędzia/maszyny').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_narzedzia == None:
					sum_rozchod_narzedzia = 0
				sum_rozchod_rachunki = Kasa.objects.filter(rodzaj_platnosci__contains='r: rachunki/podatki').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_rachunki == None:
					sum_rozchod_rachunki = 0
				sum_rozchod_spozywcze = Kasa.objects.filter(rodzaj_platnosci__contains='r: spożywcze').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_spozywcze == None:
					sum_rozchod_spozywcze = 0
				sum_rozchod_myjnia = Kasa.objects.filter(rodzaj_platnosci__contains='r: myjnia').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_myjnia == None:
					sum_rozchod_myjnia = 0
				sum_rozchod_wynagrodzenie = Kasa.objects.filter(rodzaj_platnosci__contains='r: wynagrodzenie').filter(data_przychodu_rozchodu__range=[data_od, jutro]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_wynagrodzenie == None:
					sum_rozchod_wynagrodzenie = 0
				sum_przychod = sum_przychod_naprawy + sum_przychod_czesci + sum_przychod_inne
				sum_rozchod = sum_rozchod_podwykonawcy + sum_rozchod_czesci + sum_rozchod_materialy + sum_rozchod_narzedzia + sum_rozchod_rachunki + sum_rozchod_spozywcze + sum_rozchod_myjnia + sum_rozchod_wynagrodzenie
				dochod = sum_przychod + sum_rozchod
			elif (data_od == '') & (data_do != ''): 
				data_od = "2010-01-01" 
				data_do = str(data_do) #zamieniam format daty 2021-01 na ciąg znaków
				data_do_rok = int(data_do[0:4]) #wyodrebniam rok i zmieniam na typ integer
				data_do_miesiac = int(data_do[5:7]) #wyodrebniam miesiac i zmieniam typ
				#jeśli z formularza wybierzemy zakres do danego miesiąca, to bierzemy pod uwagę ostatni dzień wybranego miesiąca
				if data_do_miesiac == 12: #nie ma 13 miesiaca, więc od razu pobieram styczeń i zmieniam rok na następny
					data_do_miesiac = 1
					data_do_rok = data_do_rok + 1
				else: 
					data_do_miesiac = data_do_miesiac + 1 #zwiększam miesiąc o jeden
				#pobieram ostatni dzień miesiąca cofając się o jeden dzień z miesiąca następnego (jeśli wybraliśmy zakres do końca lutego, to zamieniam na 1.03, cofam się o jeden dzień i wychodzi mi ost dzień lutego)
				data_do = datetime.date(data_do_rok, data_do_miesiac, 1) - datetime.timedelta(days=1)
				
				sum_przychod_naprawy = Kasa.objects.filter(rodzaj_platnosci__contains='p: naprawy').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_przychod_naprawy == None:
					sum_przychod_naprawy = 0
				sum_przychod_czesci = Kasa.objects.filter(rodzaj_platnosci__contains='p: części').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_przychod_czesci == None:
					sum_przychod_czesci = 0
				sum_przychod_inne = Kasa.objects.filter(rodzaj_platnosci__contains='p: inne').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_przychod_inne == None:
					sum_przychod_inne = 0
				sum_rozchod_podwykonawcy = Kasa.objects.filter(rodzaj_platnosci__contains='r: podwykonawcy').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_podwykonawcy == None:
					sum_rozchod_podwykonawcy = 0
				sum_rozchod_czesci = Kasa.objects.filter(rodzaj_platnosci__contains='r: zakup części').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_czesci == None:
					sum_rozchod_czesci = 0
				sum_rozchod_materialy = Kasa.objects.filter(rodzaj_platnosci__contains='r: materiały').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_materialy == None:
					sum_rozchod_materialy = 0
				sum_rozchod_narzedzia = Kasa.objects.filter(rodzaj_platnosci__contains='r: narzędzia/maszyny').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_narzedzia == None:
					sum_rozchod_narzedzia = 0
				sum_rozchod_rachunki = Kasa.objects.filter(rodzaj_platnosci__contains='r: rachunki/podatki').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_rachunki == None:
					sum_rozchod_rachunki = 0
				sum_rozchod_spozywcze = Kasa.objects.filter(rodzaj_platnosci__contains='r: spożywcze').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_spozywcze == None:
					sum_rozchod_spozywcze = 0
				sum_rozchod_myjnia = Kasa.objects.filter(rodzaj_platnosci__contains='r: myjnia').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_myjnia == None:
					sum_rozchod_myjnia = 0
				sum_rozchod_wynagrodzenie = Kasa.objects.filter(rodzaj_platnosci__contains='r: wynagrodzenie').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_wynagrodzenie == None:
					sum_rozchod_wynagrodzenie = 0
				sum_przychod = sum_przychod_naprawy + sum_przychod_czesci + sum_przychod_inne
				sum_rozchod = sum_rozchod_podwykonawcy + sum_rozchod_czesci + sum_rozchod_materialy + sum_rozchod_narzedzia + sum_rozchod_rachunki + sum_rozchod_spozywcze + sum_rozchod_myjnia + sum_rozchod_wynagrodzenie
				dochod = sum_przychod + sum_rozchod
				data_od = ''
			elif (data_od != '') & (data_do != ''):
				data_od = str(data_od) + '-01' #z formularza pobieramy miesiac i rok (format: 2021-01), musimy dodać pierwszy dzień miesiąca
				data_do = str(data_do) #zamieniam format daty 2021-01 na ciąg znaków
				data_do_rok = int(data_do[0:4]) #wyodrebniam rok i zmieniam na typ integer
				data_do_miesiac = int(data_do[5:7]) #wyodrebniam miesiac i zmieniam typ
				#jeśli wybierzemy zakres od np styczeń 2021 do styczeń 2021, to pobierzemy dane od 01.01.2021 - 31.01.2021
				if data_do_miesiac == 12: #nie ma 13 miesiaca, więc od razu pobieram styczeń i zmieniam rok na następny
					data_do_miesiac = 1
					data_do_rok = data_do_rok + 1
				else: 
					data_do_miesiac = data_do_miesiac + 1 #zwiększam miesiąc o jeden
				#pobieram ostatni dzień miesiąca cofając się o jeden dzień z miesiąca następnego (jeśli wybraliśmy zakres do końca lutego, to zamieniam na 1.03, cofam się o jeden dzień i wychodzi mi ost dzień lutego)
				data_do = datetime.date(data_do_rok, data_do_miesiac, 1) - datetime.timedelta(days=1)
				
				if data_od == data_do:
					data_od = str(data_od) + '-01'
				sum_przychod_naprawy = Kasa.objects.filter(rodzaj_platnosci__contains='p: naprawy').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_przychod_naprawy == None:
					sum_przychod_naprawy = 0
				sum_przychod_czesci = Kasa.objects.filter(rodzaj_platnosci__contains='p: części').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_przychod_czesci == None:
					sum_przychod_czesci = 0
				sum_przychod_inne = Kasa.objects.filter(rodzaj_platnosci__contains='p: inne').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_przychod_inne == None:
					sum_przychod_inne = 0
				sum_rozchod_podwykonawcy = Kasa.objects.filter(rodzaj_platnosci__contains='r: podwykonawcy').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_podwykonawcy == None:
					sum_rozchod_podwykonawcy = 0
				sum_rozchod_czesci = Kasa.objects.filter(rodzaj_platnosci__contains='r: zakup części').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_czesci == None:
					sum_rozchod_czesci = 0
				sum_rozchod_materialy = Kasa.objects.filter(rodzaj_platnosci__contains='r: materiały').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_materialy == None:
					sum_rozchod_materialy = 0
				sum_rozchod_narzedzia = Kasa.objects.filter(rodzaj_platnosci__contains='r: narzędzia/maszyny').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_narzedzia == None:
					sum_rozchod_narzedzia = 0
				sum_rozchod_rachunki = Kasa.objects.filter(rodzaj_platnosci__contains='r: rachunki/podatki').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_rachunki == None:
					sum_rozchod_rachunki = 0
				sum_rozchod_spozywcze = Kasa.objects.filter(rodzaj_platnosci__contains='r: spożywcze').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_spozywcze == None:
					sum_rozchod_spozywcze = 0
				sum_rozchod_myjnia = Kasa.objects.filter(rodzaj_platnosci__contains='r: myjnia').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_myjnia == None:
					sum_rozchod_myjnia = 0
				sum_rozchod_wynagrodzenie = Kasa.objects.filter(rodzaj_platnosci__contains='r: wynagrodzenie').filter(data_przychodu_rozchodu__range=[data_od, data_do]).aggregate(Sum('kwota_rozchodu_przychodu')).get('kwota_rozchodu_przychodu__sum', 0.00)
				if sum_rozchod_wynagrodzenie == None:
					sum_rozchod_wynagrodzenie = 0
				sum_przychod = sum_przychod_naprawy + sum_przychod_czesci + sum_przychod_inne
				sum_rozchod = sum_rozchod_podwykonawcy + sum_rozchod_czesci + sum_rozchod_materialy + sum_rozchod_narzedzia + sum_rozchod_rachunki + sum_rozchod_spozywcze + sum_rozchod_myjnia + sum_rozchod_wynagrodzenie
				dochod = sum_przychod + sum_rozchod


	if 'filtr_obroty' in request.POST:
		if request.method == 'POST':
			miesiac = request.POST['miesiac']
			year = miesiac[0:4]
			month = miesiac[6:7]
			if miesiac != '':
				obrot_towary = Obroty.objects.filter(data_od__year=year, data_od__month=month).aggregate(Sum('obrot_towary')).get('obrot_towary__sum', 0.00)
				obrot_uslugi = Obroty.objects.filter(data_od__year=year, data_od__month=month).aggregate(Sum('obrot_uslugi')).get('obrot_uslugi__sum', 0.00)
				obroty = Obroty.objects.filter(data_od__year=year, data_od__month=month)
				liczba_mech_miesiac = Obroty.objects.filter(data_od__year=year, data_od__month=month).count()
				if liczba_mech_miesiac == 1:
					sredni_obrot_uslugi = obrot_uslugi / (liczba_mech_miesiac)
				elif liczba_mech_miesiac >= 1:
					sredni_obrot_uslugi = obrot_uslugi / (liczba_mech_miesiac - 1)
				else:
					sredni_obrot_uslugi = ''
			else:
				pass

	context = {
		'sum_przychod_naprawy':sum_przychod_naprawy,
		'sum_przychod_czesci':sum_przychod_czesci,
		'sum_przychod_inne':sum_przychod_inne,
		'sum_rozchod_podwykonawcy':sum_rozchod_podwykonawcy,
		'sum_rozchod_czesci':sum_rozchod_czesci,
		'sum_rozchod_materialy':sum_rozchod_materialy,
		'sum_rozchod_narzedzia':sum_rozchod_narzedzia,
		'sum_rozchod_rachunki':sum_rozchod_rachunki,
		'sum_rozchod_spozywcze':sum_rozchod_spozywcze,
		'sum_rozchod_myjnia':sum_rozchod_myjnia,
		'sum_rozchod_wynagrodzenie':sum_rozchod_wynagrodzenie,
		'sum_przychod':sum_przychod,
		'sum_rozchod':sum_rozchod,
		'dochod':dochod,
		'data_od':data_od,
		'data_do':data_do,
		'obroty':obroty,
		'obrot_towary':obrot_towary,
		'obrot_uslugi':obrot_uslugi,
		'miesiac':miesiac,
		'today':today,
		'liczba_mech_miesiac':liczba_mech_miesiac,
		'sredni_obrot_uslugi':sredni_obrot_uslugi,
	}

	if 'csv' in request.POST:
		if request.method == "GET":
			return render(request, 'obroty.html', context)

		csv_file = request.FILES['file']

		if not csv_file.name.endswith('.csv'):
			messages.error(request, 'Wyślij plik z rozszerzeniem csv')

		tekst = csv_file.read().decode('ISO-8859–2')

		#wyrzucenie zbędnych znaków z tekstu
		tekst = tekst.replace(";", "")
		cudzy = "\""
		tekst = tekst.replace(cudzy,"")

		#wyodrębnienie zakresu dat
		data_od_csv = tekst.find("Zakres dat:  od ")
		data_od_csv = tekst[data_od_csv+16:data_od_csv+26]
		data_do_csv = tekst.find("Zakres dat:  od ")
		data_do_csv = tekst[data_do_csv+30:data_do_csv+40]

		#wyodrębnienie nazwiska i imienia mechanika
		poz_nazw_start = tekst.find("Nazwisko:")
		poz_nazw_end = tekst.find("Prowizja towary")
		nazwisko = tekst[poz_nazw_start+9:poz_nazw_end]   
		poz_imie_start = tekst.find("Imię:")
		poz_imie_end = tekst.find("Prowizja usługi")
		imie = tekst[poz_imie_start+5:poz_imie_end]

		#wyodbrębnienie sprzedaży netto Towarów i Usług
		poczatek = tekst.find("Obrót (wg udziałów serwisantów)Prowizja %Prowizja") #znalezienie linii z podsumowaniem sprzedaży
		podsumowanie = tekst[poczatek:]
		podsumowanie = podsumowanie.splitlines() #oddzielenie poszczególnych linii tekstu
		podsum_towary = podsumowanie[2] #wybranie linii, w której mamy podsumowanie sprzedaży towarów
		podsum_uslugi = podsumowanie[3] #wybranie linii, w której mamy podsumowanie sprzedaży usług
		podsum_towary_end = podsum_towary.find(",") #znalezienie pierwszego przecinka w danej linii
		podsum_usulgi_end = podsum_uslugi.find(",") #j.w.
		towary_netto = podsum_towary[7:podsum_towary_end] #wyodbrebnienie kwoty całkowitej do przecinka
		uslugi_netto = podsum_uslugi[7:podsum_usulgi_end] #j.w.
	
		Obroty.objects.update_or_create(
			data_od = data_od_csv,
			data_do = data_do_csv,
			nazwisko_mech = nazwisko,
			imie_mech = imie,
			obrot_towary = towary_netto,
			obrot_uslugi = uslugi_netto,
		)

	return render(request, 'obroty.html', context)