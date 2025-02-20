#encoding:utf-8
from django.db import models

# Create your models here.
class Nacionalidad(models.Model):
    nombre = models.CharField(max_length=30,verbose_name='Nombre de la nacionalidad')
    
    def __str__(self):
        return self.nombre

class Anyo(models.Model):
    anyo = models.CharField(max_length=5,verbose_name='Años competidos en la categoría')
    
    def __str__(self):
        return self.anyo
    
class Piloto(models.Model):
    nombre = models.TextField(verbose_name='Nombre')
    nacionalidad = models.ForeignKey(Nacionalidad,on_delete=models.SET_NULL, null=True,verbose_name='Nombre de la nacionalidad')
    fechaNacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    victorias = models.IntegerField(verbose_name='Número de victorias')
    podios = models.IntegerField(verbose_name='Número de podios')
    poles = models.IntegerField(verbose_name='Número de poles')
    campeonatos = models.IntegerField(verbose_name='Número de campeonatos del mundo de pilotos ganados')
    temporadas = models.IntegerField(verbose_name='Número de temporadas disputadas')
    carreras = models.IntegerField(verbose_name='Número de carreras disputadas')
    puntos = models.DecimalField(decimal_places=10,max_digits=15,verbose_name='Número de puntos obtenidos durante su carrera deportiva')
    retiros = models.IntegerField(verbose_name='Número de retiros durante su carrera deportiva')
    anyos_competidos = models.ManyToManyField(Anyo, verbose_name='Años competidos en la categoría')

    def __str__(self):
        return self.nombre
    
class Escuderia(models.Model):
    nombre = models.TextField(verbose_name='Nombre')
    nacionalidad = models.ForeignKey(Nacionalidad,on_delete=models.SET_NULL, null=True,verbose_name='Nombre de la nacionalidad')
    victorias = models.IntegerField(verbose_name='Número de victorias')
    poles = models.IntegerField(verbose_name='Número de poles')
    temporadas = models.IntegerField(verbose_name='Número de temporadas disputadas')
    carreras = models.IntegerField(verbose_name='Número de carreras disputadas')
    campeonatos = models.IntegerField(verbose_name='Número de campeonatos del mundo de constructores ganados')
    puntos = models.DecimalField(decimal_places=10,max_digits=15,verbose_name='Número de puntos obtenidos durante su carrera deportiva')
    anyos_competidos = models.ManyToManyField(Anyo, verbose_name='Años competidos en la categoría')
    pilotos = models.ManyToManyField("Piloto") 
    
    def __str__(self):
        return self.nombre
    
class Votacion(models.Model):
    votante = models.TextField(verbose_name="Votante")
    piloto = models.ForeignKey(Piloto, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(verbose_name="Puntos sobre 5 otorgados")
    def __str__(self):
        return str(self.votante + "-" + self.piloto.nombre + "-" + str(self.puntuacion))    