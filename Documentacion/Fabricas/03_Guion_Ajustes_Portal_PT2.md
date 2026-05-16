# Guión paso a paso para aplicar los ajustes del PT2 V3 en el portal

**Empresa**: CONTEXTO ARQUITECTURA S.A.S. (CNTXT) — PT2 `a0URQ00000LxlgM2AR`
**Fecha**: mayo 2026
**Tiempo estimado**: 25-30 minutos
**Límite del campo "Cálculo de la medición"**: 1.700 caracteres

---

## Instrucciones generales

1. Inicia sesión: `https://innpulsacolombia.my.site.com/fabricasdeproductividad/s/`
2. Para cada indicador abre la URL directa.
3. Edita campo por campo con el ícono de **lápiz** o el botón "Modificar" general.
4. **Guarda** después de cada cambio.
5. Adjunta los archivos del set V3.
6. Cuando los 6 indicadores estén listos, en el PT principal click en **"Enviar para Aprobación"**.

⚠️ **Tipo de Indicador**: el portal V2 ya está bien para los 6 (TNVA Fijo, TCP Variable, AD Fijo, CU Variable, OPC Variable, IA Fijo). **No modifiques este campo**.

⚠️ Archivos en: `/home/miguelrodriguez/repos/Contexto/Documentacion/Fabricas/v3_entregables/`

---

## 1️⃣ IPT-49179 — TNVA

**URL**: https://innpulsacolombia.my.site.com/fabricasdeproductividad/s/fp-indicadorplantrabajo-obj/a0LRQ00000N1bTJ2AZ/ipt49179

### Campos numéricos

| Campo | Antes | Nuevo |
|---|---|---|
| Línea base | 280,00000 | **3897,00000** |
| Meta del indicador | 196,00000 | **2728,00000** |
| Variación porcentual esperada | -30,00 | -30,00 (igual) |

### Cálculo de la medición (1.644 caracteres)

```
ALCANCE: Se mide el TNVA del macroproceso completo de servicio al cliente de CNTXT (7 macroetapas: Captación, Propuesta, Estructuración, Producción en 3 fases con HITOS 1/2/3, Aprobaciones, Entrega, Facturación). Sobre estas se ejecuta transversalmente el subproceso de Gestión Interna del Portafolio (12 actividades, 5 VA + 7 NVA, ejecutadas por Líder de Proyecto, Director Ejecutivo y Director Creativo sobre 13 proyectos activos). La intervención se delimita al subproceso transversal; el TNVA captura el desperdicio total del macroproceso conforme metodología Lean. Herramienta habilitadora: Central Contexto.

FÓRMULA (catálogo): TNVA = Σ (Frecuencia semanal × Tiempo unitario en min) por NVA del macroproceso. Conversión a min/mes con factor 4,33 sem/mes.

CÁLCULO LÍNEA BASE (marzo 2026):
NVAs subproceso transversal (cronométricas): NVA1 transcripción 75 + NVA2 transferencia tabla→gruesa 40 + NVA3 alimentación dashboards 30 + NVA4 búsqueda info 100 + NVA5 consolidación reporte 45 + NVA6 actualización cronogramas 30 + NVA7 reconciliación costos 30 = 350 min/sem.
NVAs en macroetapas (estimadas): NVA8 reprocesos por inconsistencia 150 + NVA9 tiempos muertos repriorización 120 + NVA10 esperas disciplinas externas 150 + NVA11 re-trabajos por feedback tardío 100 + NVA12 reprocesos facturación 30 = 550 min/sem.
TOTAL LB = 900 min/sem × 4,33 = 3.897 min/mes.

META = 2.728 min/mes (-30%). Reducción 271 min/sem (1.169 min/mes) mediante registro único en Central Contexto, fuente única de verdad y trazabilidad de hitos.

SOPORTES: Soporte_1_VSM_Macroproceso (con Lead Time, puntos críticos, tipo Lean) y Soporte_4_Calculo_Indicadores.
```

### Archivos a adjuntar

- `Soporte_1_VSM_Macroproceso_CNTXT_PT2.xlsx`
- `Soporte_4_Calculo_Indicadores_CNTXT_PT2.xlsx`

---

## 2️⃣ IPT-49182 — TCP

**URL**: https://innpulsacolombia.my.site.com/fabricasdeproductividad/s/fp-indicadorplantrabajo-obj/a0LRQ00000N1bTM2AZ/ipt49182

### Campos numéricos

Sin cambios numéricos. Mantener LB 48,00000 / Meta 16,00000 / Variación -66,67.

### Cálculo de la medición (1.386 caracteres)

