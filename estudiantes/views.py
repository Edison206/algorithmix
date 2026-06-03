from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q, Prefetch
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from .forms import RegistroForm

from .utils import obtener_temas_por_unidad
from .models import Tema, Ejercicio, Intento, Aprender, Usuario, Retroalimentacion


def inicio(request):
    return render(request, 'estudiantes/login.html')


@csrf_exempt
def login_verify(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'redirect_url': '/temas/'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Usuario o Contraseña incorrectas'
            })

    return JsonResponse({'success': False})


def temas(request):
    unidades_ordenadas = obtener_temas_por_unidad(request.user)

    return render(request, 'estudiantes/temas.html', {
        'unidades': unidades_ordenadas
    })


@csrf_exempt
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/temas/'})
        else:
            errores = form.errors.as_json()
            return JsonResponse({'success': False, 'error': 'Datos inválidos', 'detalle': errores})
    return render(request, 'estudiantes/registro.html')


def ejercicios(request, id):
    unidades_ordenadas = obtener_temas_por_unidad(request.user)
    tema = Tema.objects.get(id=id)

    # Solo intentos del usuario actual (privacidad por usuario)
    intentos_usuario = Intento.objects.filter(usuario=request.user)

    ejercicios = Ejercicio.objects.filter(tema=tema)\
        .prefetch_related(Prefetch('intentos', queryset=intentos_usuario))\
        .annotate(total_intentos=Count('intentos', filter=Q(intentos__usuario=request.user)))

    return render(request, 'estudiantes/ejercicios.html', {
        'unidades': unidades_ordenadas,
        'temaPrincipal': tema,
        'ejerciciosEnviados': ejercicios
    })


def ejercicioAprender(request, id):
    unidades_ordenadas = obtener_temas_por_unidad(request.user)

    ejercicio = Ejercicio.objects.get(id=id)
    tema = ejercicio.tema

    aprender = Aprender.objects.get(ejercicio__id=id)

    return render(request, 'estudiantes/ejercicio_aprender.html', {
        'unidades': unidades_ordenadas,
        'temaPrincipal': tema,
        'aprenderEnviado': aprender,
        'ejercicioEnviado': ejercicio
    })


def ejercicioResolver(request, id):
    unidades_ordenadas = obtener_temas_por_unidad(request.user)

    ejercicioAux = Ejercicio.objects.get(id=id)
    tema = ejercicioAux.tema

    # Solo intentos del usuario actual (privacidad por usuario)
    intentos_usuario = Intento.objects.filter(usuario=request.user)

    ejercicio = Ejercicio.objects\
        .prefetch_related(Prefetch('intentos', queryset=intentos_usuario))\
        .annotate(total_intentos=Count('intentos', filter=Q(intentos__usuario=request.user)))\
        .get(id=id)

    return render(request, 'estudiantes/ejercicio_resolver.html', {
        'unidades': unidades_ordenadas,
        'temaPrincipal': tema,
        'ejercicioEnviado': ejercicio
    })


@csrf_exempt
def agregar_respuesta(request):
    if request.method == 'POST':
        respuesta = request.POST.get('valor')
        id = request.POST.get('id')
        ejercicio = Ejercicio.objects.get(id=id)
        user = request.user

        # Buscar retroalimentacion si existe
        try:
            retro = Retroalimentacion.objects.get(ejercicio=ejercicio)
            if respuesta == ejercicio.solucion_esperada_ejercicio:
                mensaje = retro.mensajeCorrecto
                recomendacion = retro.recomendacion
            else:
                mensaje = retro.mensajeError
                recomendacion = retro.recomendacion
        except Retroalimentacion.DoesNotExist:
            if respuesta == ejercicio.solucion_esperada_ejercicio:
                mensaje = "¡Respuesta correcta!"
                recomendacion = ""
            else:
                mensaje = "Respuesta incorrecta, intenta de nuevo."
                recomendacion = ""

        if respuesta == ejercicio.solucion_esperada_ejercicio:
            Intento.objects.create(
                usuario=user,
                ejercicio=ejercicio,
                respuesta=respuesta,
                resultado='1'
            )
            return JsonResponse({
                'success': True,
                'correcto': True,
                'mensaje': mensaje,
                'recomendacion': recomendacion,
                'redirect_url': '/ejercicio_resolver/'
            })
        else:
            Intento.objects.create(
                usuario=user,
                ejercicio=ejercicio,
                respuesta=respuesta,
                resultado='0'
            )
            return JsonResponse({
                'success': True,
                'correcto': False,
                'mensaje': mensaje,
                'recomendacion': recomendacion,
                'redirect_url': '/ejercicio_resolver/'
            })


def cerrar_sesion(request):
    logout(request)
    return redirect('/login/')



# ==================== REPORTES ====================
from .reportes import generar_reporte_progreso


def descargar_reporte(request):
    """
    Genera y descarga el reporte de progreso académico del usuario actual.
    Requiere que el usuario esté autenticado.
    """
    if not request.user.is_authenticated:
        return redirect('/login/')

    return generar_reporte_progreso(request.user)