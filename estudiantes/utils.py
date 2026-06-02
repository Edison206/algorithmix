from django.db.models import Count, Q
from collections import defaultdict
from .models import Tema

def obtener_temas_por_unidad():
    temas = Tema.objects.all().annotate(
        total_ejercicios=Count('ejercicios', distinct=True),

        ejercicios_completados=Count(
            'ejercicios',
            filter=Q(ejercicios__intentos__isnull=False),
            distinct=True
        )
    ).order_by('-id')

    unidades = defaultdict(list)

    for tema in temas:
        unidades[tema.unidad_tema].append(tema)

    unidades_ordenadas = dict(sorted(unidades.items(), key=lambda x: x[0]))

    return unidades_ordenadas