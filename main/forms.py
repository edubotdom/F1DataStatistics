#encoding:utf-8
from django import forms
from main.models import Nacionalidad, Anyo
   
class BusquedaPorNacionalidadForm(forms.Form):
    lista=[(g.nombre,g.nombre) for g in Nacionalidad.objects.all()]
    nacionalidad = forms.ChoiceField(label="Seleccione la nacionalidad que desea buscar", choices=lista)
    
class BusquedaPorAnyoForm(forms.Form):
    lista=[(g.anyo,g.anyo) for g in Anyo.objects.all()]
    anyo = forms.ChoiceField(label="Seleccione el año del que desea obtener registros", choices=lista)    

class BusquedaPorNombreForm(forms.Form):
    nombre = forms.CharField(label="Introduzca el nombre del equipo o piloto del que desea obtener información ", required=True)
    
class BusquedaPorMasDestacadosForm(forms.Form):
    opcion = forms.ChoiceField(label="Seleccione la categoría para realizar la selección ", choices=[("Campeonatos", "Campeonatos"), ("Victorias", "Victorias"), ("Poles","Poles"), ("Carreras","Carreras")])
