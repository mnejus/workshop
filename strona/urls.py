from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('kasa/<int:pk>/edit', views.kasa_edit, name='kasa_edit'),
    path('kasa/<int:pk>/pobranie', views.kasa_pobranie, name='kasa_pobranie'),
    path('kasa/', views.kasa_list, name='kasa_list'),
    path('kasa/<int:pk>/delete', views.KasaDelete.as_view(), name='kasa_delete'),
    path('zamowienia/', views.zamowienia_list, name='zamowienia_list'),
    path('zamowienia/<int:pk>/edit', views.zamowienia_edit, name='zamowienia_edit'),
    path('zamowienia/<int:pk>/delete', views.ZamowienieDelete.as_view(), name='zamowienie_delete'),
    path('obroty/', views.obroty_list, name='obroty_list'),
    path('kosztorysy/', views.kosztorysy_list, name='kosztorysy_list'),
    path('kosztorys/<int:pk>/edit', views.kosztorys_edit, name='kosztorys_edit'),
    path('kosztorys/<int:pk>/delete', views.KosztorysDelete.as_view(), name='kosztorys_delete'),
]