```
ALCANCE: TCP del ciclo de respuesta a eventos operativos (subproceso transversal de Gestión Interna del Portafolio). NO corresponde al ciclo del proyecto inmobiliario completo (6-18 meses) ni al macroproceso medido por TNVA. La ficha técnica permite expresamente subprocesos distintos al del TNVA, adjuntando diagrama aparte.

EQUIVALENCIA: orden de producción = ocurrencia de evento operativo (desfase cronograma, desviación presupuestal, pausa cliente, demora disciplina externa); producto final = decisión correctiva del equipo directivo.

CICLO DE REFERENCIA TIPO (no promedio) observado en marzo 2026 sobre un evento operativo característico.

FÓRMULA: TCP = Σ horas hábiles por hito del ciclo (jornada 8,4 h, Ley 2101/2021).

CÁLCULO LÍNEA BASE:
H1 ocurrencia evento (—) 0 h.
H2 detección/registro (NVA latencia) 12 h.
H3 consolidación tabla gruesa (NVA) 12 h.
H4 preparación reporte directivo (NVA) 16 h.
H5 revisión Líder (VA) 4 h.
H6 escalamiento y decisión (VA) 4 h.
TCP LB = 0+12+12+16+4+4 = 48 h hábiles. Coherencia ficha: 8 h VA (H5+H6) + 40 h NVA (H2+H3+H4) = 48 h. Equivalencia minutos: 2.880 min.

META = 16 h hábiles (-66,67%): H2 1,5 h (alerta automática, pasa a VA), H3 y H4 eliminadas (dashboard tiempo real), H5 3 h, H6 11,5 h. Coherencia: 16 h VA + 0 h NVA = 16 h. Equivalencia: 960 min.

SOPORTES: Soporte_2_VSM_TCP_CicloRespuesta y Soporte_4_Calculo_Indicadores.
```

### Archivos a adjuntar

- `Soporte_2_VSM_TCP_CicloRespuesta_CNTXT_PT2.xlsx`
- `Soporte_4_Calculo_Indicadores_CNTXT_PT2.xlsx`

---

## 3️⃣ IPT-49180 — AD(TCP)

**URL**: https://innpulsacolombia.my.site.com/fabricasdeproductividad/s/fp-indicadorplantrabajo-obj/a0LRQ00000N1bTK2AZ/ipt49180

### Campos numéricos

| Campo | Antes | Nuevo |
|---|---|---|
| Línea base | 541.000,00000 | **1799246,00000** |
| Meta del indicador | 352.000,00000 | **1379594,00000** |
| Variación porcentual esperada | -34,94 | **-23,33** |

### Cálculo de la medición (1.245 caracteres)

```
ALCANCE: AD(TCP) sobre el subproceso transversal de Gestión Interna del Portafolio (12 actividades de los 3 perfiles directivos sobre 13 proyectos activos). Aplica solo a este subproceso porque requiere TCP cronométrico y costo unitario precisos.

FÓRMULA (catálogo): AD[TCP] = TCP × Valor por minuto. Variable: TCP total del subproceso de gestión.

CÁLCULO LÍNEA BASE (marzo 2026):
TCP total mensual = (555 + 165 + 120) min/sem × 4,33 = 3.637,20 min/mes.

CT del subproceso (base 182 h/mes, Ley 2101/2021: 42 h sem × 4,33 sem):
Líder Mike $4.500.000 ÷ 182 = $24.725/h × 40,05 h = $990.236.
Director Ejecutivo Simón $8.000.000 ÷ 182 = $43.956/h × 11,91 h = $523.516.
Director Creativo JP $6.000.000 ÷ 182 = $32.967/h × 8,66 h = $285.494.
CT total = $1.799.246/mes.

Valor por minuto = $1.799.246 ÷ 3.637,20 = $494,69/min.
AD inicial = TCP × Valor/min = 3.637,20 × $494,69 = $1.799.246/mes.

META = $1.379.594/mes (-23,33%). Eliminación 70% del NVA del subproceso (350 min/sem → 105 min/sem residual) con factor de adopción 79%, lleva TCP final a 2.788 min/mes. AD final = 2.788 × $494,69 = $1.379.594. Ahorro mensual = $419.652.

SOPORTES: Soporte_1_VSM_Macroproceso, Soporte_4_Calculo_Indicadores y Soporte_5_Reporte_Mediciones (hoja IPT-3 AD).
```

### Archivos a adjuntar

- `Soporte_1_VSM_Macroproceso_CNTXT_PT2.xlsx`
- `Soporte_4_Calculo_Indicadores_CNTXT_PT2.xlsx`
- `Soporte_5_Reporte_Mediciones_CNTXT_PT2.xlsx`

---

## 4️⃣ IPT-49183 — CU

**URL**: https://innpulsacolombia.my.site.com/fabricasdeproductividad/s/fp-indicadorplantrabajo-obj/a0LRQ00000N1bTN2AZ/ipt49183

