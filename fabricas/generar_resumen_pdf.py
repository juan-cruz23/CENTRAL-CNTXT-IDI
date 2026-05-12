"""
Resumen_Indicadores_CNTXT_PT2.pdf
8 páginas: 1 portada-resumen + 1 portafolio de proyectos + 6 páginas de detalle (1 indicador por página)
Formato: carta apaisada 11×8.5 in
"""

# ════════════════════════════════════════════════════════════════════════════
# TEXTOS CORREGIDOS PARA PLATAFORMA COLOMBIA PRODUCTIVA
# (copiar y pegar — 6 indicadores)
# ════════════════════════════════════════════════════════════════════════════
TEXTOS_PLATAFORMA = """

═══════════════════════════════════════════════════════════════════════════
IPT-1  TNVA — Reducción de Tiempo que No Agrega Valor
═══════════════════════════════════════════════════════════════════════════

Cálculo de la medición:

Mediante VSM se clasificaron las actividades del proceso de gestión de proyectos (13 activos) en VA y NVA. Se midió la frecuencia y duración de cada actividad NVA en una semana tipo de marzo 2026:

NVA 1 – Transcripción manual de datos a tabla para dummies: 3x/sem × 25 min = 75 min.
NVA 2 – Transferencia de datos tabla para dummies a tabla gruesa: 2x/sem × 20 min = 40 min.
NVA 3 – Alimentación de dashboards desde tabla gruesa: 1x/sem × 30 min = 30 min.
NVA 4 – Búsqueda de información dispersa (Drive, Monday, Sheets, correo): 5x/sem × 20 min = 100 min.
NVA 5 – Consolidación manual del reporte ejecutivo semanal: 1x/sem × 45 min = 45 min.
NVA 6 – Actualización manual de cronogramas en Google Sheets: 2x/sem × 15 min = 30 min.
NVA 7 – Reconciliación de costos reales vs. presupuestados: 1x/sem × 30 min = 30 min.

TNVA = 75 + 40 + 30 + 100 + 45 + 30 + 30 = 350 min/semana (línea base, marzo 2026).
Meta: 350 × 0,70 = 245 min/semana (−30 %).

  Línea base: 350,00
  Meta:       245,00
  Variación:  -30,00 %


═══════════════════════════════════════════════════════════════════════════
IPT-2  TCP — Reducción del Tiempo de Ciclo de Gestión Operativa
═══════════════════════════════════════════════════════════════════════════

Cálculo de la medición:

Fórmula aplicada: TCP = Σ horas hábiles transcurridas en cada hito del ciclo, desde la ocurrencia del evento hasta la decisión correctiva.

Ciclo línea base — 48 horas hábiles (6 días hábiles promedio):

• Hito 1 — Ocurrencia del evento operativo: Hora 0.
• Hito 2 — Registro manual del evento por el Líder de Proyecto en Google Sheets: 12 horas hábiles de latencia (8 a 16 horas si no coincide con día de actualización).
• Hito 3 — Consolidación de la información en la tabla gruesa: 12 horas hábiles adicionales.
• Hito 4 — Preparación del reporte para reunión del equipo directivo (Coffee semanal): 16 horas hábiles.
• Hito 5 — Revisión y decisión del equipo directivo durante la reunión semanal: 4 horas hábiles.
• Hito 6 — Escalamiento y decisión: 4 horas hábiles.

TOTAL TCP línea base: 0 + 12 + 12 + 16 + 4 + 4 = 48 horas hábiles (Marzo 2026).
META TCP: 48 × 0,3333 = 16 horas hábiles (reducción del 66,67 %).

  Línea base: 48,00
  Meta:       16,00
  Variación:  -66,67 %


═══════════════════════════════════════════════════════════════════════════
IPT-3  AD — Ahorro Generado en Reducción de Desperdicios Operativos
═══════════════════════════════════════════════════════════════════════════

Cálculo de la medición:

Perfil 1 — Líder de Proyecto:
Honorarios: $24.725/hora (base 182 h/mes, Ley 2101/2021)
Horas TNVA (NVA 1+4+5+6): 250 min/sem × 4,33 ÷ 60 = 18,04 h/mes
Costo: 18,04 × $24.725 = $446.039/mes

Perfil 2 — Director Ejecutivo:
Honorarios: $43.956/hora (base 182 h/mes, Ley 2101/2021)
Horas TNVA (NVA 7): 30 min/sem × 4,33 ÷ 60 = 2,17 h/mes
Costo: 2,17 × $43.956 = $95.385/mes

Perfil 3 — Director Creativo:
Honorarios: $32.967/hora (base 182 h/mes, Ley 2101/2021)
Horas TNVA: 0 h/mes (sin actividades NVA)
Costo: $0/mes

Totales:
AD línea base calculada: $446.039 + $95.385 + $0 = $541.424/mes ≈ $541.000/mes
Meta AD (−35 %): $541.000 × 0,65 = $352.000/mes

  Línea base: 541.000,00
  Meta:       352.000,00
  Variación:  -35,00 %


═══════════════════════════════════════════════════════════════════════════
IPT-4  CU — Costo Unitario de Gestión Administrativa por Proyecto
═══════════════════════════════════════════════════════════════════════════

Cálculo de la medición:

CU = Costo Total de Gestión (VA + NVA) ÷ Número de proyectos activos

• Líder de Proyecto: 555 min/sem × 4,33 ÷ 60 = 40,05 h/mes × $24.725/h = $990.236/mes
• Director Ejecutivo: 165 min/sem × 4,33 ÷ 60 = 11,91 h/mes × $43.956/h = $523.516/mes
• Director Creativo: 120 min/sem × 4,33 ÷ 60 = 8,66 h/mes × $32.967/h = $285.494/mes
• CT total (VA + NVA): $990.236 + $523.516 + $285.494 = $1.799.246/mes
• Número de proyectos activos: 13
• CU = $1.799.246 ÷ 13 = $138.404/proyecto/mes ≈ $138.400/proyecto/mes

Meta CU: $138.400 × 0,65 = $90.000/proyecto/mes (reducción del 34,97 %)
Reducción absoluta esperada: $138.400 − $90.000 = $48.400/proyecto/mes

  Línea base: 138.400,00
  Meta:       90.000,00
  Variación:  -34,97 %


═══════════════════════════════════════════════════════════════════════════
IPT-5  OPC — Optimización de Puntos de Contacto con el Cliente
═══════════════════════════════════════════════════════════════════════════

Cálculo de la medición:

OPC = (Subprocesos con contacto directo cliente ÷ Total subprocesos del ciclo) × 100

Línea Base — Marzo 2026:
Total de subprocesos del ciclo productivo: 12 actividades.
Subprocesos con contacto directo con el cliente externo: 7 puntos.

P1: Convocatoria y coordinación de reunión de avance con cliente (correo/llamada).
P2: Preparación de presentación de avance impresa para el cliente.
P3: Reunión presencial de avance con entrega de material impreso al cliente.
P4: Envío de planos y renders al cliente para revisión y aprobación.
P5: Recepción y procesamiento de comentarios del cliente (correo/verbal).
P6: Ciclo de ajustes por feedback del cliente y re-envío de entregables.
P7: Confirmación de aprobación y escalamiento de hito con el cliente.

OPC línea base = (7 ÷ 12) × 100 = 58,33 %

Meta — Proceso rediseñado:
Subprocesos conservados con contacto directo cliente: 3 puntos.

P1: Líder registra avance en Central Contexto 2.0; cliente accede al dashboard en tiempo real.
P2: Sistema genera notificación automática al cliente con informe de avance digital.
P3: Cliente aprueba digitalmente en la plataforma y se escala el hito.

OPC meta = (3 ÷ 12) × 100 = 25,00 %

  Línea base: 58,33
  Meta:       25,00
  Variación:  -57,14 %


═══════════════════════════════════════════════════════════════════════════
IPT-6  IA — Impacto Ambiental: Consumo de Recursos por Servicio Prestado
═══════════════════════════════════════════════════════════════════════════

Cálculo de la medición:

Fórmula aplicada: IA = Σ (Frecuencia mensual × Número de hojas por tipo de documento).
El resultado se expresa en hojas de papel por mes.

• Documento 1 — Reportes ejecutivos impresos para reuniones presenciales con equipo directivo: 40 hojas/mes (4 reuniones × 10 hojas promedio).
• Documento 2 — Presentaciones de avance de proyectos impresas para reuniones con clientes: 60 hojas/mes (distribuidas entre 13 proyectos activos).
• Documento 3 — Planos y renders impresos para aprobación de clientes en reuniones presenciales: 30 hojas/mes.
• Documento 4 — Documentación de soporte de gestión de proyectos (actas de seguimiento, fichas de entregables): 25 hojas/mes.
• Documento 5 — Copias de respaldo de información crítica de proyectos: 15 hojas/mes.

TOTAL IA línea base: 40 + 60 + 30 + 25 + 15 = 170 hojas/mes (Marzo 2026).
META IA: 145 hojas/mes (reducción del 14,71 %).

  Línea base: 170,00
  Meta:       145,00
  Variación:  -14,71 %

═══════════════════════════════════════════════════════════════════════════
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import textwrap, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'Resumen_Indicadores_CNTXT_PT2.pdf')

# ── Paleta ────────────────────────────────────────────────────────────────────
HEAD  = '#1a3a5c'
VA_C  = '#27ae60'
NVA_C = '#c0392b'
VAR_C = '#2471a3'
SOS_C = '#7d3c98'
BG    = '#f7f9fc'
WHITE = '#ffffff'
LGRAY = '#ecf0f1'
DGRAY = '#dde3ea'
DARK  = '#2c3e50'
MID   = '#5d6d7e'

W, H = 11.0, 8.5        # figura (pulgadas, landscape)
MX   = 0.28             # margen lateral
TW   = W - 2*MX        # ancho de trabajo = 10.44

# ── Helpers ───────────────────────────────────────────────────────────────────
def fig_ax():
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis('off')
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    return fig, ax

def r(ax, x, y, w, h, fc, ec='none', lw=1, z=2, alpha=1.0):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec,
                            linewidth=lw, zorder=z, alpha=alpha))

def txt(ax, x, y, s, size=9, bold=False, color=DARK, ha='left', va='center',
        italic=False, z=4, alpha=1.0, wrap_w=None):
    """Escribe texto; si wrap_w, hace wrap y retorna número de líneas usadas."""
    if wrap_w:
        lines = textwrap.wrap(str(s), wrap_w)
        for i, line in enumerate(lines):
            ax.text(x, y - i*0.195, line, fontsize=size, ha=ha, va=va,
                    color=color, fontweight='bold' if bold else 'normal',
                    fontstyle='italic' if italic else 'normal', zorder=z)
        return len(lines)
    ax.text(x, y, str(s), fontsize=size, ha=ha, va=va, color=color,
            fontweight='bold' if bold else 'normal',
            fontstyle='italic' if italic else 'normal',
            zorder=z, alpha=alpha)
    return 1

def header_global(ax, subtitle=''):
    """Banda azul superior global."""
    r(ax, 0, H-0.52, W, 0.52, HEAD, z=3)
    ax.text(W/2, H-0.17, 'RESUMEN DE INDICADORES — PLAN DE TRABAJO 2',
            ha='center', va='center', fontsize=12.5, fontweight='bold',
            color=WHITE, zorder=4)
    ax.text(W/2, H-0.40, subtitle or
            'CONTEXTO ARQUITECTURA S.A.S. (CNTXT)  |  Productividad Operacional  |  Línea base: Marzo 2026',
            ha='center', va='center', fontsize=7.5, color='#aec6e8', zorder=4)

def footer_band(ax, page, total):
    r(ax, 0, 0, W, 0.30, HEAD, z=3)
    ax.text(MX, 0.15,
            'CONTEXTO ARQUITECTURA S.A.S. (CNTXT)  |  Fábricas de Productividad — Colombia Productiva  |  Plan de Trabajo 2',
            ha='left', va='center', fontsize=6.5, color='#aec6e8', zorder=4)
    ax.text(W-MX, 0.15, f'Pág. {page}/{total}',
            ha='right', va='center', fontsize=7, color='#aec6e8', zorder=4)

def metric_box(ax, x, y, w, h, label, value, val_color, label_bg):
    """Caja métrica con etiqueta arriba y valor abajo."""
    r(ax, x, y+h*0.45, w, h*0.55, label_bg, z=3)   # banda etiqueta
    r(ax, x, y,        w, h*0.45, WHITE,     z=3)   # banda valor
    ax.add_patch(Rectangle((x, y), w, h, facecolor='none',
                            edgecolor=label_bg, linewidth=1.2, zorder=4))
    ax.text(x+w/2, y+h*0.72, label, ha='center', va='center',
            fontsize=7.5, fontweight='bold', color=WHITE, zorder=5)
    ax.text(x+w/2, y+h*0.20, value, ha='center', va='center',
            fontsize=11.5, fontweight='bold', color=val_color, zorder=5)

def table(ax, x, y_top, col_xs, col_ws, headers, rows,
          header_color, row_h=0.285, fontsize_body=8):
    """
    Dibuja tabla con encabezado coloreado.
    col_xs: posiciones x de cada columna (relativas a x).
    col_ws: anchos de cada columna.
    Retorna y inferior de la tabla.
    """
    n_cols = len(headers)
    full_w = sum(col_ws)
    header_h = 0.28

    # Fondo encabezado
    r(ax, x, y_top - header_h, full_w, header_h, header_color, z=3)
    for j, h in enumerate(headers):
        cx = x + col_xs[j] + col_ws[j]/2
        ax.text(cx, y_top - header_h/2, h, ha='center', va='center',
                fontsize=8, fontweight='bold', color=WHITE, zorder=4)

    y = y_top - header_h
    for i, row in enumerate(rows):
        bg = WHITE if i % 2 == 0 else LGRAY
        r(ax, x, y - row_h, full_w, row_h, bg, ec=DGRAY, lw=0.6, z=3)

        # Borde derecho entre columnas
        cx = x
        for j in range(n_cols - 1):
            cx += col_ws[j]
            ax.plot([cx, cx], [y - row_h, y], color=DGRAY, lw=0.5, zorder=4)

        for j, cell in enumerate(row):
            cx = x + col_xs[j]
            cw = col_ws[j]
            is_last_col = (j == n_cols - 1)
            al = 'left' if j <= 1 else 'center'
            # Wrap texto si necesario
            cell_str = str(cell)
            max_chars = max(8, int(cw / 0.056))   # ~0.056 in/char a 7.5pt
            lines = textwrap.wrap(cell_str, max_chars) or ['']
            lh = row_h / max(len(lines), 1)
            for li, line in enumerate(lines):
                ly = y - (li + 0.5) * lh
                px = cx + (0.08 if al == 'left' else cw/2)
                ax.text(px, ly, line, ha=al, va='center',
                        fontsize=fontsize_body, color=DARK, zorder=4)
        y -= row_h

    # Borde exterior
    r(ax, x, y, full_w, y_top-y, 'none', ec=HEAD, lw=1.0, z=5)
    return y   # y inferior

def section_label(ax, x, y, text, color=HEAD):
    r(ax, x, y-0.01, TW, 0.235, color, alpha=0.12, z=2)
    ax.text(x+0.10, y+0.105, text, ha='left', va='center',
            fontsize=9, fontweight='bold', color=color, zorder=3)


# ════════════════════════════════════════════════════════════════════════════
# DATOS
# ════════════════════════════════════════════════════════════════════════════
indicadores = [
    dict(
        cod='IPT-1', tipo='Fijo', color=NVA_C,
        nombre='Reducción de Tiempo que No Agrega Valor (TNVA)',
        unidad='Minutos / semana',
        base='350,00', meta='245,00', var='-30,00 %',
        alcance='Proceso completo de gestión de proyectos de CNTXT (13 proyectos activos), '
                'desde el registro inicial por el Líder de Proyecto hasta la decisión '
                'correctiva del equipo directivo. Alcance idéntico en mediciones intermedia y de salida.',
        formula='TNVA = Σ (Frecuencia semanal × Tiempo unitario en minutos)  para cada actividad NVA',
        t_headers=['Actividad NVA', 'Descripción', 'Frecuencia', 'T. unitario', 'Total sem.'],
        t_cw=[1.0, 4.9, 1.4, 1.4, 1.74],
        t_rows=[
            ('NVA 1', 'Transcripción manual de datos a tabla para dummies', '3x / sem', '25 min', '75 min'),
            ('NVA 2', 'Transferencia de datos tabla dummies → tabla gruesa', '2x / sem', '20 min', '40 min'),
            ('NVA 3', 'Alimentación de dashboards desde tabla gruesa', '1x / sem', '30 min', '30 min'),
            ('NVA 4', 'Búsqueda de información dispersa (Drive, Monday, Sheets, correo)', '5x / sem', '20 min', '100 min'),
            ('NVA 5', 'Consolidación manual del reporte ejecutivo semanal', '1x / sem', '45 min', '45 min'),
            ('NVA 6', 'Actualización manual de cronogramas en Google Sheets', '2x / sem', '15 min', '30 min'),
            ('NVA 7', 'Reconciliación manual costos reales vs. presupuestados', '1x / sem', '30 min', '30 min'),
            ('TOTAL', '', '', '', '350 min/sem'),
        ],
        entregable='VSM_CNTXT_PT2.xlsx  |  VSM_Proceso_Actual_CNTXT.png  |  VSM_Proceso_Futuro_CNTXT.png',
    ),
    dict(
        cod='IPT-2', tipo='Fijo', color=NVA_C,
        nombre='Reducción del Tiempo de Ciclo de Gestión Operativa (TCP)',
        unidad='Horas hábiles (jornada 8,4 h — Ley 2101/2021)',
        base='48,00', meta='16,00', var='-66,67 %',
        alcance='Ciclo completo desde la ocurrencia de un evento operativo relevante '
                '(desfase en cronograma, desviación presupuestal, pausa de cliente) '
                'hasta la toma de decisión correctiva del equipo directivo.',
        formula='TCP = Σ horas hábiles de cada hito del ciclo  (ocurrencia del evento → decisión correctiva)',
        t_headers=['Hito', 'Descripción del hito', 'Responsable', 'Línea base', 'Meta'],
        t_cw=[0.8, 4.2, 2.0, 1.72, 1.72],
        t_rows=[
            ('H1', 'Ocurrencia del evento operativo', 'Evento externo', '0 h', '0 h'),
            ('H2', 'Detección y registro del evento', 'Líder Proyecto', '12 h', '1,5 h — alerta automática'),
            ('H3', 'Consolidación en tabla gruesa', 'Asistente / Líder', '12 h', '0 h — ELIMINADO'),
            ('H4', 'Preparación del reporte para reunión directiva', 'Líder Proyecto', '16 h', '0 h — ELIMINADO'),
            ('H5', 'Revisión por Líder antes de escalar', 'Líder Proyecto', '4 h', '3 h'),
            ('H6', 'Escalamiento y decisión del equipo directivo', 'Equipo Directivo', '4 h', '11,5 h'),
            ('', 'TOTAL', '', '48 h hábiles', '16 h hábiles'),
        ],
        entregable='VSM_CNTXT_PT2.xlsx  |  VSM_TCP_CNTXT.png',
    ),
    dict(
        cod='IPT-3', tipo='Variable', color=VAR_C,
        nombre='Ahorro Generado en Reducción de Desperdicios Operativos (AD)',
        unidad='Pesos colombianos / mes',
        base='541.000,00', meta='352.000,00', var='-35,00 %',
        alcance='Costo mensual de las actividades TNVA del VSM por perfil. Líder de Proyecto: '
                'NVA 1+4+5+6 (250 min/sem). Director Ejecutivo: NVA 7 (30 min/sem). Director Creativo: sin NVA. '
                'Costo/hora = honorarios ÷ 182 h/mes (Ley 2101/2021). '
                'Horas mensuales = min/sem × 4,33 ÷ 60  [4,33 = 52 semanas ÷ 12 meses].',
        formula='AD = Σ (Horas TNVA mensuales del perfil  ×  Costo por hora del perfil)',
        t_headers=['Perfil', 'Actividades NVA  (min/sem)', 'Horas TNVA/mes', 'Costo/hora  (182 h)', 'Costo TNVA/mes'],
        t_cw=[2.4, 3.2, 1.6, 1.8, 1.44],
        t_rows=[
            ('Líder de Proyecto', 'NVA 1+4+5+6  (250 min/sem)', '18,04 h', '$ 24.725 / h', '$ 446.039'),
            ('Director Ejecutivo', 'NVA 7  (30 min/sem)', '2,17 h', '$ 43.956 / h', '$ 95.385'),
            ('Director Creativo', 'Ninguna  (solo VA)', '0 h', '$ 32.967 / h', '$ 0'),
            ('AD línea base  (280 min/sem totales)', '20,21 h/mes', '', '', '$ 541.424 ≈ $ 541.000 / mes'),
            ('Meta AD  (−35 %)', '$ 541.000 × 0,65', '', '', '$ 352.000 / mes'),
        ],
        entregable='Reporte_Mediciones_CNTXT_PT2.xlsx  (hoja IPT-3 AD)',
    ),
    dict(
        cod='IPT-4', tipo='Variable', color=VAR_C,
        nombre='Costo Unitario de Gestión Administrativa por Proyecto (CU)',
        unidad='Pesos colombianos / proyecto / mes',
        base='138.400,00', meta='90.000,00', var='-34,97 %',
        alcance='Costo total de gestión (actividades VA + NVA) por proyecto activo por mes, sobre el portafolio '
                'de 13 proyectos de CNTXT. CT incluye todas las actividades de los tres perfiles del proceso '
                '(Líder, Director Ejecutivo y Director Creativo) según tiempos del VSM. Base: 182 h/mes.',
        formula='CU = CT (Costo Total de gestión por mes)  ÷  Número de proyectos activos',
        t_headers=['Concepto', 'Cálculo / Dato  (min/sem × 4,33 ÷ 60 = h/mes;  4,33 = 52 sem ÷ 12 meses)', 'Resultado'],
        t_cw=[3.6, 4.2, 2.64],
        t_rows=[
            ('Líder de Proyecto: 40,05 h/mes × $ 24.725 / h', 'VSM: 555 × 4,33 ÷ 60 = 40,05 h/mes', '$ 990.236'),
            ('Director Ejecutivo: 11,91 h/mes × $ 43.956 / h', 'VSM: 165 × 4,33 ÷ 60 = 11,91 h/mes', '$ 523.516'),
            ('Director Creativo: 8,66 h/mes × $ 32.967 / h', 'VSM: 120 × 4,33 ÷ 60 = 8,66 h/mes', '$ 285.494'),
            ('CT total de gestión (VA + NVA)', '', '$ 1.799.246 / mes'),
            ('Número de proyectos activos', '', '13 proyectos'),
            ('Cálculo CU línea base', '$ 1.799.246 ÷ 13', '$ 138.404 / proyecto / mes'),
            ('Línea base CU (redondeada)', '', '$ 138.400 / proyecto / mes'),
            ('Meta CU  (−35 %)', '$ 138.400 × 0,65', '$ 90.000 / proyecto / mes'),
            ('Ahorro esperado', '$ 138.400 − $ 90.000', '$ 48.400 / proyecto / mes'),
        ],
        entregable='Reporte_Mediciones_CNTXT_PT2.xlsx  (hoja IPT-4 CU)',
    ),
    dict(
        cod='IPT-5', tipo='Variable', color=VAR_C,
        nombre='Optimización de Puntos de Contacto con el Cliente en el Proceso Productivo (OPC)',
        unidad='Porcentaje (%) de subprocesos del ciclo productivo con contacto directo con el cliente',
        base='58,33', meta='25,00', var='-57,14 %',
        alcance='Porcentaje de subprocesos del ciclo productivo (12 actividades del VSM) en los cuales '
                'se tiene contacto directo con el cliente externo, desde el registro del dato operativo '
                'hasta la aprobación del hito por el cliente. Alcance idéntico en mediciones intermedia y de salida.',
        formula='OPC = (Subprocesos con contacto directo cliente ÷ Total subprocesos del ciclo)  × 100',
        t_headers=['Punto', 'Descripción (contacto directo con cliente externo)', 'Estado en meta'],
        t_cw=[0.85, 7.65, 1.94],
        t_rows=[
            ('P 1', 'Convocatoria y coordinación de reunión de avance con cliente (correo / llamada)', 'ELIMINADO — automatizado en plataforma'),
            ('P 2', 'Preparación de presentación de avance impresa para el cliente', 'ELIMINADO — dashboard digital'),
            ('P 3', 'Reunión presencial de avance con entrega de material impreso al cliente', 'Se conserva — reunión directiva'),
            ('P 4', 'Envío de planos y renders al cliente para revisión y aprobación', 'ELIMINADO — portal digital'),
            ('P 5', 'Recepción y procesamiento de comentarios del cliente (correo / verbal)', 'ELIMINADO — formulario digital'),
            ('P 6', 'Ciclo de ajustes por feedback del cliente y re-envío de entregables', 'ELIMINADO — trazabilidad en plataforma'),
            ('P 7', 'Confirmación de aprobación y escalamiento de hito con el cliente', 'Se conserva — aprobación digital'),
            ('', 'Línea base: 7 / 12 subprocesos = 58,33 %', ''),
            ('', 'Meta: 3 / 12 subprocesos conservados = 25,00 %   →   Variación: −57,14 %', ''),
        ],
        entregable='Reporte_Mediciones_CNTXT_PT2.xlsx  (hoja IPT-5 OPC)',
    ),
    dict(
        cod='IPT-6', tipo='Variable — Sostenibilidad', color=SOS_C,
        nombre='Impacto Ambiental: Consumo de Recursos por Servicio Prestado (IA)',
        unidad='Hojas de papel / mes',
        base='170,00', meta='145,00', var='-14,71 %',
        alcance='Consumo mensual de papel en procesos documentales de gestión de proyectos '
                '(portafolio de 13 proyectos activos). Inventario físico levantado en marzo 2026. '
                'Alcance idéntico en mediciones intermedia y de salida.',
        formula='IA = Σ (Frecuencia mensual  ×  Número de hojas por tipo de documento)',
        t_headers=['Documento', 'Descripción', 'Línea base', 'Meta', 'Δ  /  Acción'],
        t_cw=[1.1, 3.5, 1.35, 1.1, 3.39],
        t_rows=[
            ('Doc 1', 'Reportes ejecutivos impresos para equipo directivo', '40 h/mes', '15 h/mes', '−25 h. → Dashboard digital en Central Contexto'),
            ('Doc 2', 'Presentaciones de avance impresas para clientes', '60 h/mes', '55 h/mes', '−5 h.  → PDF digital (clientes exigen parcial físico)'),
            ('Doc 3', 'Planos y renders impresos para aprobación cliente', '30 h/mes', '30 h/mes', '0 h.   → Requerimiento cliente (físico obligatorio)'),
            ('Doc 4', 'Actas de seguimiento y fichas de entregables', '25 h/mes', '30 h/mes', '+5 h.  → Módulo de prerrequisitos genera más actas'),
            ('Doc 5', 'Copias de respaldo de información crítica', '15 h/mes', '15 h/mes', '0 h.   → Política interna de respaldo físico'),
            ('TOTAL', '', '170 h/mes', '145 h/mes', '−25 hojas/mes  (−14,71 %)'),
        ],
        entregable='Inventario_Papel_CNTXT_PT2_IA.xlsx',
    ),
]

TOTAL_PAGES = 8   # 1 portada + 1 portafolio + 6 detalle

PROYECTOS = [
    ('1',  'Made',   'POP-UP AAA',                      'Comercial',                    'Diseño'),
    ('2',  'Made',   'WELLNESS RESIDENCES',              'Parcelaciones y Condominios',  'Diseño & Visual'),
    ('3',  'Made',   'LA SENDA',                         'Parcelaciones y Condominios',  'Diseño & Visual'),
    ('4',  'Made',   'NATIVE SAN JOSÉ',                  'Parcelaciones y Condominios',  'Diseño & Visual'),
    ('5',  'Made',   'DON MATIAS',                       'Parcelaciones y Condominios',  'Diseño'),
    ('6',  'Made',   'CASA RODINA',                      'Vivienda Campestre',           'Diseño & Visual'),
    ('7',  'Made',   'CASA ESCULTA',                     'Vivienda Campestre',           'Diseño & Visual'),
    ('8',  'Select', 'CASA DIANA & HERIBERTO',           'Vivienda Campestre',           'Diseño & Visual'),
    ('9',  'Select', 'CASA ADRIANA MOCCIOLA & FELIPE',   'Vivienda Campestre',           'Diseño & Visual'),
    ('10', 'Select', 'CASA CARLOS & YOHANA',             'Vivienda Campestre',           'Diseño & Visual'),
    ('11', 'Select', 'CASA CARMEN & TONY',               'Vivienda Campestre',           'Diseño & Visual'),
    ('12', 'Select', 'CASA MAURICIO MARTINEZ',           'Vivienda Campestre',           'Diseño & Visual'),
    ('13', 'Select', 'CASA FELIPE SALDARRIAGA',          'Vivienda Campestre',           'Diseño & Visual'),
]


# ════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — PORTADA + TABLA RESUMEN
# ════════════════════════════════════════════════════════════════════════════
def pagina_portada(pdf):
    fig, ax = fig_ax()

    # Header
    r(ax, 0, H-1.70, W, 1.70, HEAD, z=2)
    r(ax, 0, H-1.70, W, 0.06, VA_C, z=3)   # línea verde
    ax.text(W/2, H-0.55, 'RESUMEN DE INDICADORES — PLAN DE TRABAJO 2',
            ha='center', va='center', fontsize=16, fontweight='bold', color=WHITE, zorder=3)
    ax.text(W/2, H-0.95, 'CONTEXTO ARQUITECTURA S.A.S.  (CNTXT Casa de Diseño)',
            ha='center', va='center', fontsize=11, color='#aec6e8', zorder=3)
    ax.text(W/2, H-1.22, 'Línea de Servicio: Productividad Operacional  |  NIT: 900.948.892-7',
            ha='center', va='center', fontsize=9, color='#7fb3d3', zorder=3)
    ax.text(W/2, H-1.46, 'Consultor: Miguel Bernardo Rodríguez Torres — INDUNNOVA S.A.S.',
            ha='center', va='center', fontsize=9, color='#7fb3d3', zorder=3)
    ax.text(W/2, H-1.65, 'Período intervención: 09 abril – 18 junio 2026  |  Período línea base: Marzo 2026',
            ha='center', va='center', fontsize=8.5, color='#7fb3d3', zorder=3)

    # ── Tabla resumen ──────────────────────────────────────────────────────
    # Anchos fijos (suma = TW = 10.44)
    CW = [1.10, 3.56, 1.36, 1.36, 0.92, 0.80, 1.34]
    # Posiciones X acumuladas desde MX
    CX = [MX + sum(CW[:j]) for j in range(len(CW))]
    HEADS = ['Código', 'Indicador', 'Línea Base', 'Meta', 'Variación', 'Tipo', 'Unidad']
    ROW_H = 0.57
    TABLE_TOP = H - 1.82

    # Encabezado
    r(ax, MX, TABLE_TOP-0.34, TW, 0.34, HEAD, z=3)
    for j, h in enumerate(HEADS):
        ax.text(CX[j]+CW[j]/2, TABLE_TOP-0.17, h, ha='center', va='center',
                fontsize=8, fontweight='bold', color=WHITE, zorder=4)

    def _short(v):
        """Quita el sufijo ',00000' para mostrar valores compactos en tabla resumen."""
        return v[:-6] if v.endswith(',00000') else v

    for i, ind in enumerate(indicadores):
        yy = TABLE_TOP - 0.34 - (i+1)*ROW_H
        bg = WHITE if i % 2 == 0 else LGRAY
        r(ax, MX, yy, TW, ROW_H, bg, ec=DGRAY, lw=0.5, z=2)

        # Separadores de columna
        cx = MX
        for j in range(len(CW)-1):
            cx += CW[j]
            ax.plot([cx, cx], [yy, yy+ROW_H], color=DGRAY, lw=0.5, zorder=3)

        # Badge código
        r(ax, CX[0]+0.05, yy+0.12, CW[0]-0.10, 0.33, ind['color'], z=3)
        ax.text(CX[0]+CW[0]/2, yy+0.285, ind['cod'],
                ha='center', va='center', fontsize=8, fontweight='bold', color=WHITE, zorder=4)

        # Valores — nombre truncado para que quepa en la columna (CW[1]=3.56)
        nombre_short = ind['nombre']
        if len(nombre_short) > 43:
            nombre_short = nombre_short[:41] + '…'

        # Línea base y meta sin decimales triviales para que quepan en columnas 1.36 in
        vals = [nombre_short, _short(ind['base']), _short(ind['meta']), ind['var'],
                ind['tipo'].split('—')[0].strip(), ind['unidad']]
        aligns = ['left','center','center','center','center','left']
        colors_  = [DARK, NVA_C, VA_C, ind['color'], MID, MID]
        bolds_   = [False, True, True, True, False, False]
        sizes_   = [7.5, 8.5, 8.5, 8.5, 7.5, 7]

        for j, (v, al, col, bo, sz) in enumerate(
                zip(vals, aligns, colors_, bolds_, sizes_)):
            max_c = int(CW[j+1] / 0.062)
            v_show = v if len(v) <= max_c else v[:max_c-1] + '…'
            xp = CX[j+1] + (0.10 if al == 'left' else CW[j+1]/2)
            ax.text(xp, yy+ROW_H/2, v_show, ha=al, va='center',
                    fontsize=sz, color=col, fontweight='bold' if bo else 'normal', zorder=4)

    # Nota
    NOTE_Y = TABLE_TOP - 0.34 - 6*ROW_H - 0.12
    r(ax, MX, NOTE_Y-0.28, TW, 0.28, '#eafaf1', ec=VA_C, lw=0.8, z=2)
    ax.text(MX+0.18, NOTE_Y-0.14,
            '✔  Todos los indicadores superan el mínimo del 8 % exigido por Colombia Productiva.  '
            'Menor variación: IPT-6 IA con −14,71 %.',
            ha='left', va='center', fontsize=8, color='#1a5c33', zorder=3)

    footer_band(ax, 1, TOTAL_PAGES)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — PORTAFOLIO DE 13 PROYECTOS ACTIVOS
# ════════════════════════════════════════════════════════════════════════════
def pagina_portafolio(pdf):
    fig, ax = fig_ax()

    header_global(ax, 'PORTAFOLIO DE PROYECTOS ACTIVOS — Alcance de la Medición (Marzo 2026)')

    cursor = H - 0.62

    # Título de sección
    section_label(ax, MX, cursor, 'Portafolio de 13 Proyectos Activos — Base de la Medición', HEAD)
    cursor -= 0.30

    # Nota introductoria
    nota = ('Los indicadores IPT-1, IPT-2, IPT-3, IPT-4 e IPT-6 se midieron sobre el portafolio completo '
            'de 13 proyectos activos simultáneos de CNTXT en marzo de 2026. '
            'El alcance se mantendrá idéntico en las mediciones intermedia y de salida.')
    for li, line in enumerate(textwrap.wrap(nota, 130)):
        ax.text(MX + 0.15, cursor - 0.05 - li * 0.188, line,
                ha='left', va='top', fontsize=8.5, color=DARK, zorder=3)
    cursor -= len(textwrap.wrap(nota, 130)) * 0.188 + 0.20

    # Tabla de proyectos
    t_headers = ['#', 'Modelo', 'Proyecto', 'Categoría', 'Línea Operativa']
    t_cw      = [0.42, 1.10, 3.80, 3.30, 1.82]
    col_xs    = [sum(t_cw[:j]) for j in range(len(t_cw))]
    ROW_H     = 0.36
    full_w    = sum(t_cw)
    HDR_H     = 0.30

    # Encabezado tabla
    r(ax, MX, cursor - HDR_H, full_w, HDR_H, HEAD, z=3)
    for j, h in enumerate(t_headers):
        cx = MX + col_xs[j] + t_cw[j] / 2
        ax.text(cx, cursor - HDR_H / 2, h, ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=WHITE, zorder=4)

    y = cursor - HDR_H
    for i, (num, modelo, proyecto, categoria, linea) in enumerate(PROYECTOS):
        bg = WHITE if i % 2 == 0 else LGRAY
        modelo_color = '#1a5276' if modelo == 'Select' else '#145a32'
        r(ax, MX, y - ROW_H, full_w, ROW_H, bg, ec=DGRAY, lw=0.5, z=3)

        # Separadores de columna
        cx = MX
        for j in range(len(t_cw) - 1):
            cx += t_cw[j]
            ax.plot([cx, cx], [y - ROW_H, y], color=DGRAY, lw=0.5, zorder=4)

        # Celdas
        datos = [num, modelo, proyecto, categoria, linea]
        aligns = ['center', 'center', 'left', 'left', 'center']
        for j, (dato, al) in enumerate(zip(datos, aligns)):
            px = MX + col_xs[j] + (0.10 if al == 'left' else t_cw[j] / 2)
            color_txt = modelo_color if j == 1 else DARK
            bold_txt  = (j == 1)
            ax.text(px, y - ROW_H / 2, dato, ha=al, va='center',
                    fontsize=8.5, color=color_txt,
                    fontweight='bold' if bold_txt else 'normal', zorder=4)
        y -= ROW_H

    # Borde exterior tabla
    r(ax, MX, y, full_w, cursor - y, 'none', ec=HEAD, lw=1.0, z=5)

    # Leyenda modelos
    leg_y = y - 0.18
    r(ax, MX, leg_y - 0.26, full_w, 0.26, '#eaf4fb', ec='#2471a3', lw=0.8, z=2)
    ax.text(MX + 0.18, leg_y - 0.13,
            '■ Made (7 proyectos): parcelaciones, condominios, vivienda campestre y comercial — '
            '■ Select (6 proyectos): vivienda campestre personalizada.',
            ha='left', va='center', fontsize=7.5, color='#154360', zorder=3)

    footer_band(ax, 2, TOTAL_PAGES)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ════════════════════════════════════════════════════════════════════════════
# PÁGINAS 3–8 — DETALLE POR INDICADOR (1 por página)
# ════════════════════════════════════════════════════════════════════════════
def pagina_indicador(pdf, ind, page):
    fig, ax = fig_ax()

    # ── Header global ─────────────────────────────────────────────────────
    r(ax, 0, H-0.48, W, 0.48, HEAD, z=3)
    ax.text(W/2, H-0.17, 'RESUMEN DE INDICADORES — PLAN DE TRABAJO 2',
            ha='center', va='center', fontsize=11, fontweight='bold', color=WHITE, zorder=4)
    ax.text(W/2, H-0.36, 'CONTEXTO ARQUITECTURA S.A.S. (CNTXT)  |  Productividad Operacional  |  Línea base: Marzo 2026',
            ha='center', va='center', fontsize=7, color='#aec6e8', zorder=4)

    # ── Banda del indicador ───────────────────────────────────────────────
    BAND_TOP = H - 0.48
    BAND_H   = 0.60
    r(ax, MX, BAND_TOP-BAND_H, TW, BAND_H, ind['color'], z=3)
    ax.text(MX+0.20, BAND_TOP-BAND_H/2, f"{ind['cod']}  —  {ind['nombre']}",
            ha='left', va='center', fontsize=11, fontweight='bold', color=WHITE, zorder=4)
    r(ax, W-MX-1.45, BAND_TOP-BAND_H+0.14, 1.40, BAND_H-0.28, WHITE, alpha=0.18, z=4)
    ax.text(W-MX-0.74, BAND_TOP-BAND_H/2, f"[ {ind['tipo']} ]",
            ha='center', va='center', fontsize=8, color=WHITE, zorder=5)

    cursor = BAND_TOP - BAND_H - 0.14   # Y libre

    # ── Fila de métricas (4 cajas) ────────────────────────────────────────
    BOX_H   = 0.88
    BOX_GAP = 0.14
    n_boxes = 4
    BOX_W   = (TW - (n_boxes-1)*BOX_GAP) / n_boxes

    boxes = [
        ('Línea Base',        ind['base'],  NVA_C, NVA_C),
        ('Mes de Medición',   'Marzo 2026', HEAD,  HEAD),
        ('Meta del Indicador',ind['meta'],  VA_C,  VA_C),
        ('Variación Esperada',ind['var'],   ind['color'], ind['color']),
    ]
    for k, (lbl, val, lbg, vcol) in enumerate(boxes):
        bx = MX + k*(BOX_W+BOX_GAP)
        metric_box(ax, bx, cursor-BOX_H, BOX_W, BOX_H, lbl, val, vcol, lbg)

    # Unidad debajo de los boxes
    cursor -= BOX_H + 0.10
    r(ax, MX, cursor-0.27, TW, 0.27, LGRAY, ec='none', z=2)
    ax.text(MX+0.15, cursor-0.135, f"Unidad de medida:  {ind['unidad']}",
            ha='left', va='center', fontsize=8.5, color=MID, fontstyle='italic', zorder=3)
    cursor -= 0.42   # gap suficiente antes del label de sección

    # ── Sección: Cálculo de la medición ───────────────────────────────────
    section_label(ax, MX, cursor, 'Cálculo de la Medición', ind['color'])
    cursor -= 0.30

    # Alcance (wrap ~115 chars)
    ax.text(MX+0.12, cursor-0.05, 'Alcance:',
            ha='left', va='top', fontsize=8.5, fontweight='bold', color=HEAD, zorder=3)
    alcance_lines = textwrap.wrap(ind['alcance'], 115)
    for li, line in enumerate(alcance_lines):
        ax.text(MX+1.05, cursor - 0.05 - li*0.188, line,
                ha='left', va='top', fontsize=8.5, color=DARK, zorder=3)
    alcance_h = len(alcance_lines)*0.188 + 0.12
    cursor -= alcance_h + 0.06

    # Fórmula (banda destacada)
    FORM_H = 0.34
    r(ax, MX, cursor-FORM_H, TW, FORM_H, HEAD, alpha=0.10, z=2)
    ax.text(MX+0.15, cursor-FORM_H/2, f"Fórmula:   {ind['formula']}",
            ha='left', va='center', fontsize=8.5, color=HEAD, fontweight='bold',
            fontstyle='italic', zorder=3)
    cursor -= FORM_H + 0.18

    # ── Tabla de detalle ──────────────────────────────────────────────────
    section_label(ax, MX, cursor, 'Detalle del Cálculo', ind['color'])
    cursor -= 0.26

    col_xs = [sum(ind['t_cw'][:j]) for j in range(len(ind['t_cw']))]
    y_bot = table(ax, MX, cursor,
                  col_xs, ind['t_cw'],
                  ind['t_headers'], ind['t_rows'],
                  ind['color'], row_h=0.30, fontsize_body=7.5)

    # ── Entregable ────────────────────────────────────────────────────────
    ENT_H = 0.30
    ent_y = max(y_bot - 0.14, 0.34 + ENT_H)
    r(ax, MX, ent_y-ENT_H, TW, ENT_H, '#eaf4fb', ec='#2471a3', lw=0.8, z=2)
    ax.text(MX+0.18, ent_y-ENT_H/2,
            f"Entregable de soporte:   {ind['entregable']}",
            ha='left', va='center', fontsize=8, color='#154360',
            fontstyle='italic', zorder=3)

    footer_band(ax, page, TOTAL_PAGES)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


# ════════════════════════════════════════════════════════════════════════════
# GENERAR PDF
# ════════════════════════════════════════════════════════════════════════════
with PdfPages(OUT) as pdf:
    pagina_portada(pdf)
    pagina_portafolio(pdf)
    for i, ind in enumerate(indicadores):
        pagina_indicador(pdf, ind, page=i+3)

    d = pdf.infodict()
    d['Title']   = 'Resumen Indicadores Plan de Trabajo 2 — CNTXT'
    d['Author']  = 'Miguel Bernardo Rodríguez Torres — INDUNNOVA S.A.S.'
    d['Subject'] = 'Fábricas de Productividad — Colombia Productiva'

size_mb = os.path.getsize(OUT) / 1024 / 1024
print(f'✓  {os.path.basename(OUT)}  —  {size_mb:.2f} MB  —  8 páginas')
