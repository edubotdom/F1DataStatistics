#encoding:utf-8
import shelve, random, lxml, re, os, shutil, urllib.request
from main.models import Piloto, Escuderia, Nacionalidad, Anyo, Votacion
from django.shortcuts import render, redirect, get_object_or_404
from bs4 import BeautifulSoup
from datetime import datetime
from whoosh.query import Every
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from main.forms import BusquedaPorNacionalidadForm, BusquedaPorAnyoForm,\
    BusquedaPorNombreForm, BusquedaPorMasDestacadosForm, BusquedaDePilotoSimilar
from numpy.random.mtrand import randint
from main.recommendations import  transformPrefs, calculateSimilarItems, getRecommendations, getRecommendedItems, topMatches


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

def listar_mejores(request):
    formulario = BusquedaPorMasDestacadosForm()
    pilotos = None
    escuderias = None
    
    if request.method=='POST':
        formulario = BusquedaPorMasDestacadosForm(request.POST)      
        if formulario.is_valid():
            opcion=formulario.cleaned_data['opcion']
            
            if opcion=="Campeonatos":        
                ix=open_dir("DriversIndex")      
                with ix.searcher() as searcher:
                    query = Every()
                    pilotos_seleccionados = searcher.search(query, limit=10, sortedby="campeonatos", reverse=True)
                    
                    pilotos=[]
                    for piloto_seleccionado in pilotos_seleccionados:
                        piloto_obj = Piloto.objects.get(nombre=piloto_seleccionado['nombre'])
                        pilotos.append(piloto_obj)                
                 
                ix=open_dir("ConstructorsIndex")      
                with ix.searcher() as searcher:
                    query = Every()
                    constructores_seleccionados = searcher.search(query, limit=10, sortedby="campeonatos", reverse=True)
                     
                    escuderias=[]
                    for constructor_seleccionado in constructores_seleccionados:
                        escuderia_obj = Escuderia.objects.get(nombre=constructor_seleccionado['nombre'])
                        escuderias.append(escuderia_obj) 
                
            elif opcion=="Victorias":
                ix=open_dir("DriversIndex")      
                with ix.searcher() as searcher:
                    query = Every()
                    pilotos_seleccionados = searcher.search(query, limit=10, sortedby="victorias", reverse=True)
                    
                    pilotos=[]
                    for piloto_seleccionado in pilotos_seleccionados:
                        piloto_obj = Piloto.objects.get(nombre=piloto_seleccionado['nombre'])
                        pilotos.append(piloto_obj)                
                 
                ix=open_dir("ConstructorsIndex")      
                with ix.searcher() as searcher:
                    query = Every()
                    constructores_seleccionados = searcher.search(query, limit=10, sortedby="victorias", reverse=True)
                     
                    escuderias=[]
                    for constructor_seleccionado in constructores_seleccionados:
                        escuderia_obj = Escuderia.objects.get(nombre=constructor_seleccionado['nombre'])
                        escuderias.append(escuderia_obj) 
            elif opcion=="Poles":
                ix=open_dir("DriversIndex")      
                with ix.searcher() as searcher:
                    query = Every()
                    pilotos_seleccionados = searcher.search(query, limit=10, sortedby="poles", reverse=True)
                    
                    pilotos=[]
                    for piloto_seleccionado in pilotos_seleccionados:
                        piloto_obj = Piloto.objects.get(nombre=piloto_seleccionado['nombre'])
                        pilotos.append(piloto_obj)                
                 
                ix=open_dir("ConstructorsIndex")      
                with ix.searcher() as searcher:
                    query = Every()
                    constructores_seleccionados = searcher.search(query, limit=10, sortedby="poles", reverse=True)
                     
                    escuderias=[]
                    for constructor_seleccionado in constructores_seleccionados:
                        escuderia_obj = Escuderia.objects.get(nombre=constructor_seleccionado['nombre'])
                        escuderias.append(escuderia_obj) 
            elif opcion=="Carreras":
                ix=open_dir("DriversIndex")      
                with ix.searcher() as searcher:
                    query = Every()
                    pilotos_seleccionados = searcher.search(query, limit=10, sortedby="carreras", reverse=True)
                    
                    pilotos=[]
                    for piloto_seleccionado in pilotos_seleccionados:
                        piloto_obj = Piloto.objects.get(nombre=piloto_seleccionado['nombre'])
                        pilotos.append(piloto_obj)                
                 
                ix=open_dir("ConstructorsIndex")      
                with ix.searcher() as searcher:
                    query = Every()
                    constructores_seleccionados = searcher.search(query, limit=10, sortedby="carreras", reverse=True)
                     
                    escuderias=[]
                    for constructor_seleccionado in constructores_seleccionados:
                        escuderia_obj = Escuderia.objects.get(nombre=constructor_seleccionado['nombre'])
                        escuderias.append(escuderia_obj)             
           
    return render(request, 'top_pilotos_escuderias.html', {'formulario':formulario, 'pilotos':pilotos, 'escuderias':escuderias})


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
                
    return render(request, 'pilotos_escuderias_por_anyo.html', {'formulario':formulario, 'pilotos':pilotos, 'escuderias':escuderias})

