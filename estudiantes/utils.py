from django.db.models import Count, Q
from collections import defaultdict
from .models import Tema


def obtener_temas_por_unidad(usuario=None):
    # Solo contar como "completados" los ejercicios donde el USUARIO ACTUAL tenga intentos
    if usuario is not None and usuario.is_authenticated:
        filtro_completados = Q(ejercicios__intentos__usuario=usuario)
    else:
        # Si no hay usuario logueado, ningun ejercicio cuenta como completado
        filtro_completados = Q(pk__in=[])

    temas = Tema.objects.all().annotate(
        total_ejercicios=Count('ejercicios', distinct=True),

        ejercicios_completados=Count(
            'ejercicios',
            filter=filtro_completados,
            distinct=True
        )
    ).order_by('-id')

    unidades = defaultdict(list)

    for tema in temas:
        unidades[tema.unidad_tema].append(tema)

    unidades_ordenadas = dict(sorted(unidades.items(), key=lambda x: x[0]))

    return unidades_ordenadas