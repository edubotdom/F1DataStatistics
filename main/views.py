#encoding:utf-8
from main.models import Piloto, Escuderia
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
import urllib.request
import lxml
from datetime import datetime
# Create your views here.

def extraer_pilotos():
    #extraemos los datos de la web con BS
    f = urllib.request.urlopen("https://www.racing-statistics.com/en/drivers")
    s = BeautifulSoup(f, "lxml")
    
    lista_link_pilotos = []

    for link in s.find(class_="letterboxes").find_all("a"):
        lista_link_pilotos.append(link.get('href'))

    for piloto in lista_link_pilotos:
        
        f = urllib.request.urlopen(piloto)
        s = BeautifulSoup(f, "lxml")
        
        nacionalidad = s.find("span", itemprop="nationality").string.strip()
        nombre = s.find("h1", itemprop="name").string.strip()
        fechaNacimiento = datetime.strptime(s.find("span", itemprop="birthDate")['datetime'].strip(), '%Y-%m-%d')
        
        s.find("label", text="wins:").find_parent('td').next_sibling.span.decompose()
        victorias = s.find("label", text="wins:").find_parent('td').next_sibling.get_text().strip()
        
        s.find("label", text="podiums:").find_parent('td').next_sibling.span.decompose()
        podios = s.find("label", text="podiums:").find_parent('td').next_sibling.get_text().strip()
        
        s.find("label", text="pole positions:").find_parent('td').next_sibling.span.decompose()
        poles_sin_procesar = s.find("label", text="pole positions:").find_parent('td').next_sibling.get_text().strip()
        if len(poles_sin_procesar)>4:
            poles=1
        else:
            poles = poles_sin_procesar
    
        s.find("label", text="championships:").find_parent('td').next_sibling.span.decompose()
        campeonatos = s.find("label", text="championships:").find_parent('td').next_sibling.get_text().strip()
        
        temporadas = s.find("label", text="seasons:").find_parent('td').next_sibling.get_text().strip()
        
        carreras = s.find("label", text="events:").find_parent('td').next_sibling.get_text().strip()
        
        s.find("label", text="points:").find_parent('td').next_sibling.span.decompose()
        puntos = s.find("label", text="points:").find_parent('td').next_sibling.get_text().strip()
    
        s.find("label", text="retirements:").find_parent('td').next_sibling.span.decompose()
        retiros = s.find("label", text="retirements:").find_parent('td').next_sibling.get_text().strip()
        
        p = Piloto.objects.create(nacionalidad = nacionalidad, nombre = nombre, fechaNacimiento = fechaNacimiento, victorias=victorias, podios=podios, 
                                  poles=poles, campeonatos=campeonatos, temporadas=temporadas, carreras=carreras, puntos=puntos, retiros=retiros)        
    
def extraer_escuderias():
    #extraemos los datos de la web con BS
    f = urllib.request.urlopen("https://www.racing-statistics.com/en/constructors")
    s = BeautifulSoup(f, "lxml")
    
    lista_link_escuderias = []

    for link in s.find(class_="letterboxes").find_all("a"):
        lista_link_escuderias.append(link.get('href'))
    
    for escuderia in lista_link_escuderias:
  
        f = urllib.request.urlopen(escuderia)
        s = BeautifulSoup(f, "lxml")
          
        s.find("label", text="nationality:").find_parent('td').next_sibling.span.decompose()
        nacionalidad = s.find("label", text="nationality:").find_parent('td').next_sibling.get_text().strip()
        nombre = s.find("h1").string.strip()

        temporadas = s.find("label", text="seasons:").find_parent('td').next_sibling.get_text().strip()
        carreras = s.find("label", text="events:").find_parent('td').next_sibling.get_text().strip()
        
        if(s.find("label", text="wins:") != None):
            s.find("label", text="wins:").find_parent('td').next_sibling.span.decompose()
            victorias = s.find("label", text="wins:").find_parent('td').next_sibling.get_text().strip()
        else:
            victorias = 0
        
        if(s.find("label", text="pole positions:") != None):
            s.find("label", text="pole positions:").find_parent('td').next_sibling.span.decompose()
            poles_sin_procesar = s.find("label", text="pole positions:").find_parent('td').next_sibling.get_text().strip()        
            if len(poles_sin_procesar)>4:
                poles=1
            else:
                poles = poles_sin_procesar
        else:
            poles = 0
        
        if(s.find("label", text="constructor championships:") != None):
            s.find("label", text="constructor championships:").find_parent('td').next_sibling.span.decompose()
            campeonatos = s.find("label", text="constructor championships:").find_parent('td').next_sibling.get_text().strip()
        else:
            campeonatos = 0
        
        if(s.find("label", text="points:") != None):
            puntos = s.find("label", text="points:").find_parent('td').next_sibling.get_text().strip()
        else:
            puntos = 0
        
        e = Escuderia.objects.create(nombre=nombre, 
                                     nacionalidad=nacionalidad,
                                     victorias = victorias,
                                     poles = poles,
                                     temporadas = temporadas,
                                     carreras = carreras,
                                     campeonatos = campeonatos,
                                     puntos = puntos )    
        


def cargar_bd(request):
    #borramos todas las tablas de la BD
    Piloto.objects.all().delete()
    Escuderia.objects.all().delete()
    
    #Cargamos los datos
    extraer_pilotos()
    extraer_escuderias()
    return render(request, 'inicio.html')