### Campos numéricos

Sin cambios numéricos. Mantener LB 138.404,00000 / Meta 90.000,00000 / Variación -34,97.

### Cálculo de la medición (1.087 caracteres)

```
ALCANCE: CU sobre el subproceso transversal de Gestión Interna del Portafolio: costo total de gestión dividido entre número de proyectos activos en el período.

FÓRMULA (catálogo): CU = CT / Número de productos. Variables: CT (costo total) y N (número de servicios prestados).

CÁLCULO LÍNEA BASE (marzo 2026):
CT total subproceso = $1.799.246/mes (idéntico al CT del IPT-3 AD; suma costo VA+NVA de los 3 perfiles directivos con base 182 h/mes Ley 2101/2021).
N = 13 proyectos activos en gestión.
CU LB = $1.799.246 ÷ 13 = $138.404/proyecto·mes.

META = $90.000/proyecto·mes (-34,97%). Se logra al reducir el CT a $1.170.000/mes mediante eliminación del NVA del subproceso (impacto compuesto IPT-1 TNVA y IPT-3 AD) con N = 13 proyectos en el período. Ahorro mensual en CT = $1.799.246 − $1.170.000 = $629.246/mes.

COHERENCIA CON IPT-3 AD: el ahorro en CT supera al AD del IPT-3 ($419.652) porque el CU contempla la liberación adicional de tiempo VA reasignable, no solo el costo del NVA eliminado.

SOPORTES: Soporte_4_Calculo_Indicadores y Soporte_5_Reporte_Mediciones (hoja IPT-4 CU).
```

### Archivos a adjuntar

- `Soporte_4_Calculo_Indicadores_CNTXT_PT2.xlsx`
- `Soporte_5_Reporte_Mediciones_CNTXT_PT2.xlsx`

---

## 5️⃣ IPT-49184 — OPC

**URL**: https://innpulsacolombia.my.site.com/fabricasdeproductividad/s/fp-indicadorplantrabajo-obj/a0LRQ00000N1bTO2AZ/ipt49184

### Campos numéricos

| Campo | Antes | Nuevo |
|---|---|---|
| Línea base | 58,33000 | **100,00000** |
| Meta del indicador | 25,00000 | **28,57000** |
| Variación porcentual esperada | -57,14 | **-71,43** |

### Cálculo de la medición (1.541 caracteres)

```
ALCANCE: OPC sobre los puntos de contacto directo con el cliente externo en el subproceso productivo (concentrados en macroetapa M5 Aprobaciones y parte de M4 Producción). El indicador mide los 7 tipos de punto, no el número de ocurrencias (los 7 tipos se ejecutan en cada uno de los 3 hitos del proyecto: ~21 ocurrencias por proyecto).

FÓRMULA (catálogo): OPC = (Puntos por optimizar / Total puntos contacto cliente) × 100. Numerador: puntos sin estandarizar. Denominador: total puntos de contacto directo con cliente externo.

CÁLCULO LÍNEA BASE (marzo 2026):
Total puntos contacto cliente externo (denominador) = 7:
P1 Convocatoria reunión avance, P2 Preparación presentación, P3 Reunión presencial, P4 Envío planos/renders, P5 Recepción comentarios cliente, P6 Ciclo ajustes feedback, P7 Confirmación aprobación.
Puntos por optimizar al inicio (numerador) = 7 (ninguno opera bajo protocolo estandarizado: tiempos variables, herramientas disjuntas, trazabilidad fragmentada).
OPC LB = (7/7) × 100 = 100,00%.

META = 28,57% (-71,43%). 5 puntos a estandarizar mediante Central Contexto (P1 calendar_sync+notifications, P2 dashboards, P4 documents, P5 rfis, P6 projects+documents). 2 sin estandarizar al cierre (P3 reunión presencial por requerimiento cliente, P7 comunicación final canal del cliente). OPC final = (2/7) × 100 = 28,57%.

SUSTENTO EMPÍRICO: caso Saint Regis, período revisión cliente 88 h reales vs 47 proyectadas (+87%) en cada hito.

SOPORTES: Soporte_4_Calculo_Indicadores y Soporte_5_Reporte_Mediciones (hoja IPT-5 OPC).
```

### Archivos a adjuntar

- `Soporte_4_Calculo_Indicadores_CNTXT_PT2.xlsx`
- `Soporte_5_Reporte_Mediciones_CNTXT_PT2.xlsx`

---

## 6️⃣ IPT-49181 — IA papel

**URL**: https://innpulsacolombia.my.site.com/fabricasdeproductividad/s/fp-indicadorplantrabajo-obj/a0LRQ00000N1bTL2AZ/ipt49181

