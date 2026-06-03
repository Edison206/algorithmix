from django.urls import path
from .views import inicio, login_verify, temas, ejercicios, ejercicioResolver, agregar_respuesta, ejercicioAprender, registro, cerrar_sesion, descargar_reporte

urlpatterns = [
    path('login/', inicio, name='login'),
    path('login/verify/', login_verify),
    path('registro/', registro, name='registro'),
    path('temas/', temas,  name='temas'),
    path('ejercicios/<int:id>/', ejercicios, name='ejercicios'),
    path('ejercicio_resolver/<int:id>/', ejercicioResolver, name='ejercicio_resolver'),
    path('agregar_respuesta/', agregar_respuesta),
    path('ejercicio_aprender/<int:id>/', ejercicioAprender, name='ejercicio_aprender'),
    path('logout/', cerrar_sesion, name='logout'),
    path('reporte/descargar/', descargar_reporte, name='descargar_reporte'),

]