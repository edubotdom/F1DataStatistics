#encoding:utf-8
from main.models import Piloto, Escuderia, Nacionalidad, Anyo
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
import urllib.request
import lxml
from datetime import datetime
import re, os, shutil
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from main.forms import BusquedaPorNacionalidadForm, BusquedaPorAnyoForm

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
        nacionalidad_obj, created = Nacionalidad.objects.get_or_create(nombre=nacionalidad)
        
        lista_anyos = anyos_competidos.split(sep=",")
        lista_anyos_obj = []
        for anyo in lista_anyos:
            anyo_obj, created = Anyo.objects.get_or_create(anyo=anyo)
            lista_anyos_obj.append(anyo_obj)
        
        p = Piloto.objects.create(nacionalidad = nacionalidad_obj, nombre = nombre, fechaNacimiento = fechaNacimiento, victorias=victorias, podios=podios, 
                                  poles=poles, campeonatos=campeonatos, temporadas=temporadas, carreras=carreras, puntos=puntos, retiros=retiros)        
        
        #añadimos la lista de anyos
        for a in lista_anyos_obj:
            p.anyos_competidos.add(a)
        
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
            
        nacionalidad_obj, created = Nacionalidad.objects.get_or_create(nombre=nacionalidad)
        
        lista_anyos = anyos_competidos.split(sep=",")
        lista_anyos_obj = []
        for anyo in lista_anyos:
            anyo_obj, created = Anyo.objects.get_or_create(anyo=anyo)
            lista_anyos_obj.append(anyo_obj)
    
            
        e=Escuderia.objects.create(nombre=nombre, 
                                     nacionalidad=nacionalidad_obj,
                                     victorias = victorias,
                                     poles = poles,
                                     temporadas = temporadas,
                                     carreras = carreras,
                                     campeonatos = campeonatos,
                                     puntos = puntos )    
        
        #añadimos la lista de pilotos
        for p in pilotos:
            e.pilotos.add(p)
        
        #añadimos la lista de anyos
        for a in lista_anyos_obj:
            e.anyos_competidos.add(a) 
        
        #Registramos los datos obtenidos en el directorio de Whoosh
        constructors_writer.add_document(nombre=str(nombre),nacionalidad=str(nacionalidad),victorias=str(victorias),poles=str(poles),temporadas=str(temporadas),carreras=str(carreras),campeonatos=str(campeonatos),puntos=str(puntos), anyos_competidos=str(anyos_competidos), pilotos=str(lista_textual_pilotos))
         
        print(nombre)

    constructors_writer.commit()

    
@login_required(login_url='/ingresar')
def cargar_bd(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      

            #borramos todas las tablas de la BD
            #Piloto.objects.all().delete()
            Escuderia.objects.all().delete()

            #Cargamos los datos
            #extraer_pilotos()
            extraer_escuderias()
            return render(request, 'cargar_datos.html')
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')

def ingresar(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/cargar_base_datos')
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        if formulario.is_valid:
            usuario = request.POST['username']
            clave = request.POST['password']
            acceso = authenticate(username=usuario, password=clave)
            if acceso is not None:
                if acceso.is_active:
                    login(request, acceso)
                    return HttpResponseRedirect('/cargar_base_datos')
                else:
                    return render(request, 'noactivo.html')
            else:
                return render(request, 'nousuario.html')
    else:
        formulario = AuthenticationForm()
    context = {'formulario': formulario}
    return render(request, 'ingresar.html', context)

#muestra un listado con los datos de los pilotos
def lista_pilotos(request):
    pilotos=Piloto.objects.all()
    return render(request,'pilotos.html', {'pilotos':pilotos})

#muestra un listado con los datos de las escuderías
def lista_constructores(request):
    escuderias=Escuderia.objects.all()
    return render(request,'escuderias.html', {'escuderias':escuderias})

def buscar_por_nacionalidad(request):
    formulario = BusquedaPorNacionalidadForm()
    pilotos = None
    escuderias = None
    
    if request.method=='POST':
        formulario = BusquedaPorNacionalidadForm(request.POST)      
        if formulario.is_valid():
            nacionalidad=formulario.cleaned_data['nacionalidad']
            
            ix=open_dir("DriversIndex")      
            with ix.searcher() as searcher:
                query = QueryParser("nacionalidad", ix.schema).parse(nacionalidad)
                pilotos_nacionalidad = searcher.search(query, limit=160)
                
                pilotos=[]
                for piloto_nacionalidad in pilotos_nacionalidad:
                    piloto_obj = Piloto.objects.get(nombre=piloto_nacionalidad['nombre'])
                    pilotos.append(piloto_obj)                
             
            ix=open_dir("ConstructorsIndex")      
            with ix.searcher() as searcher:
                query = QueryParser("nacionalidad", ix.schema).parse(nacionalidad)
                constructores_nacionalidad = searcher.search(query, limit=50)  
                
                escuderias=[]
                for constructor_nacionalidad in constructores_nacionalidad:
                    escuderia_obj = Escuderia.objects.get(nombre=constructor_nacionalidad['nombre'])
                    escuderias.append(escuderia_obj) 
    
    print(pilotos)
    print(escuderias)            
    return render(request, 'pilotos_escuderias_por_nacionalidad.html', {'formulario':formulario, 'pilotos':pilotos, 'escuderias':escuderias})

def buscar_por_anyo(request):
    formulario = BusquedaPorAnyoForm()
    pilotos = None
    escuderias = None
    
    if request.method=='POST':
        formulario = BusquedaPorAnyoForm(request.POST)      
        if formulario.is_valid():
            anyo=formulario.cleaned_data['anyo']
            
            ix=open_dir("DriversIndex")      
            with ix.searcher() as searcher:
                query = QueryParser("anyos_competidos", ix.schema).parse(anyo)
                pilotos_anyo = searcher.search(query, limit=100)
                
                pilotos=[]
                for piloto_anyo in pilotos_anyo:
                    piloto_obj = Piloto.objects.get(nombre=piloto_anyo['nombre'])
                    pilotos.append(piloto_obj)                
             
            ix=open_dir("ConstructorsIndex")      
            with ix.searcher() as searcher:
                query = QueryParser("anyos_competidos", ix.schema).parse(anyo)
                constructores_anyo = searcher.search(query, limit=30)  
                
                escuderias=[]
                for constructor_anyo in constructores_anyo:
                    escuderia_obj = Escuderia.objects.get(nombre=constructor_anyo['nombre'])
                    escuderias.append(escuderia_obj) 
    
    print(pilotos)
    print(escuderias)            
    return render(request, 'pilotos_escuderias_por_anyo.html', {'formulario':formulario, 'pilotos':pilotos, 'escuderias':escuderias})


def usuario_nuevo(request):
    if request.method=='POST':
        formulario = UserCreationForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect('/')
    else:
        formulario = UserCreationForm()
    context = {'formulario': formulario}
    return render(request, 'nuevousuario.html', context)

@login_required(login_url='/ingresar')
def cerrar(request):
    logout(request)
    return HttpResponseRedirect('/')

def inicio(request):
    return render(request, 'inicio.html')