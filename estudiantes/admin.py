from django.contrib import admin
from .models import Tema, Ejercicio, Intento, Retroalimentacion, Usuario, Aprender

admin.site.register(Tema)
admin.site.register(Ejercicio)
admin.site.register(Intento)
admin.site.register(Retroalimentacion)
admin.site.register(Usuario)
admin.site.register(Aprender)