### Campos numéricos

| Campo | Antes | Nuevo |
|---|---|---|
| Línea base | 170,00000 | **13,08000** |
| Meta del indicador | 145,00000 | **11,15000** |
| Variación porcentual esperada | -14,71 | **-14,74** |

### Cálculo de la medición (1.519 caracteres)

```
ALCANCE: Consumo de papel del subproceso de Gestión Interna y de las macroetapas con contacto cliente. El papel se reporta como instancia del 'Consumo de Recurso' genérico contemplado en la ficha (variables canónicas: agua, energía, gas, recurso, combustible). La unidad 'hojas/proyecto·mes' es coherente con la fórmula del catálogo, aunque no aparezca literalmente en el listado de unidades sugeridas (m³, kWh, Km/gal, Gal/mes); el papel tiene métrica natural en hojas. Para sostenibilidad ambiental, la metodología del programa permite formatos como inventario del recurso o disminución en compras cuando no aplican facturas de servicios públicos.

FÓRMULA (catálogo): IA[Recurso] = Consumo / NPoS.

CÁLCULO LÍNEA BASE (marzo 2026):
Consumo mensual de papel:
Doc 1 Reportes ejecutivos directivos: 40 hojas/mes.
Doc 2 Presentaciones avance clientes: 60 hojas/mes.
Doc 3 Planos y renders impresos para aprobación: 30 hojas/mes.
Doc 4 Documentación soporte (actas, fichas entregables): 25 hojas/mes.
Doc 5 Copias de respaldo: 15 hojas/mes.
Consumo total = 170 hojas/mes.
NPoS = 13 proyectos activos.
IA LB = 170 ÷ 13 = 13,08 hojas/proyecto·mes.

META = 11,15 hojas/proyecto·mes (-14,74%). Consumo reducido a 145 hojas/mes mediante reemplazo de reportes ejecutivos por dashboards (Doc 1: 40→15) y reducción de presentaciones para clientes (Doc 2: 60→55). Otros mantenidos por requerimiento cliente o política. IA meta = 145 ÷ 13 = 11,15.

SOPORTES: Soporte_3_Inventario_Papel_CNTXT_PT2_IA y Soporte_4_Calculo_Indicadores.
```

### Archivos a adjuntar

- `Soporte_3_Inventario_Papel_CNTXT_PT2_IA.xlsx`
- `Soporte_4_Calculo_Indicadores_CNTXT_PT2.xlsx`

---

## ✅ Verificación final

URL del PT principal: https://innpulsacolombia.my.site.com/fabricasdeproductividad/s/fp-plantrabajo-obj/a0URQ00000LxlgM2AR/plan-de-trabajo-contexto-arquitectura

| # | Código | Indicador | LB | Meta | Variación |
|---|---|---|---|---|---|
| 1 | IPT-49179 | TNVA | 3.897,00000 | 2.728,00000 | -30,00 |
| 2 | IPT-49182 | TCP | 48,00000 | 16,00000 | -66,67 |
| 3 | IPT-49180 | AD(TCP) | 1.799.246,00000 | 1.379.594,00000 | -23,33 |
| 4 | IPT-49183 | CU | 138.404,00000 | 90.000,00000 | -34,97 |
| 5 | IPT-49184 | OPC | 100,00000 | 28,57000 | -71,43 |
| 6 | IPT-49181 | IA papel | 13,08000 | 11,15000 | -14,74 |

## 📤 Reenviar el PT2

En el detalle del PT principal click en **"Enviar para Aprobación"**. Flujo: Gestor (Yoing) → Líder de Línea (Melisa).

## 💬 Notificar a Melisa

> "Melisa, buenos días. Reenviamos el PT2 de CNTXT con los ajustes acordados en la reunión: (1) reflejamos el alcance completo del proceso productivo (7 macroetapas) en los 6 indicadores; (2) aclaramos que las mediciones del subproceso intervenido (Gestión Interna del Portafolio) se delimitan según corresponda a cada indicador; (3) corregimos las observaciones técnicas del 23/04 sobre AD(TCP), CU y OPC, alineando las fórmulas con las fichas del catálogo. Quedo atento a tu revisión."

---

## Troubleshooting

- **Campo no se deja editar**: el registro debe estar desbloqueado (Melisa lo desbloqueó el 4/05).
- **El campo "Cálculo de la medición" rechaza el texto por longitud**: cada bloque está dentro del límite de 1.700 chars; si rechaza, copia un bloque a la vez (Alcance / Fórmula / Cálculo / Meta / Soportes).
- **No puedes adjuntar archivo**: nuestros archivos son <25 KB cada uno, dentro del límite del portal.
- **Cualquier error inesperado**: tómame screenshot y lo reviso.
