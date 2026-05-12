"""
Genera el VSM visual (Value Stream Map) de CNTXT como imágenes PNG.
Archivos de salida:
  - VSM_Proceso_Actual_CNTXT.png
  - VSM_Proceso_Futuro_CNTXT.png
  - VSM_TCP_CNTXT.png
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── Colores ──────────────────────────────────────────────────────────────────
VA_C    = '#27ae60'
NVA_C   = '#c0392b'
HEAD_C  = '#1a3a5c'
DATA_C  = '#eaf0fb'
BG_C    = '#f7f9fc'
ARROW_C = '#2c3e50'
CRIT_C  = '#f39c12'

# ── Helpers ───────────────────────────────────────────────────────────────────
def process_box(ax, x, y_top, w, h_box, h_data, p):
    """Dibuja caja de proceso + caja de datos + etiqueta responsable."""
    color = VA_C if p['type'] == 'VA' else NVA_C
    y_box  = y_top - h_box
    y_data = y_box  - h_data

    # — Caja proceso —
    ax.add_patch(Rectangle((x, y_box), w, h_box,
                            facecolor=color, edgecolor='#1a1a2e', linewidth=1.8, zorder=3))
    # ID
    ax.text(x+0.18, y_top-0.13, f"P{p['id']}",
            ha='left', va='top', fontsize=7, color='white', fontweight='bold',
            alpha=0.85, zorder=4)
    # Badge VA/NVA
    ax.add_patch(Rectangle((x+w-0.62, y_top-0.36), 0.58, 0.26,
                            facecolor='white', edgecolor='none', alpha=0.25, zorder=4))
    ax.text(x+w-0.33, y_top-0.23, p['type'],
            ha='center', va='center', fontsize=6.5, color='white', fontweight='bold', zorder=5)
    # Nombre
    ax.text(x+w/2, y_box+h_box/2, p['name'],
            ha='center', va='center', fontsize=7.5, color='white',
            fontweight='bold', multialignment='center', zorder=4)
    # Crítico
    if p.get('critico'):
        ax.text(x+0.18, y_box+0.18, '⚡',
                ha='left', va='bottom', fontsize=10, color=CRIT_C, zorder=5)

    # — Caja de datos —
    ax.add_patch(Rectangle((x, y_data), w, h_data,
                            facecolor=DATA_C, edgecolor='#1a1a2e', linewidth=1.2, zorder=3))
    lines = [
        f"Frec: {p['freq']}",
        f"T/ciclo: {p['tc']}",
        f"Total: {p['total']}",
    ]
    for k, txt in enumerate(lines):
        yy = y_data + h_data * (0.8 - k*0.28)
        ax.text(x+w/2, yy, txt, ha='center', va='center',
                fontsize=7, color='#1a1a2e',
                fontweight='bold' if k == 2 else 'normal', zorder=4)

    # — Responsable —
    ax.text(x+w/2, y_top+0.06, p['resp'],
            ha='center', va='bottom', fontsize=6.5, color='#444', style='italic', zorder=4)

    return y_data   # retorna y inferior del bloque

def push_arrow(ax, x1, x2, y_mid, label='PUSH'):
    ax.annotate('', xy=(x2, y_mid), xytext=(x1, y_mid),
                arrowprops=dict(arrowstyle='->', color=ARROW_C, lw=1.8), zorder=5)
    ax.text((x1+x2)/2, y_mid+0.16, label,
            ha='center', va='bottom', fontsize=5.5, color='#666', zorder=5)

def pull_arrow(ax, x1, x2, y_mid, label='PULL'):
    ax.annotate('', xy=(x2, y_mid), xytext=(x1, y_mid),
                arrowprops=dict(arrowstyle='->', color=ARROW_C, lw=1.8), zorder=5)
    ax.text((x1+x2)/2, y_mid+0.16, label,
            ha='center', va='bottom', fontsize=5.5, color='#666', zorder=5)

def down_arrow(ax, x, y_from, y_to):
    ax.annotate('', xy=(x, y_to), xytext=(x, y_from),
                arrowprops=dict(arrowstyle='->', color=ARROW_C, lw=2.5), zorder=5)

def timeline_bar(ax, x0, y0, total_w, total_time, segments, labels=True):
    """
    Dibuja barra de timeline proporcional.
    segments = lista de (tiempo, tipo 'VA'|'NVA', label)
    """
    x = x0
    for (t, tipo, lbl) in segments:
        w = total_w * t / total_time
        c = VA_C if tipo == 'VA' else NVA_C
        ax.add_patch(Rectangle((x, y0), w, 0.55,
                                facecolor=c, edgecolor='white', linewidth=0.8, zorder=3))
        if labels and w > 0.6:
            ax.text(x+w/2, y0+0.275, lbl,
                    ha='center', va='center', fontsize=6, color='white',
                    fontweight='bold', zorder=4)
        x += w


# ════════════════════════════════════════════════════════════════════════════
# 1. VSM PROCESO ACTUAL
# ════════════════════════════════════════════════════════════════════════════
def vsm_actual():
    W, H = 24.0, 16.0
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis('off')
    fig.patch.set_facecolor(BG_C)
    ax.set_facecolor(BG_C)

    BW, BH, DH, GAP = 3.55, 2.2, 1.05, 0.45
    STEP = BW + GAP
    X0 = 0.22

    R1_TOP = 14.2   # top del process-box fila 1
    R2_TOP =  8.0   # top del process-box fila 2

    # ── Header ──────────────────────────────────────────────────────────────
    ax.add_patch(Rectangle((0, H-1.6), W, 1.6, facecolor=HEAD_C, zorder=2))
    ax.text(W/2, H-0.62, 'VALUE STREAM MAP — PROCESO ACTUAL DE GESTIÓN DE PROYECTOS',
            ha='center', va='center', fontsize=15, fontweight='bold', color='white', zorder=3)
    ax.text(W/2, H-1.3,
            'CONTEXTO ARQUITECTURA S.A.S. (CNTXT)  |  Línea: Productividad Operacional  |'
            '  Período línea base: Marzo 2026  |  13 proyectos activos',
            ha='center', va='center', fontsize=8.5, color='#aec6e8', zorder=3)

    # ── Leyenda ──────────────────────────────────────────────────────────────
    leg_patches = [
        mpatches.Patch(facecolor=VA_C,   edgecolor='black', label='Agrega Valor (VA)'),
        mpatches.Patch(facecolor=NVA_C,  edgecolor='black', label='No Agrega Valor (NVA)'),
        Line2D([0],[0], marker='$⚡$', color='w', markerfacecolor=CRIT_C,
               markersize=12, label='Punto crítico de desperdicio'),
    ]
    ax.legend(handles=leg_patches, loc='upper right',
              bbox_to_anchor=(0.999, 0.888), fontsize=8.5, framealpha=0.92,
              edgecolor='#bbb')

    # ── Fila 1: P1 → P6 ──────────────────────────────────────────────────────
    row1 = [
        dict(id=1,  name='Registro inicial\nen herramienta\nde origen',
             resp='Líder Proyecto', type='VA',
             freq='5x/sem', tc='12 min', total='60 min/sem', critico=False),
        dict(id=2,  name='Transcripción\na tabla\npara dummies',
             resp='Líder Proyecto', type='NVA',
             freq='3x/sem', tc='25 min', total='75 min/sem', critico=True),
        dict(id=3,  name='Transferencia\nDummies →\nTabla Gruesa',
             resp='Asistente / Líder', type='NVA',
             freq='2x/sem', tc='20 min', total='40 min/sem', critico=True),
        dict(id=4,  name='Alimentación\ndashboards\nCentral Contexto',
             resp='Asistente', type='NVA',
             freq='1x/sem', tc='30 min', total='30 min/sem', critico=True),
        dict(id=5,  name='Búsqueda info\ndispersa\n(Drive/Sheets/Mail)',
             resp='Líder Proyecto', type='NVA',
             freq='5x/sem', tc='20 min', total='100 min/sem', critico=True),
        dict(id=6,  name='Consolidación\nreporte\nejecutivo',
             resp='Líder Proyecto', type='NVA',
             freq='1x/sem', tc='45 min', total='45 min/sem', critico=True),
    ]
    row1_xs = [X0 + i*STEP for i in range(6)]

    for i, p in enumerate(row1):
        process_box(ax, row1_xs[i], R1_TOP, BW, BH, DH, p)

    for i in range(5):
        push_arrow(ax,
                   row1_xs[i]+BW, row1_xs[i+1],
                   R1_TOP - BH/2)

    # ── Flecha bajada: P6 → P7 (misma columna, idx=5) ───────────────────────
    cx6 = row1_xs[5] + BW/2
    y_from = R1_TOP - BH - DH
    y_to   = R2_TOP + 0.12
    # línea vertical con curva
    ax.annotate('', xy=(cx6, y_to), xytext=(cx6, y_from),
                arrowprops=dict(arrowstyle='->', color=ARROW_C, lw=2.5,
                                connectionstyle='arc3,rad=0'), zorder=5)
    ax.text(cx6+0.22, (y_from+y_to)/2, '↓ continúa',
            ha='left', va='center', fontsize=7, color='#666', style='italic')

    # ── Fila 2: P12 ← P11 ← … ← P7 (visual izq→der = P12,11,10,9,8,7) ──────
    row2 = [
        dict(id=12, name='Reunión Coffee\nequipo directivo\n(decisión correctiva)',
             resp='Equipo Directivo', type='VA',
             freq='1x/sem', tc='60 min', total='60 min/sem', critico=False),
        dict(id=11, name='Coordinación\ncon clientes\n(llamadas / visitas)',
             resp='Líder Proyecto', type='VA',
             freq='5x/sem', tc='30 min', total='150 min/sem', critico=False),
        dict(id=10, name='Revisión técnica\nde entregables',
             resp='Director Creativo', type='VA',
             freq='1x/sem', tc='60 min', total='60 min/sem', critico=False),
        dict(id=9,  name='Revisión y cruce\ninfo. financiera\n(CASH)',
             resp='Director Ejecutivo', type='VA',
             freq='1x/sem', tc='90 min', total='90 min/sem', critico=False),
        dict(id=8,  name='Reconciliación\ncostos reales\nvs. presupuesto',
             resp='Líder / Dir. Ejec.', type='NVA',
             freq='1x/sem', tc='30 min', total='30 min/sem', critico=True),
        dict(id=7,  name='Actualización\ncronogramas\nGoogle Sheets',
             resp='Líder Proyecto', type='NVA',
             freq='2x/sem', tc='15 min', total='30 min/sem', critico=True),
    ]
    row2_xs = [X0 + i*STEP for i in range(6)]   # P12=idx0, P7=idx5

    for i, p in enumerate(row2):
        process_box(ax, row2_xs[i], R2_TOP, BW, BH, DH, p)

    # Flechas fila 2: apuntan a la IZQUIERDA (flujo P7→P12 = idx5→0)
    for i in range(5, 0, -1):
        pull_arrow(ax,
                   row2_xs[i],          # origen: lado izq de P actual
                   row2_xs[i-1]+BW,     # destino: lado der de P siguiente
                   R2_TOP - BH/2, label='')

    # ── Símbolos inicio / salida ──────────────────────────────────────────────
    # Inicio (arriba izq)
    ax.add_patch(Rectangle((0.02, R1_TOP-BH), 0.17, BH,
                            facecolor='#2980b9', edgecolor='#1a1a2e', linewidth=1.5, zorder=3))
    ax.text(0.105, R1_TOP-BH/2, 'IN\nIC\nIO',
            ha='center', va='center', fontsize=5.5, color='white', fontweight='bold', zorder=4)
    ax.annotate('', xy=(row1_xs[0], R1_TOP-BH/2), xytext=(0.19, R1_TOP-BH/2),
                arrowprops=dict(arrowstyle='->', color=ARROW_C, lw=1.8), zorder=5)

    # Salida (abajo izq, después de P12)
    ax.add_patch(Rectangle((0.02, R2_TOP-BH), 0.17, BH,
                            facecolor='#8e44ad', edgecolor='#1a1a2e', linewidth=1.5, zorder=3))
    ax.text(0.105, R2_TOP-BH/2, 'DE\nCI\nSI\nÓN',
            ha='center', va='center', fontsize=5.5, color='white', fontweight='bold', zorder=4)
    ax.annotate('', xy=(0.19, R2_TOP-BH/2), xytext=(row2_xs[0], R2_TOP-BH/2),
                arrowprops=dict(arrowstyle='->', color=ARROW_C, lw=1.8), zorder=5)

    # ── Timeline ──────────────────────────────────────────────────────────────
    TL_Y = 3.4
    TL_X0 = X0
    TL_W = 23.4

    total = 700
    # Orden de flujo (P1→P12): tipo, minutos totales/sem
    segs_flow = [
        (60,  'VA',  'P1\n60'),
        (75,  'NVA', 'P2\n75'),
        (40,  'NVA', 'P3\n40'),
        (30,  'NVA', 'P4\n30'),
        (100, 'NVA', 'P5\n100'),
        (45,  'NVA', 'P6\n45'),
        (30,  'NVA', 'P7\n30'),
        (30,  'NVA', 'P8\n30'),
        (90,  'VA',  'P9\n90'),
        (60,  'VA',  'P10\n60'),
        (150, 'VA',  'P11\n150'),
        (60,  'VA',  'P12\n60'),
    ]
    ax.text(TL_X0-0.1, TL_Y+1.05, 'TIMELINE (min/semana):',
            ha='left', va='bottom', fontsize=8, color=HEAD_C, fontweight='bold')
    timeline_bar(ax, TL_X0, TL_Y+0.5, TL_W, total, segs_flow, labels=True)

    # Barra NVA total
    nva_total = 350   # 280 de Líder (TNVA indicador) + 70 otros NVA
    tnva_w = TL_W * 280 / total
    ax.add_patch(Rectangle((TL_X0, TL_Y+0.05), TL_W * nva_total/total, 0.38,
                            facecolor='#7f8c8d', edgecolor='white', linewidth=0.5, alpha=0.35, zorder=3))
    ax.add_patch(Rectangle((TL_X0, TL_Y+0.05), tnva_w, 0.38,
                            facecolor=NVA_C, edgecolor='white', linewidth=0.5, alpha=0.55, zorder=3))
    ax.text(TL_X0 + tnva_w/2, TL_Y+0.24,
            'TNVA Indicador: 280 min/sem (Líder)',
            ha='center', va='center', fontsize=6.5, color='white', fontweight='bold', zorder=4)

    # ── Caja resumen ──────────────────────────────────────────────────────────
    ax.add_patch(Rectangle((X0, 0.25), TL_W, 2.9,
                            facecolor='white', edgecolor='#bbb', linewidth=1.2,
                            alpha=0.7, zorder=2))
    metrics = [
        ('Lead Time total', '700 min/sem', '(12 h / semana)'),
        ('Tiempo NVA total', '350 min/sem', '(50%)'),
        ('TNVA — Indicador IPT-1', '280 min/sem', '(activ. Líder de Proyecto)'),
        ('Tiempo VA', '420 min/sem', '(60%)'),
        ('Eficiencia del proceso VA/LT', '60 %', ''),
        ('Nº subprocesos NVA', '7 de 12', 'con 5 puntos críticos ⚡'),
    ]
    cols = 3
    for idx, (lbl, val, note) in enumerate(metrics):
        col = idx % cols
        row = idx // cols
        mx = X0 + 0.4 + col * (TL_W/cols)
        my = 2.85 - row * 1.2
        ax.text(mx, my,      lbl,  fontsize=7.5, color='#555', va='bottom')
        ax.text(mx, my-0.42, val,  fontsize=11, color=HEAD_C, fontweight='bold', va='bottom')
        if note:
            ax.text(mx, my-0.80, note, fontsize=7, color='#888', va='bottom', style='italic')

    ax.text(W/2, 0.10,
            'Entregable — Indicadores IPT-1 TNVA e IPT-2 TCP  |  CNTXT — Fábricas de Productividad — Colombia Productiva',
            ha='center', va='bottom', fontsize=7.5, color='#999')

    fig.savefig(os.path.join(OUT, 'VSM_Proceso_Actual_CNTXT.png'),
                dpi=150, bbox_inches='tight', facecolor=BG_C)
    plt.close(fig)
    print('✓  VSM_Proceso_Actual_CNTXT.png')


# ════════════════════════════════════════════════════════════════════════════
# 2. VSM PROCESO FUTURO
# ════════════════════════════════════════════════════════════════════════════
def vsm_futuro():
    W, H = 22.0, 12.0
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis('off')
    fig.patch.set_facecolor(BG_C)
    ax.set_facecolor(BG_C)

    BW, BH, DH, GAP = 3.2, 2.0, 1.0, 0.5
    STEP = BW + GAP
    X0 = 0.4
    R1_TOP = 9.6

    # Header
    ax.add_patch(Rectangle((0, H-1.5), W, 1.5, facecolor=HEAD_C, zorder=2))
    ax.text(W/2, H-0.6, 'VALUE STREAM MAP — PROCESO FUTURO REDISEÑADO',
            ha='center', va='center', fontsize=14, fontweight='bold', color='white', zorder=3)
    ax.text(W/2, H-1.15,
            'Meta: TNVA = 196 min/sem (−30%) | TCP = 16 h hábiles (−66.67%)  |  Central Contexto 2.0',
            ha='center', va='center', fontsize=8.5, color='#aec6e8', zorder=3)

    leg_patches = [
        mpatches.Patch(facecolor=VA_C,  edgecolor='black', label='Agrega Valor (VA)'),
        mpatches.Patch(facecolor=NVA_C, edgecolor='black', label='No Agrega Valor (NVA) — reducido'),
        mpatches.Patch(facecolor='#95a5a6', edgecolor='black', label='Eliminado (vs proceso actual)'),
    ]
    ax.legend(handles=leg_patches, loc='upper right',
              bbox_to_anchor=(0.999, 0.875), fontsize=8, framealpha=0.92)

    row = [
        dict(id=1, name='Registro único\nen Central\nContexto 2.0',
             resp='Líder Proyecto', type='VA',
             freq='5x/sem', tc='12 min', total='60 min/sem',
             mejora='Fuente única de verdad.\nElimina transcripciones.', critico=False),
        dict(id=2, name='Búsqueda info\ncentralizada\n(1 plataforma)',
             resp='Líder Proyecto', type='NVA',
             freq='5x/sem', tc='8 min', total='40 min/sem',
             mejora='−60% vs línea base\n(100→40 min/sem)', critico=False),
        dict(id=3, name='Actualización\ncronogramas\n(validación humana)',
             resp='Líder Proyecto', type='NVA',
             freq='2x/sem', tc='15 min', total='30 min/sem',
             mejora='Se mantiene:\nrequiere validación.', critico=False),
        dict(id=4, name='Reconciliación\ncostos\n(automática + OK)',
             resp='Líder / Dir. Ejec.', type='NVA',
             freq='1x/sem', tc='6 min', total='6 min/sem',
             mejora='−80% vs línea base\n(30→6 min/sem)', critico=False),
        dict(id=5, name='Reporte ejecutivo\nautomático\ndesde dashboards',
             resp='Sistema', type='VA',
             freq='1x/sem', tc='0 min', total='0 min/sem',
             mejora='ELIMINADO el trabajo\nmanual (−45 min/sem)', critico=False),
        dict(id=6, name='Reunión Coffee\n+ decisión\ncon datos en vivo',
             resp='Equipo Directivo', type='VA',
             freq='1x/sem', tc='60 min', total='60 min/sem',
             mejora='Decisión informada\ncon dashboard RT.', critico=False),
    ]
    xs = [X0 + i*STEP for i in range(6)]

    # Dibujar procesos
    for i, p in enumerate(row):
        if p['total'] == '0 min/sem':
            # Proceso eliminado — caja gris
            y_box = R1_TOP - BH
            ax.add_patch(Rectangle((xs[i], y_box), BW, BH,
                                    facecolor='#95a5a6', edgecolor='#1a1a2e',
                                    linewidth=1.8, zorder=3))
            ax.text(xs[i]+BW/2, y_box+BH/2, p['name'],
                    ha='center', va='center', fontsize=7.5, color='white',
                    fontweight='bold', multialignment='center', zorder=4)
            ax.text(xs[i]+BW/2, R1_TOP+0.06, p['resp'],
                    ha='center', va='bottom', fontsize=6.5, color='#444', style='italic')
            ax.text(xs[i]+BW/2, y_box-0.1, '✕ ELIMINADO',
                    ha='center', va='top', fontsize=8, color=NVA_C, fontweight='bold')
        else:
            process_box(ax, xs[i], R1_TOP, BW, BH, DH, p)

    # Flechas entre procesos
    for i in range(5):
        push_arrow(ax, xs[i]+BW, xs[i+1], R1_TOP-BH/2)

    # Cajas de mejora
    for i, p in enumerate(row):
        my = R1_TOP - BH - DH - 1.45
        ax.add_patch(Rectangle((xs[i]+0.1, my), BW-0.2, 1.15,
                                facecolor='#eafaf1', edgecolor='#27ae60',
                                linewidth=1, zorder=3, alpha=0.9))
        ax.text(xs[i]+0.2, my+1.05, '✔ Mejora:',
                ha='left', va='top', fontsize=6, color='#27ae60', fontweight='bold')
        ax.text(xs[i]+BW/2, my+0.52, p['mejora'],
                ha='center', va='center', fontsize=6.5, color='#1a5c33',
                multialignment='center')

    # Timeline futuro
    TL_Y = 1.2
    TL_X0 = X0
    TL_W = W - X0 - 0.4
    total_fut = 196
    segs_fut = [
        (60, 'VA',  'P1\n60'),
        (40, 'NVA', 'P2\n40'),
        (30, 'NVA', 'P3\n30'),
        (6,  'NVA', 'P4\n6'),
        (0,  'VA',  ''),
        (60, 'VA',  'P6\n60'),
    ]
    ax.text(TL_X0, TL_Y+0.7, 'TIMELINE META (min/semana):',
            ha='left', va='bottom', fontsize=8, color=HEAD_C, fontweight='bold')
    timeline_bar(ax, TL_X0, TL_Y+0.18, TL_W, 196, segs_fut, labels=True)

    # Resumen
    ax.add_patch(Rectangle((X0, 0.05), TL_W, 1.0,
                            facecolor='white', edgecolor='#bbb', linewidth=1,
                            alpha=0.8, zorder=2))
    summary = [
        ('TNVA meta', '196 min/sem', '−30%  ✓'),
        ('Tiempo VA', '120 min/sem', '(ciclo decisión + coord)'),
        ('Puntos NVA', '3 actividades', '(vs 7 en proceso actual)'),
        ('Eficiencia proceso', '≥ 61%', '(vs 60% actual)'),
    ]
    for idx, (lbl, val, note) in enumerate(summary):
        mx = X0 + 0.3 + idx * (TL_W/4)
        ax.text(mx, 0.82, lbl,  fontsize=7,  color='#555')
        ax.text(mx, 0.50, val,  fontsize=10, color=HEAD_C, fontweight='bold')
        ax.text(mx, 0.22, note, fontsize=6.5, color='#888', style='italic')

    fig.savefig(os.path.join(OUT, 'VSM_Proceso_Futuro_CNTXT.png'),
                dpi=150, bbox_inches='tight', facecolor=BG_C)
    plt.close(fig)
    print('✓  VSM_Proceso_Futuro_CNTXT.png')


# ════════════════════════════════════════════════════════════════════════════
# 3. TCP — CICLO DE GESTIÓN OPERATIVA
# ════════════════════════════════════════════════════════════════════════════
def vsm_tcp():
    W, H = 20.0, 11.0
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis('off')
    fig.patch.set_facecolor(BG_C)
    ax.set_facecolor(BG_C)

    # Header
    ax.add_patch(Rectangle((0, H-1.5), W, 1.5, facecolor=HEAD_C, zorder=2))
    ax.text(W/2, H-0.62, 'IPT-2 TCP — CICLO DE GESTIÓN OPERATIVA',
            ha='center', va='center', fontsize=14, fontweight='bold', color='white', zorder=3)
    ax.text(W/2, H-1.2,
            'Desde la ocurrencia del evento operativo hasta la decisión correctiva del equipo directivo  |  Período: Marzo 2026',
            ha='center', va='center', fontsize=8.5, color='#aec6e8', zorder=3)

    hitos = [
        dict(n=1, lbl='Ocurrencia\ndel evento\noperativo',
             base=0, fut=0, resp='Evento externo',
             mejora='Punto de partida (H0)'),
        dict(n=2, lbl='Detección /\nregistro\ndel evento',
             base=12, fut=1.5, resp='Líder Proyecto',
             mejora='Alerta automática\nde la plataforma'),
        dict(n=3, lbl='Consolidación\nen tabla\ngruesa',
             base=12, fut=0, resp='Asistente / Líder',
             mejora='ELIMINADA: datos\nya consolidados RT'),
        dict(n=4, lbl='Preparación\ndel reporte\npara reunión',
             base=16, fut=0, resp='Líder Proyecto',
             mejora='ELIMINADA: dashboard\nsiempre actualizado'),
        dict(n=5, lbl='Revisión por\nLíder antes\nde escalar',
             base=4, fut=3, resp='Líder Proyecto',
             mejora='−25%: info disponible\nsin compilación'),
        dict(n=6, lbl='Escalamiento\ny decisión\ndirectivos',
             base=4, fut=11.5, resp='Equipo Directivo',
             mejora='Decisión informada\ncon datos en vivo'),
    ]

    BW = 2.8
    GAP = 0.5
    STEP = BW + GAP
    X0 = 0.6
    Y_HITO = 8.5   # top de cajas de hito

    # Cajas de hito (top row)
    for i, h in enumerate(hitos):
        x = X0 + i * STEP
        color = '#2980b9' if h['base'] == 0 else ('#c0392b' if h['fut'] == 0 else '#e67e22')
        if h['fut'] == 0 and h['base'] > 0:
            color = '#95a5a6'  # eliminado

        ax.add_patch(Rectangle((x, Y_HITO-1.6), BW, 1.6,
                                facecolor=color, edgecolor='#1a1a2e', linewidth=1.6, zorder=3))
        ax.text(x+BW/2, Y_HITO-0.8, h['lbl'],
                ha='center', va='center', fontsize=8, color='white',
                fontweight='bold', multialignment='center', zorder=4)
        ax.text(x+0.12, Y_HITO-0.12, f"H{h['n']}",
                ha='left', va='top', fontsize=7, color='white', alpha=0.8, zorder=4)
        ax.text(x+BW/2, Y_HITO+0.08, h['resp'],
                ha='center', va='bottom', fontsize=7, color='#555', style='italic')

        # Flechas entre hitos
        if i < 5:
            ax.annotate('', xy=(x+BW+GAP, Y_HITO-0.8), xytext=(x+BW, Y_HITO-0.8),
                        arrowprops=dict(arrowstyle='->', color=ARROW_C, lw=2), zorder=5)

    # Barras comparativas (base vs futuro) por hito
    BAR_Y_BASE = 4.8
    BAR_Y_FUT  = 3.2
    MAX_H = 1.1
    max_val = 16

    ax.text(X0-0.3, BAR_Y_BASE+MAX_H+0.15, 'Línea base (h hábiles)',
            ha='left', va='bottom', fontsize=8.5, color=NVA_C, fontweight='bold')
    ax.text(X0-0.3, BAR_Y_FUT+MAX_H+0.15, 'Meta (h hábiles)',
            ha='left', va='bottom', fontsize=8.5, color=VA_C, fontweight='bold')

    for i, h in enumerate(hitos):
        x = X0 + i * STEP
        bw2 = BW * 0.4

        # Barra base
        if h['base'] > 0:
            bh = MAX_H * h['base'] / max_val
            ax.add_patch(Rectangle((x+BW/2-bw2/2, BAR_Y_BASE), bw2, bh,
                                    facecolor=NVA_C, edgecolor='#1a1a2e',
                                    linewidth=1, alpha=0.8, zorder=3))
            ax.text(x+BW/2, BAR_Y_BASE+bh+0.08, f"{h['base']}h",
                    ha='center', va='bottom', fontsize=8, color=NVA_C, fontweight='bold')
        else:
            ax.text(x+BW/2, BAR_Y_BASE+0.15, '0h\n(inicio)',
                    ha='center', va='bottom', fontsize=7, color='#999')

        # Barra futuro
        if h['fut'] > 0:
            fh = MAX_H * h['fut'] / max_val
            ax.add_patch(Rectangle((x+BW/2-bw2/2, BAR_Y_FUT), bw2, fh,
                                    facecolor=VA_C, edgecolor='#1a1a2e',
                                    linewidth=1, alpha=0.8, zorder=3))
            ax.text(x+BW/2, BAR_Y_FUT+fh+0.08, f"{h['fut']}h",
                    ha='center', va='bottom', fontsize=8, color=VA_C, fontweight='bold')
        else:
            ax.text(x+BW/2, BAR_Y_FUT+0.08,
                    'ELIMINADO' if h['base'] > 0 else '0h',
                    ha='center', va='bottom', fontsize=7,
                    color='#c0392b' if h['base'] > 0 else '#999', fontweight='bold')

        # Nota de mejora
        ax.text(x+BW/2, BAR_Y_FUT-0.35, h['mejora'],
                ha='center', va='top', fontsize=6.2, color='#1a5c33',
                multialignment='center', style='italic')

    # Totales
    ax.add_patch(Rectangle((0.1, 0.8), W-0.2, 1.9,
                            facecolor='white', edgecolor='#bbb', linewidth=1.2,
                            alpha=0.85, zorder=2))
    totals = [
        ('Lead Time LÍNEA BASE', '48 h hábiles', '(6 días hábiles promedio)', NVA_C),
        ('Lead Time META',       '16 h hábiles', '(2 días hábiles promedio)', VA_C),
        ('Reducción absoluta',   '32 h hábiles', 'por evento operativo',       HEAD_C),
        ('Variación porcentual', '−66.67 %',     'Indicador IPT-2 TCP ✓',     '#27ae60'),
    ]
    for idx, (lbl, val, note, col) in enumerate(totals):
        mx = 0.5 + idx * ((W-0.4)/4)
        ax.text(mx, 2.5,  lbl,  fontsize=7.5, color='#555')
        ax.text(mx, 2.12, val,  fontsize=12,  color=col, fontweight='bold')
        ax.text(mx, 1.78, note, fontsize=7,   color='#888', style='italic')

    ax.text(W/2, 0.08,
            'Entregable — Indicador IPT-2 TCP  |  CNTXT — Fábricas de Productividad — Colombia Productiva',
            ha='center', va='bottom', fontsize=7.5, color='#999')

    fig.savefig(os.path.join(OUT, 'VSM_TCP_CNTXT.png'),
                dpi=150, bbox_inches='tight', facecolor=BG_C)
    plt.close(fig)
    print('✓  VSM_TCP_CNTXT.png')


if __name__ == '__main__':
    vsm_actual()
    vsm_futuro()
    vsm_tcp()
    print('\nListo. Archivos en:', OUT)
