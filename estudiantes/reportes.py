"""
Módulo de generación de reportes PDF.
Usa Paragraph dentro de cada celda para que el texto se ajuste sin desbordarse.
"""

from io import BytesIO
from datetime import datetime
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from .models import Ejercicio, Intento
from .utils import obtener_temas_por_unidad


# ==================== COLORES ====================
COLOR_PRIMARIO = colors.HexColor('#0d1117')
COLOR_ACENTO = colors.HexColor('#2f81f7')
COLOR_EXITO = colors.HexColor('#238636')
COLOR_GRIS = colors.HexColor('#8b949e')
COLOR_FILA_ALT = colors.HexColor('#f6f8fa')


# ==================== ESTILOS ====================
def _crear_estilos():
    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name='TituloUTA',
        parent=estilos['Heading1'],
        fontSize=18,
        textColor=COLOR_PRIMARIO,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    ))

    estilos.add(ParagraphStyle(
        name='SubtituloUTA',
        parent=estilos['Heading2'],
        fontSize=10,
        textColor=COLOR_GRIS,
        alignment=TA_CENTER,
        spaceAfter=18
    ))

    estilos.add(ParagraphStyle(
        name='Seccion',
        parent=estilos['Heading2'],
        fontSize=13,
        textColor=COLOR_ACENTO,
        spaceBefore=15,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))

    estilos.add(ParagraphStyle(
        name='Normal_Justificado',
        parent=estilos['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))

    estilos.add(ParagraphStyle(
        name='PieDePagina',
        parent=estilos['Normal'],
        fontSize=8,
        textColor=COLOR_GRIS,
        alignment=TA_CENTER
    ))

    # Estilos para celdas de tabla — clave para que el texto envuelva correctamente
    estilos.add(ParagraphStyle(
        name='CeldaTabla',
        parent=estilos['Normal'],
        fontSize=9,
        textColor=colors.black,
        alignment=TA_LEFT,
        leading=11
    ))

    estilos.add(ParagraphStyle(
        name='CeldaTablaCentro',
        parent=estilos['Normal'],
        fontSize=9,
        textColor=colors.black,
        alignment=TA_CENTER,
        leading=11
    ))

    estilos.add(ParagraphStyle(
        name='CeldaTablaHeader',
        parent=estilos['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=12
    ))

    return estilos


# ==================== FUNCIÓN PRINCIPAL ====================
def generar_reporte_progreso(usuario):
    """
    Genera un PDF con el progreso académico del usuario.
    Devuelve un HttpResponse listo para descargar.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Reporte de Progreso - {usuario.username}"
    )

    estilos = _crear_estilos()
    elementos = []

    # ===== ENCABEZADO INSTITUCIONAL =====
    elementos.append(Paragraph("UNIVERSIDAD TÉCNICA DE AMBATO", estilos['TituloUTA']))
    elementos.append(Paragraph(
        "Facultad de Ingeniería en Sistemas, Electrónica e Industrial<br/>"
        "Carrera de Software<br/>"
        "Algoritmos y Lógica de Programación",
        estilos['SubtituloUTA']
    ))

    linea = Table([['']], colWidths=[18 * cm], rowHeights=[2])
    linea.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), COLOR_ACENTO)]))
    elementos.append(linea)
    elementos.append(Spacer(1, 0.4 * cm))

    elementos.append(Paragraph(
        "REPORTE DE PROGRESO ACADÉMICO",
        ParagraphStyle(
            name='ReporteTitulo',
            fontSize=15,
            textColor=COLOR_PRIMARIO,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=15
        )
    ))

    # ===== 1. DATOS DEL ESTUDIANTE =====
    elementos.append(Paragraph("1. Datos del Estudiante", estilos['Seccion']))

    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    datos_data = [
        [Paragraph('<b>Nombre de usuario:</b>', estilos['CeldaTabla']),
         Paragraph(usuario.username or '—', estilos['CeldaTabla'])],
        [Paragraph('<b>Correo electrónico:</b>', estilos['CeldaTabla']),
         Paragraph(usuario.email or '—', estilos['CeldaTabla'])],
        [Paragraph('<b>Rol:</b>', estilos['CeldaTabla']),
         Paragraph(usuario.rol.capitalize() if usuario.rol else '—', estilos['CeldaTabla'])],
        [Paragraph('<b>Fecha del reporte:</b>', estilos['CeldaTabla']),
         Paragraph(fecha_actual, estilos['CeldaTabla'])],
    ]

    tabla_datos = Table(datos_data, colWidths=[5.5 * cm, 12.5 * cm])
    tabla_datos.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, COLOR_GRIS),
    ]))
    elementos.append(tabla_datos)

    # ===== 2. RESUMEN GENERAL =====
    elementos.append(Paragraph("2. Resumen General de Desempeño", estilos['Seccion']))

    total_ejercicios = Ejercicio.objects.count()
    intentos_usuario = Intento.objects.filter(usuario=usuario)
    total_intentos = intentos_usuario.count()
    intentos_correctos = intentos_usuario.filter(resultado='1').count()
    intentos_incorrectos = intentos_usuario.filter(resultado='0').count()
    ejercicios_resueltos = intentos_usuario.values('ejercicio').distinct().count()
    porcentaje_avance = (ejercicios_resueltos / total_ejercicios * 100) if total_ejercicios > 0 else 0
    tasa_acierto = (intentos_correctos / total_intentos * 100) if total_intentos > 0 else 0

    resumen_data = [
        [Paragraph('Métrica', estilos['CeldaTablaHeader']),
         Paragraph('Valor', estilos['CeldaTablaHeader'])],
        [Paragraph('Total de ejercicios disponibles', estilos['CeldaTabla']),
         Paragraph(str(total_ejercicios), estilos['CeldaTablaCentro'])],
        [Paragraph('Ejercicios trabajados', estilos['CeldaTabla']),
         Paragraph(str(ejercicios_resueltos), estilos['CeldaTablaCentro'])],
        [Paragraph('Total de intentos realizados', estilos['CeldaTabla']),
         Paragraph(str(total_intentos), estilos['CeldaTablaCentro'])],
        [Paragraph('Intentos correctos', estilos['CeldaTabla']),
         Paragraph(str(intentos_correctos), estilos['CeldaTablaCentro'])],
        [Paragraph('Intentos incorrectos', estilos['CeldaTabla']),
         Paragraph(str(intentos_incorrectos), estilos['CeldaTablaCentro'])],
        [Paragraph('Avance general', estilos['CeldaTabla']),
         Paragraph(f"{porcentaje_avance:.1f}%", estilos['CeldaTablaCentro'])],
        [Paragraph('Tasa de acierto', estilos['CeldaTabla']),
         Paragraph(f"{tasa_acierto:.1f}%", estilos['CeldaTablaCentro'])],
    ]

    tabla_resumen = Table(resumen_data, colWidths=[11 * cm, 7 * cm], repeatRows=1)
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARIO),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_GRIS),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_FILA_ALT]),
    ]))
    elementos.append(tabla_resumen)

    # ===== 3. PROGRESO POR UNIDAD =====
    elementos.append(Paragraph("3. Progreso por Unidad", estilos['Seccion']))

    unidades = obtener_temas_por_unidad(usuario)

    progreso_data = [[
        Paragraph('Unidad', estilos['CeldaTablaHeader']),
        Paragraph('Tema', estilos['CeldaTablaHeader']),
        Paragraph('Total', estilos['CeldaTablaHeader']),
        Paragraph('Completados', estilos['CeldaTablaHeader']),
        Paragraph('% Avance', estilos['CeldaTablaHeader']),
    ]]

    for nombre_unidad, temas in unidades.items():
        for tema in temas:
            total_ej = tema.total_ejercicios or 0
            completados = tema.ejercicios_completados or 0
            porcentaje = (completados / total_ej * 100) if total_ej > 0 else 0

            progreso_data.append([
                Paragraph(nombre_unidad, estilos['CeldaTabla']),
                Paragraph(tema.name_tema, estilos['CeldaTabla']),
                Paragraph(str(total_ej), estilos['CeldaTablaCentro']),
                Paragraph(str(completados), estilos['CeldaTablaCentro']),
                Paragraph(f"{porcentaje:.0f}%", estilos['CeldaTablaCentro']),
            ])

    tabla_progreso = Table(
        progreso_data,
        colWidths=[3 * cm, 8 * cm, 2 * cm, 2.5 * cm, 2.5 * cm],
        repeatRows=1
    )
    tabla_progreso.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARIO),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_GRIS),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_FILA_ALT]),
    ]))
    elementos.append(tabla_progreso)

    # ===== 4. EJERCICIOS RESUELTOS =====
    elementos.append(PageBreak())
    elementos.append(Paragraph("4. Ejercicios Resueltos Correctamente", estilos['Seccion']))

    correctos = intentos_usuario.filter(resultado='1')\
        .select_related('ejercicio', 'ejercicio__tema').order_by('-fecha')

    if correctos.exists():
        detalle_data = [[
            Paragraph('Tema', estilos['CeldaTablaHeader']),
            Paragraph('Ejercicio', estilos['CeldaTablaHeader']),
            Paragraph('Dificultad', estilos['CeldaTablaHeader']),
            Paragraph('Fecha', estilos['CeldaTablaHeader']),
        ]]

        for intento in correctos:
            detalle_data.append([
                Paragraph(intento.ejercicio.tema.name_tema, estilos['CeldaTabla']),
                Paragraph(intento.ejercicio.titulo_ejercicio, estilos['CeldaTabla']),
                Paragraph(intento.ejercicio.dificultad_ejercicio.capitalize(), estilos['CeldaTablaCentro']),
                Paragraph(intento.fecha.strftime("%d/%m/%Y %H:%M"), estilos['CeldaTablaCentro']),
            ])

        tabla_detalle = Table(
            detalle_data,
            colWidths=[5 * cm, 7 * cm, 2.5 * cm, 3.5 * cm],
            repeatRows=1
        )
        tabla_detalle.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_EXITO),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_GRIS),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_FILA_ALT]),
        ]))
        elementos.append(tabla_detalle)
    else:
        elementos.append(Paragraph(
            "Aún no has resuelto ningún ejercicio correctamente. ¡Sigue practicando!",
            estilos['Normal_Justificado']
        ))

    # ===== 5. OBSERVACIONES =====
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(Paragraph("5. Observaciones", estilos['Seccion']))

    if porcentaje_avance >= 80:
        observacion = (
            f"<b>Excelente desempeño.</b> Has completado el {porcentaje_avance:.1f}% del contenido "
            f"con una tasa de acierto del {tasa_acierto:.1f}%. Continúa con este nivel de dedicación."
        )
    elif porcentaje_avance >= 50:
        observacion = (
            f"<b>Buen progreso.</b> Llevas un avance del {porcentaje_avance:.1f}% y tu tasa de acierto "
            f"es del {tasa_acierto:.1f}%. Sigue practicando para reforzar los temas pendientes."
        )
    elif porcentaje_avance >= 20:
        observacion = (
            f"<b>En desarrollo.</b> Tu avance actual es del {porcentaje_avance:.1f}%. "
            f"Te recomendamos dedicar más tiempo a las unidades con menor avance."
        )
    else:
        observacion = (
            f"<b>Inicio del proceso.</b> Acabas de comenzar tu camino en la plataforma. "
            f"Te invitamos a explorar los temas y resolver los ejercicios paso a paso."
        )

    elementos.append(Paragraph(observacion, estilos['Normal_Justificado']))

    # ===== PIE DE PÁGINA =====
    elementos.append(Spacer(1, 1 * cm))
    elementos.append(Paragraph(
        f"Reporte generado automáticamente por Silabo - UTA FISEI<br/>"
        f"Algoritmos y Lógica de Programación | Ciclo Académico Enero - Julio 2026",
        estilos['PieDePagina']
    ))

    # ===== CONSTRUIR PDF =====
    doc.build(elementos)
    pdf = buffer.getvalue()
    buffer.close()

    nombre_archivo = f"reporte_progreso_{usuario.username}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response