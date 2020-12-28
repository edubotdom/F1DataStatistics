#encoding:utf-8
from main.models import Piloto, Escuderia
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
import urllib.request
import lxml
from datetime import datetime
import re, os, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

def extraer_pilotos():
    #definimos el esquema de la información
    schem = Schema(nombre=KEYWORD(stored=True), nacionalidad=KEYWORD(stored=True,commas=True), fechaNacimiento=DATETIME(stored=True), victorias=NUMERIC, podios=NUMERIC, poles=NUMERIC, campeonatos=NUMERIC, temporadas=NUMERIC, carreras=NUMERIC, puntos=TEXT(stored=True), retiros=NUMERIC, descripcion=TEXT, anyos_competidos=KEYWORD(stored=True,commas=True))
    
    #eliminamos el directorio del índice, si existe
    if os.path.exists("DriversIndex"):
        shutil.rmtree("DriversIndex")
    os.mkdir("DriversIndex")
    
    #creamos el índice
    driver_ix = create_in("DriversIndex", schema=schem)
    #creamos un writer para poder añadir documentos al indice
    driver_writer = driver_ix.writer()

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
        
        enlaces_anyos_competidos = s.find("h2", text="seasons").find_parent('legend').find_parent("fieldset", {"class":"block"}).find_all("a")
        anyos_competidos=""
        for anyo in enlaces_anyos_competidos:
            anyos_competidos = anyos_competidos+anyo.get_text()+","
        
        #Creamos cada uno de los pilotos en la base de datos de Django
        Piloto.objects.create(nacionalidad = nacionalidad, nombre = nombre, fechaNacimiento = fechaNacimiento, victorias=victorias, podios=podios, 
                                  poles=poles, campeonatos=campeonatos, temporadas=temporadas, carreras=carreras, puntos=puntos, retiros=retiros, anyos_competidos=anyos_competidos)        
        
        #Registramos los datos obtenidos en el directorio de Whoosh
        driver_writer.add_document(nombre=str(nombre),nacionalidad=str(nacionalidad),fechaNacimiento=fechaNacimiento,victorias=str(victorias),podios=str(podios),poles=str(poles),campeonatos=str(campeonatos),temporadas=str(temporadas),carreras=str(carreras),puntos=str(puntos),retiros=str(retiros), anyos_competidos=str(anyos_competidos))
        
               
        print(nombre)       
        
    driver_writer.commit()    
        
def extraer_escuderias():
    #definimos el esquema de la información
    schem = Schema(nombre=KEYWORD(stored=True), nacionalidad=KEYWORD(stored=True,commas=True), fechaNacimiento=DATETIME(stored=True), victorias=NUMERIC, poles=NUMERIC, temporadas=NUMERIC, carreras=NUMERIC, campeonatos=NUMERIC, puntos=TEXT(stored=True), anyos_competidos=KEYWORD(stored=True,commas=True), pilotos=KEYWORD(stored=True,commas=True))
    
    #eliminamos el directorio del índice, si existe
    if os.path.exists("ConstructorsIndex"):
        shutil.rmtree("ConstructorsIndex")
    os.mkdir("ConstructorsIndex")
    
    #creamos el índice
    constructors_ix = create_in("ConstructorsIndex", schema=schem)
    #creamos un writer para poder añadir documentos al indice
    constructors_writer = constructors_ix.writer()

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
        
        enlaces_anyos_competidos = s.find("h2", text="seasons").find_parent('legend').find_parent("fieldset", {"class":"block"}).find_all("a")
        anyos_competidos=""
        for anyo in enlaces_anyos_competidos:
            anyos_competidos = anyos_competidos+anyo.get_text()+","
        
        enlaces_pilotos = s.find("h2", text="drivers who drove for "+nombre).find_parent('legend').find_parent("fieldset", {"class":"block"}).find_all("a")
        pilotos=[]
        lista_textual_pilotos=""
        for piloto in enlaces_pilotos:
            lista_textual_pilotos = lista_textual_pilotos+piloto.get_text()+","
            
            piloto_extraido = Piloto.objects.get(nombre=piloto.get_text())
            pilotos.append(piloto_extraido)
            
        e=Escuderia.objects.create(nombre=nombre, 
                                     nacionalidad=nacionalidad,
                                     victorias = victorias,
                                     poles = poles,
                                     temporadas = temporadas,
                                     carreras = carreras,
                                     campeonatos = campeonatos,
                                     puntos = puntos,
                                     anyos_competidos = anyos_competidos )    
        
        #añadimos la lista de pilotos
        for p in pilotos:
            e.pilotos.add(p)
        
        #Registramos los datos obtenidos en el directorio de Whoosh
        constructors_writer.add_document(nombre=str(nombre),nacionalidad=str(nacionalidad),victorias=str(victorias),poles=str(poles),temporadas=str(temporadas),carreras=str(carreras),campeonatos=str(campeonatos),puntos=str(puntos), anyos_competidos=str(anyos_competidos), pilotos=str(lista_textual_pilotos))
         
        print(nombre)
    
    constructors_writer.commit()
    

def cargar_bd(request):
    
    #borramos todas las tablas de la BD
    #Piloto.objects.all().delete()
    Escuderia.objects.all().delete()

    #Cargamos los datos
    #extraer_pilotos()
    extraer_escuderias()

    return render(request, 'inicio.html')