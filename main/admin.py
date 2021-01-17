from django.contrib import admin
from main.models import Piloto, Escuderia, Nacionalidad, Anyo, Votacion
# Register your models here.
admin.site.register(Piloto)
admin.site.register(Escuderia)
admin.site.register(Nacionalidad)
admin.site.register(Anyo)
admin.site.register(Votacion)