def buscar_por_nombre(request):
    formulario = BusquedaPorNombreForm()
    pilotos = None
    escuderias = None
    
    if request.method=='POST':
        formulario = BusquedaPorNombreForm(request.POST)      
        if formulario.is_valid():
            nombre=formulario.cleaned_data['nombre']
            
            ix=open_dir("DriversIndex")      
            with ix.searcher() as searcher:
                query = QueryParser("nombre", ix.schema).parse(nombre)
                pilotos_nombre = searcher.search(query, limit=100)
                
                pilotos=[]
                for piloto_nombre in pilotos_nombre:
                    piloto_obj = Piloto.objects.get(nombre=piloto_nombre['nombre'])
                    pilotos.append(piloto_obj)                
             
            ix=open_dir("ConstructorsIndex")      
            with ix.searcher() as searcher:
                query = QueryParser("nombre", ix.schema).parse(nombre)
                constructores_nombre= searcher.search(query, limit=30)  
                
                escuderias=[]
                for constructor_nombre in constructores_nombre:
                    escuderia_obj = Escuderia.objects.get(nombre=constructor_nombre['nombre'])
                    escuderias.append(escuderia_obj) 
               
    return render(request, 'pilotos_escuderias_por_nombre.html', {'formulario':formulario, 'pilotos':pilotos, 'escuderias':escuderias})


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
    num_pilotos=Piloto.objects.all().count()
    num_escuderias=Escuderia.objects.all().count()
    return render(request,'inicio.html', {'num_pilotos':num_pilotos, 'num_escuderias':num_escuderias})

@login_required(login_url='/ingresar')
def loadRS(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            gen_votaciones_piloto()
            populateVotaciones()
            loadDict()
            return render(request, 'cargar_datos.html')
        else:
            return redirect("/")

    return render(request,'confirmacion_loadRS.html')

def pilotoSimilar(request):
    piloto = None
    if request.method=='POST':
        form = BusquedaDePilotoSimilar(request.POST)
        if form.is_valid():
            idPiloto = form.cleaned_data['id']
            piloto = get_object_or_404(Piloto, id=idPiloto)
            shelf = shelve.open("votacionesPilotosRS.dat")
            ItemsPrefs = shelf['ItemsPrefs']
            shelf.close()
            recommended = topMatches(ItemsPrefs, int(idPiloto),n=3)
            pilotos = []
            similar = []
            for re in recommended:
                pilotos.append(Piloto.objects.get(pk=re[1]))
                similar.append(re[0])
            items= zip(pilotos,similar)
            print(items)
            return render(request,'buscar_piloto_similar.html', {'piloto': piloto,'pilotos': items, 'formulario': form})
    form = BusquedaDePilotoSimilar()
    return render(request,'buscar_piloto_similar.html', {'formulario': form})

def gen_votaciones_piloto():
    iteraciones = 5000
    votos_por_persona = 15
    path="voting_data"    
    f = open(path+"\\votaciones_piloto.txt", "w")
    """
    for i in range(0,iteraciones):
        puntuacion_piloto = str(randint(0,5))
        usuario_random = "user"+ str(randint(100))
        id_min=Piloto.objects.all().order_by("id")[0].id
        id_max= Piloto.objects.all().order_by("-id")[0].id
        piloto_random = Piloto.objects.get(id=randint(id_min,id_max)).id
        
        f.write(usuario_random + "-" + str(piloto_random) + "-" + puntuacion_piloto + "\n")
    
    f.close()
    """
    id_min=Piloto.objects.all().order_by("id")[0].id
    id_max= Piloto.objects.all().order_by("-id")[0].id
    
    id_nac_min=Nacionalidad.objects.all().order_by("id")[0].id
    id_nac_max= Nacionalidad.objects.all().order_by("-id")[0].id
    
    for i in range(0,iteraciones):
        usuario_random = "user"+ str(i)
        nacionalidad = Nacionalidad.objects.get(id=randint(id_nac_min,id_nac_max)).id
        
        for i2 in range(0, votos_por_persona):
            piloto_random = Piloto.objects.get(id=randint(id_min,id_max))
            piloto_random_id = piloto_random.id
            pesos = [1,1,1,1,1,1]
            if(piloto_random.nacionalidad.id == nacionalidad):
                for i in range(1,5):
                    pesos[i] = pesos[i]*(i+0.5)
                
            if(piloto_random.campeonatos > 1):
                for i in range(1,5):
                    pesos[i] = pesos[i]*(i+1)
            
            if(piloto_random.carreras > 50):
                for i in range(1,5):
                    pesos[i] = pesos[i]*(i+0.5)

            if(piloto_random.victorias > 20):
                for i in range(1,5):
                    pesos[i] = pesos[i]*(i+0.75)

            puntuacion_piloto = random.choices([0,1,2,3,4,5], pesos, k=1)[0]
            #puntuacion_piloto = str(randint(0,5))
            
            f.write(usuario_random + "-" + str(piloto_random_id) + "-" + str(puntuacion_piloto) + "\n")
    
    f.close()
    
def populateVotaciones():
    Votacion.objects.all().delete()
    path="voting_data"
    lista=[]
    fileobj=open(path+"\\votaciones_piloto.txt", "r")
    for line in fileobj.readlines():
        rip = line.split('-')
        lista.append(Votacion(votante=rip[0].strip(), piloto=Piloto.objects.get(id=int(rip[1].strip())), puntuacion=int(rip[2].strip()) ))
    fileobj.close()
    Votacion.objects.bulk_create(lista)
    
# Funcion que carga en el diccionario Prefs todas las puntuaciones de usuarios a pilotos. Tambien carga el diccionario inverso y la matriz de similitud entre items
# Serializa los resultados en votacionesPilotosRS.dat
def loadDict():
    Prefs={}   # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("votacionesPilotosRS.dat")
    votaciones = Votacion.objects.all()
    for vo in votaciones:
        votante = str(vo.votante)
        piloto = int(vo.piloto.id)
        puntuacion = float(vo.puntuacion)
        Prefs.setdefault(votante, {})
        Prefs[votante][piloto] = puntuacion
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf['SimItems']=calculateSimilarItems(Prefs, n=10)
    shelf.close()
        
    