from django.contrib.auth.models import AbstractUser
from django.conf import settings

from django.db import models


# ==================== Usuario ====================
class Usuario(AbstractUser):
    ROLES = (
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
    )

    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES)

    # Opcional: usar email como login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


# ==================== TEMA ====================
class Tema(models.Model):
    name_tema = models.CharField(max_length=200)
    descripcion_tema = models.TextField()
    unidad_tema = models.CharField(max_length=100)

    def __str__(self):
        return self.name_tema


# ==================== EJERCICIO ====================
class Ejercicio(models.Model):
    Dificultad = (
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    )


    titulo_ejercicio = models.CharField(max_length=200)
    enunciado_ejercicio = models.TextField()  # MUCHO TEXTO
    categoria_ejercicio = models.CharField(max_length=100)
    dificultad_ejercicio = models.CharField(max_length=50, choices=Dificultad)

    codigo_ejercicio = models.TextField(blank=True, default='')  
    solucion_esperada_ejercicio = models.TextField(max_length=200, blank=True, default='')

    archivo_pdf_ejercicio = models.FileField(upload_to='apes/', blank=True, null=True)  

    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name="ejercicios")

    def __str__(self):
        return self.titulo_ejercicio


# ==================== INTENTO ====================
class Intento(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE,  related_name='intentos')

    respuesta = models.TextField()  
    resultado = models.CharField(max_length=50)

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.ejercicio}"


# ==================== RETROALIMENTACION ====================
class Retroalimentacion(models.Model):
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)

    mensajeCorrecto = models.TextField()
    mensajeError = models.TextField()
    recomendacion = models.TextField()

    def __str__(self):
        return f"Feedback {self.ejercicio}"


#=========================Aprender=========================
class Aprender(models.Model):
    enunciado_aprender = models.TextField()
    ejercicioBien_aprender = models.TextField()
    ejercicioMal_aprender = models.TextField()
    ejercicioJava_aprender = models.TextField(blank=True, default='')

    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)

    def __str__(self):
        return self.enunciado_aprender

