from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Prefetch
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import RegistroForm
from .utils import obtener_temas_por_unidad
from .models import Tema, Ejercicio, Intento, Aprender, Retroalimentacion


def inicio(request):
    if request.user.is_authenticated:
        return redirect('bienvenida')
    return render(request, 'estudiantes/login.html')


@csrf_exempt
def login_verify(request):
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/bienvenida/'})
        return JsonResponse({'success': False, 'error': 'Usuario o Contraseña incorrectas'})
    return JsonResponse({'success': False, 'error': 'Metodo no permitido'})


@csrf_exempt
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({'success': True, 'redirect_url': '/bienvenida/'})
        return JsonResponse({'success': False, 'error': 'Datos invalidos',
                             'detalle': form.errors.as_json()})
    return render(request, 'estudiantes/registro.html')


def cerrar_sesion(request):
    logout(request)
    return redirect('/login/')


@login_required
def temas(request):
    return render(request, 'estudiantes/temas.html',
                  {'unidades': obtener_temas_por_unidad(request.user)})


@login_required
def ejercicios(request, id):
    unidades_ordenadas = obtener_temas_por_unidad(request.user)
    tema = get_object_or_404(Tema, id=id)
    intentos_usuario = Intento.objects.filter(usuario=request.user)
    ejercicios = Ejercicio.objects.filter(tema=tema)\
        .prefetch_related(Prefetch('intentos', queryset=intentos_usuario))\
        .annotate(total_intentos=Count('intentos', filter=Q(intentos__usuario=request.user)))
    return render(request, 'estudiantes/ejercicios.html', {
        'unidades': unidades_ordenadas,
        'temaPrincipal': tema,
        'ejerciciosEnviados': ejercicios,
    })


@login_required
def ejercicioAprender(request, id):
    unidades_ordenadas = obtener_temas_por_unidad(request.user)
    ejercicio = get_object_or_404(Ejercicio, id=id)
    aprender = get_object_or_404(Aprender, ejercicio__id=id)
    return render(request, 'estudiantes/ejercicio_aprender.html', {
        'unidades': unidades_ordenadas,
        'temaPrincipal': ejercicio.tema,
        'aprenderEnviado': aprender,
        'ejercicioEnviado': ejercicio,
    })


@login_required
def ejercicioResolver(request, id):
    unidades_ordenadas = obtener_temas_por_unidad(request.user)
    ejercicioAux = get_object_or_404(Ejercicio, id=id)
    intentos_usuario = Intento.objects.filter(usuario=request.user)
    ejercicio = Ejercicio.objects\
        .prefetch_related(Prefetch('intentos', queryset=intentos_usuario))\
        .annotate(total_intentos=Count('intentos', filter=Q(intentos__usuario=request.user)))\
        .get(id=id)
    return render(request, 'estudiantes/ejercicio_resolver.html', {
        'unidades': unidades_ordenadas,
        'temaPrincipal': ejercicioAux.tema,
        'ejercicioEnviado': ejercicio,
    })


@csrf_exempt
@login_required
@require_POST
def agregar_respuesta(request):
    respuesta = request.POST.get('valor')
    id = request.POST.get('id')
    if not id:
        return JsonResponse({'success': False, 'error': 'Falta el ejercicio'}, status=400)

    ejercicio = get_object_or_404(Ejercicio, id=id)
    correcto = (respuesta == ejercicio.solucion_esperada_ejercicio)
    retro = Retroalimentacion.objects.filter(ejercicio=ejercicio).first()

    if retro:
        mensaje = retro.mensajeCorrecto if correcto else retro.mensajeError
        recomendacion = retro.recomendacion
    else:
        mensaje = 'Respuesta correcta!' if correcto else 'Respuesta incorrecta, intenta de nuevo.'
        recomendacion = ''

    Intento.objects.create(usuario=request.user, ejercicio=ejercicio,
                           respuesta=respuesta or '', resultado='1' if correcto else '0')

    return JsonResponse({'success': True, 'correcto': correcto, 'mensaje': mensaje,
                         'recomendacion': recomendacion,
                         'redirect_url': '/ejercicio_resolver/'})


from .reportes import generar_reporte_progreso


@login_required
def descargar_reporte(request):
    return generar_reporte_progreso(request.user)


@login_required
def bienvenida(request):
    return render(request, 'estudiantes/bienvenida.html')
