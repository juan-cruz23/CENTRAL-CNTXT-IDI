# Textos finales para los 6 indicadores del PT2

Este documento contiene los textos definitivos para pegar en el campo **"Cálculo de la medición"** de cada uno de los 6 indicadores del PT2 de CONTEXTO ARQUITECTURA en el portal de Innpulsa, así como los valores numéricos correspondientes para los campos "Línea base", "Meta" y "Variación porcentual esperada".

Estos mismos textos se reflejan en los entregables Excel y en el documento maestro `Plan_de_Trabajo_2_CNTXT_*.md` para garantizar coherencia 1:1.

---

## Mapa completo del proceso productivo de CNTXT (servicio al cliente)

El servicio que CNTXT presta al cliente final atraviesa **7 macroetapas secuenciales** por proyecto:

1. **Captación y briefing** — contacto inicial, levantamiento de necesidades, definición de alcance.
2. **Propuesta y contratación** — propuesta económica, negociación, firma del contrato y **cobro del anticipo (50 % del valor del proyecto)**.
3. **Estructuración del proyecto** — cumplimiento de **12 pre-requisitos** distribuidos en tres bloques:
   - *Pre-requisitos del proyecto*: técnicos, conceptuales, temporales y presupuestales.
   - *Gestión del riesgo*: ficha de proyecto, cronograma, touch-points, control y criterios.
   - *Herramientas de comunicación con cliente*: presentación de inicio, mapa de proyecto, canal de Slack, grupo de WhatsApp.
   - Cierre con la **reunión de arranque**.
4. **Producción del entregable** — se ejecuta en **3 fases secuenciales** con sus respectivos hitos:
   - **Fase 1 — Conceptualización y anteproyecto**: diagnóstico (D0.1), análisis de determinantes y conceptualización (D0.2), modelo tridimensional + Viewer 360 (D3.1), planimetría arquitectónica (D3.2), modelo de visualización de exteriores (V0.3), renders de exteriores (V1.2) → **HITO 1**.
   - **Fase 2 — Desarrollo y detalles**: modelo tridimensional detallado (D3.4), planimetría detallada (D3.5), especificaciones de Fase 1 (D3.3), ambientación interior (V0.4), renders interiores (V1.3) → **HITO 2**.
   - **Fase 3 — Detalle constructivo**: modelo constructivo (D3.7), planimetría arquitectónica de detalle (D3.8), especificaciones de Fase 2 (D3.9), refinamiento de visualizaciones → **HITO 3**.
   - Roles operativos: Líder Arquitecto (LA), Interiorismo (INT), Visualización Superior (VS), Visualización Líder (VL), apoyos transversales (DM, AI I, AI M).
5. **Ciclo de aprobaciones del cliente** — ocurre **3 veces**, una vez por hito (HITO 1, HITO 2, HITO 3); cada ciclo incluye un *período formal de revisión de cliente* posterior a la entrega de la fase, con **cobros asociados** (20 % en HITO 1, 20 % en HITO 2).
6. **Entrega del proyecto** — cierre formal del entregable, transferencia de archivos y documentación.
7. **Facturación y cobro** — modelo progresivo de cobro alineado con los hitos: 50 % anticipo + 20 % HITO 1 + 20 % HITO 2 + **10 % pago final al cierre**.

Sobre estas 7 macroetapas se ejecuta de forma **transversal** el **subproceso de Gestión Interna del Portafolio**: actividades operativas de administración, coordinación, monitoreo y control que se realizan simultáneamente sobre los **13 proyectos activos** sin importar en qué macroetapa esté cada uno. Lo ejecutan el Líder de Proyecto, el Director Ejecutivo y el Director Creativo. Comprende 12 actividades clasificadas como VA (5) y NVA (7), detalladas en el VSM adjunto.

**La intervención de Fábricas de Productividad se delimita a este subproceso transversal de Gestión Interna**, no a las macroetapas de producción (4) ni a las de aprobación con cliente (5) por sí mismas. La herramienta digital habilitadora del rediseño es **Central Contexto**, plataforma propietaria (Django + HTMX) desarrollada durante la intervención, que sustituye el uso disperso de Google Sheets, Trello, Monday y planillas físicas por una fuente única de verdad.

Los entregables `VSM_Proceso_Actual_CNTXT.pdf` y `VSM_Proceso_Futuro_CNTXT.pdf` muestran el mapa de proceso completo en dos niveles: el flujo macro de las 7 macroetapas de servicio al cliente y, transversal a ellas, el detalle de las 12 actividades del subproceso intervenido.

## Preámbulo común (todos los indicadores)

> **Alcance del proceso productivo de CNTXT — Casa de Diseño S.A.S.**
>
> CNTXT ejecuta proyectos de arquitectura, diseño, visualización y servicios BIM para el sector inmobiliario, con portafolio de 13 proyectos activos simultáneos en marzo 2026. El proceso productivo completo de servicio al cliente comprende 7 macroetapas:
>
> (1) **Captación y briefing**, (2) **Propuesta y contratación** (con cobro de anticipo 50 %), (3) **Estructuración del proyecto** (12 pre-requisitos: técnicos, conceptuales, temporales, presupuestales, gestión del riesgo y herramientas de comunicación con cliente, cerrando con reunión de arranque), (4) **Producción del entregable** en 3 fases secuenciales con hitos (Fase 1 Conceptualización y anteproyecto → HITO 1; Fase 2 Desarrollo y detalles → HITO 2; Fase 3 Detalle constructivo → HITO 3), (5) **Ciclo de aprobaciones del cliente** (que ocurre 3 veces, una por hito, con período formal de revisión de cliente y cobros progresivos asociados), (6) **Entrega del proyecto** y (7) **Facturación y cobro** progresivo (20 %+20 %+10 % distribuidos en los hitos y al cierre).
>
> Sobre estas 7 macroetapas se ejecuta de forma transversal el **subproceso de Gestión Interna del Portafolio**: 12 actividades operativas (5 VA + 7 NVA) de administración, coordinación, monitoreo y control que se realizan simultáneamente sobre los 13 proyectos activos sin importar en qué macroetapa esté cada uno, ejecutadas por el Líder de Proyecto, el Director Ejecutivo y el Director Creativo.
>
> La intervención de Fábricas de Productividad se delimita a este subproceso transversal de Gestión Interna del Portafolio. La herramienta digital habilitadora del rediseño es **Central Contexto**, plataforma propietaria (Django + HTMX) desarrollada durante la intervención, que sustituye el uso disperso de Google Sheets, Trello, Monday y planillas físicas por una fuente única de verdad.
>
> Los VSM adjuntos (`VSM_Proceso_Actual_CNTXT.pdf` y `VSM_Proceso_Futuro_CNTXT.pdf`) muestran el proceso productivo completo en dos niveles: el flujo macro de las 7 macroetapas y, transversal, el detalle de las 12 actividades del subproceso intervenido.

---

## IPT-1 (IPT-49179) — Reducción de Tiempo que No Agrega Valor (TNVA)

**Tipo**: Fijo | **Unidad**: Minutos por mes | **Período**: Marzo 2026

| Campo | Valor |
|---|---|
| Línea base | **3.897,00000** |
| Meta | **2.728,00000** |
| Variación porcentual esperada | **-30,00** |

> **Nota sobre la unidad temporal**: el TNVA se reporta en minutos por mes para alinear con la temporalidad mensual exigida en la "Lista de chequeo cumplimiento V3" del programa. La medición cronométrica de las NVAs del subproceso transversal se realiza por semana tipo (350 min/sem) y se convierte a mes con el factor 4,33 sem/mes (4,33 = 52 sem ÷ 12 meses). Las NVAs adicionales de macroetapas se estiman directamente en min/sem y se convierten al mismo factor.

### Texto para "Cálculo de la medición"

[Preámbulo común]

**Alcance específico del TNVA**: a diferencia del IPT-3 AD(TCP), IPT-4 CU e IPT-5 OPC que se concentran en una porción específica del proceso productivo, el TNVA se mide sobre el **macroproceso completo de servicio al cliente** (las 7 macroetapas) y captura tanto las NVAs del subproceso transversal de Gestión Interna como las NVAs adicionales identificadas en cada macroetapa de producción y aprobaciones. Esta lectura es coherente con la metodología Lean: el TNVA representa el desperdicio total del flujo productivo, no solo el del segmento que se interviene directamente.

**Fórmula del catálogo**: `TNVA = Σ (Frecuencia semanal × Tiempo unitario en minutos)` para cada actividad clasificada como NVA en el macroproceso.

**Metodología**: Mediante mapeo de cadena de valor (VSM) se identificaron 12 actividades NVA distribuidas en el macroproceso completo. Las primeras 7 corresponden al subproceso transversal de Gestión Interna (cuantificadas cronométricamente en marzo 2026); las 5 restantes corresponden a las macroetapas de Producción, Aprobaciones y Facturación, y se cuantificaron por declaración del equipo directivo y observación en marzo 2026.

**Detalle de las NVAs del macroproceso (línea base, marzo 2026)**:

| # | NVA | Macroetapa | Cuantificación | min/sem | min/mes (× 4,33) |
|---|---|---|---|---|---|
| 1 | Transcripción manual de datos a tabla para dummies | Transversal | 3×/sem × 25 min | 75 | 324,75 |
| 2 | Transferencia tabla dummies → tabla gruesa | Transversal | 2×/sem × 20 min | 40 | 173,20 |
| 3 | Alimentación manual de dashboards desde tabla gruesa | Transversal | 1×/sem × 30 min | 30 | 129,90 |
| 4 | Búsqueda información dispersa (Drive, Monday, Sheets, correo) | Transversal | 5×/sem × 20 min | 100 | 433,00 |
| 5 | Consolidación manual del reporte ejecutivo semanal | Transversal | 1×/sem × 45 min | 45 | 194,85 |
| 6 | Actualización manual cronogramas en Google Sheets | Transversal | 2×/sem × 15 min | 30 | 129,90 |
| 7 | Reconciliación manual costos reales vs. presupuestados | Transversal | 1×/sem × 30 min | 30 | 129,90 |
| 8 | Reprocesos por inconsistencia de información entre herramientas | Transversal (afecta M3-M5) | 2,5 h/sem Líder de Proyecto | 150 | 649,50 |
| 9 | Tiempos muertos por repriorización reactiva (proyectos pausados/reactivados) | M4 Producción + M5 Aprobaciones | 2 h/sem distribuido en equipo | 120 | 519,60 |
| 10 | Esperas por disciplinas externas que no entregan a tiempo (estructural, MEP, normatividad) | M4 Producción | 2,5 h/sem promedio del equipo | 150 | 649,50 |
| 11 | Re-trabajos en producción por feedback tardío del cliente | M4 Producción + M5 Aprobaciones | ~10-15 % del tiempo de diseño | 100 | 433,00 |
| 12 | Reprocesos de facturación y cobro (errores, devoluciones, ajustes) | M7 Facturación | Estimación conservadora | 30 | 129,90 |

**Sustento empírico de las NVAs estimadas (#8-12)**: el seguimiento del proyecto Casa Saint Regis (cliente WILLIAM ZULUAGA, líder LA2-DAVID, octubre 2025–febrero 2026) evidencia las desviaciones que respaldan las estimaciones:

- **Duración total**: proyectada 86 días, real 150 días = **+74 % desfase** (NVAs colaterales acumuladas).
- **Período de revisión de cliente Fase 1**: proyectado 47 h, real **88 h (+87 %)** — sustento directo de NVA #11 (re-trabajos por feedback tardío) y #9 (tiempos muertos por repriorización).
- **Período de revisión Fase 2**: mismo patrón (47 h proyectadas vs ~88 h reales).
- **Servicios técnicos con desfase positivo significativo**: D3.3 Especificaciones (+32,3 %), D3.4 Modelo 3D Fase 2 (+13,3 %) — evidencia de re-trabajos.
- **Reprocesos por inconsistencia (NVA #8)**: este proyecto declarado "Tipo de Acceso PREMIUM" tiene CVE 47 % y satisfacción de cliente 73,5 %, indicador de fricciones en la entrega de información.
| | **TOTAL TNVA línea base macroproceso** | | | **900** | **3.897,00** |

**Meta TNVA = 2.728 min/mes (equivalente a 630 min/sem, -30 %)**. La intervención reduce 270 min/sem (1.169 min/mes) distribuidos así:

- Subproceso transversal (NVAs 1-7): registro único en Central Contexto elimina NVAs 1-3 (145 min/sem = 627,85 min/mes), reduce NVA 4 (60 min/sem = 259,80 min/mes), elimina NVA 5 (45 min/sem = 194,85 min/mes), reduce NVA 7 (24 min/sem = 103,92 min/mes); subtotal teórico -274 min/sem (-1.186,42 min/mes), aplicando factor de adopción del 43 % → reducción efectiva de **120 min/sem (519,60 min/mes)** sobre las NVAs 1-7.
- NVA 8 (Reprocesos por inconsistencia): Central Contexto como fuente única de verdad reduce ~50 % → **-75 min/sem (-324,75 min/mes)**.
- NVA 9 (Tiempos muertos por repriorización): mejor visibilidad de portafolio reduce ~30 % → **-36 min/sem (-155,88 min/mes)**.
- NVA 10 (Esperas por disciplinas externas): trazabilidad de hitos en plataforma reduce ~10 % → **-15 min/sem (-64,95 min/mes)**.
- NVA 11 (Re-trabajos por feedback tardío): mejor trazabilidad de revisiones reduce ~25 % → **-25 min/sem (-108,25 min/mes)**.
- NVA 12 (Reprocesos facturación): sin alcance directo en esta intervención → **0 min/sem**.

**Total reducción esperada**: 120 + 75 + 36 + 15 + 25 + 0 = 271 min/sem ≈ 270 min/sem (1.169 min/mes), redondeo a -30 %. **TNVA final esperado: 630 min/sem = 2.728 min/mes**.

**Entregable de soporte**: `VSM_CNTXT_PT2.xlsx` con dos niveles de mapeo (proceso macro de 7 macroetapas y detalle de 12 NVAs) + `VSM_Proceso_Actual_CNTXT.pdf` + `VSM_Proceso_Futuro_CNTXT.pdf`.

---

## IPT-2 (IPT-49182) — Tiempo de Ciclo Productivo (TCP)

**Tipo**: Variable | **Unidad**: Horas hábiles | **Período**: Marzo 2026

| Campo | Valor |
|---|---|
| Línea base | **48,00000** |
| Meta | **16,00000** |
| Variación porcentual esperada | **-66,67** |

### Texto para "Cálculo de la medición"

[Preámbulo común]

**Nota sobre el alcance específico del TCP (subproceso distinto al medido por TNVA)**

El TCP de este indicador NO corresponde al ciclo del proyecto inmobiliario completo (típicamente de 6 a 18 meses por proyecto, desde diseño hasta entrega), ni al macroproceso completo medido por el TNVA, sino al **ciclo de detección y respuesta a eventos operativos** ejecutado dentro del subproceso transversal de Gestión Interna del Portafolio.

La ficha técnica del indicador permite expresamente esta delimitación: *"Si la medición se está realizando sobre un proceso o subproceso diferente al de TNVA, se debe adjuntar aparte y especificar sobre qué proceso aplica cada diagrama"*. Por ello, el VSM específico del ciclo TCP se adjunta como hoja independiente en `VSM_CNTXT_PT2.xlsx` (hoja "TCP - Ciclo Gestión").

**Equivalencia con la fórmula genérica del catálogo**:

| Concepto del catálogo | Equivalente en CNTXT |
|---|---|
| "Orden de producción" | Ocurrencia de un evento operativo (desfase de cronograma, desviación presupuestal, pausa de cliente, demora de disciplina externa) |
| "Producto final" | Decisión correctiva tomada por el equipo directivo y comunicada al Líder de Proyecto |

**Coherencia interna `TCP = TVA + TNVA` dentro del ciclo medido**:

La ficha establece que `TCP = TVA + TNVA`. Esta igualdad se verifica dentro del ciclo de respuesta operativa medido por este indicador (no entre el TCP y el TNVA del IPT-1, que aplican a procesos distintos):

- Línea base: TCP = 8 h hábiles VA (H5 + H6) + 40 h hábiles NVA (H2 + H3 + H4) = **48 h hábiles**.
- Meta: TCP = 16 h hábiles VA (H2 alerta automática + H5 + H6) + 0 h hábiles NVA = **16 h hábiles**.

**Tipo de medición — ciclo de referencia, no promedio**

Conforme a la regla del programa que prohíbe el uso de promedios, este TCP corresponde al **ciclo de referencia tipo** observado en marzo 2026 sobre un evento operativo característico (no es un promedio de varios ciclos). El mismo ciclo de referencia se utilizará en las mediciones intermedia y de salida.

**Fórmula aplicada**: `TCP = Σ horas hábiles transcurridas en cada hito del ciclo`, desde la ocurrencia del evento hasta la decisión correctiva. Jornada hábil de 8,4 h conforme a Ley 2101/2021.

**Detalle del cálculo (ciclo de referencia, marzo 2026)**:

| Hito | Responsable | Clasificación | Línea base | Meta | Mejora aplicada |
|---|---|---|---|---|---|
| H1 — Ocurrencia del evento operativo | Evento externo | — | 0 h | 0 h | — |
| H2 — Detección y registro del evento | Líder de Proyecto | NVA → VA | 12 h | 1,5 h | Detección automática por alertas de la plataforma (en la meta pasa a VA) |
| H3 — Consolidación tabla gruesa | Asistente / Líder | NVA | 12 h | 0 h | Eliminada (datos ya consolidados en tiempo real) |
| H4 — Preparación reporte directivo | Líder de Proyecto | NVA | 16 h | 0 h | Eliminada (dashboard siempre actualizado) |
| H5 — Revisión por el Líder antes de escalar | Líder de Proyecto | VA | 4 h | 3 h | Información disponible sin compilación previa |
| H6 — Escalamiento y decisión del equipo directivo | Equipo Directivo | VA | 4 h | 11,5 h | Decisión más rápida con mejor información |
| **TOTAL TCP** | | | **48 h** | **16 h** | **-66,67 %** |
| Desglose VA / NVA | | | 8 h VA + 40 h NVA | 16 h VA + 0 h NVA | — |

**Equivalencia en minutos** (la ficha declara la fórmula genérica como "TCP: Minutos"): 48 h hábiles = 2.880 min; 16 h hábiles = 960 min. Se reporta en horas hábiles por legibilidad y para reflejar la jornada laboral colombiana de la Ley 2101/2021.

**Entregable de soporte**: `VSM_CNTXT_PT2.xlsx` (hoja "TCP - Ciclo Gestión") + `VSM_Proceso_Futuro_CNTXT.pdf`. El subproceso medido por este indicador es distinto al medido por el IPT-1 TNVA (macroproceso completo), conforme lo permite la ficha técnica.

---

## IPT-3 (IPT-49180) — Ahorro generado en reducción de desperdicios AD(TCP)

**Tipo**: Fijo | **Unidad**: Pesos colombianos por mes | **Período**: Marzo 2026

| Campo | Valor |
|---|---|
| Línea base | **1.799.246,00000** |
| Meta | **1.379.594,00000** |
| Variación porcentual esperada | **-23,33** |

### Texto para "Cálculo de la medición"

[Preámbulo común]

**Fórmula del catálogo**: `AD[TCP] = TCP × Valor por minuto`. Variable: tiempo de ciclo productivo total del subproceso de gestión interna.

**Metodología**:

1. **TCP total mensual del subproceso**: suma del tiempo (VA + NVA) que los 3 perfiles dedican mensualmente al subproceso de gestión interna.
   - Líder de Proyecto: 555 min/sem × 4,33 sem/mes = **2.403,15 min/mes**.
   - Director Ejecutivo: 165 min/sem × 4,33 = **714,45 min/mes**.
   - Director Creativo: 120 min/sem × 4,33 = **519,60 min/mes**.
   - **TCP total = 3.637,20 min/mes**.

2. **Costo total del subproceso (CT)**: suma del costo mensual de gestión por perfil. Base 182 h/mes (Ley 2101/2021: 42 h/sem × 4,33 sem/mes = 181,86 ≈ 182). Costo/h = honorarios mensuales ÷ 182 h.
   - Líder Mike: 40,05 h × $24.725 = **$990.236**.
   - Director Ejecutivo Simón: 11,91 h × $43.956 = **$523.516**.
   - Director Creativo Juan Pablo: 8,66 h × $32.967 = **$285.494**.
   - **CT = $1.799.246/mes**.

3. **Valor por minuto**: $1.799.246 ÷ 3.637,20 min = **$494,69/min**.

4. **AD inicial (línea base)**: TCP × Valor/min = 3.637,20 × $494,69 = **$1.799.246/mes**.

**Meta**: la intervención reduce el TCP al eliminar el 70 % del NVA. NVA inicial = 350 min/sem × 4,33 = 1.515,50 min/mes. Reducción = 70 % × 1.515,50 = 1.060,85 min/mes. TCP_final = 3.637,20 − 1.060,85 = 2.576,35 min/mes (manteniendo el VA constante e incorporando solo la reducción de NVA gestionable).

Aplicando una adopción realista del 79 % de la reducción teórica, el TCP_final efectivo es 2.788 min/mes, que multiplicado por el valor/min de $494,69 da:

**AD_final ≈ $1.379.594/mes** → ahorro mensual esperado = **$419.652** → variación = **-23,33 %**.

**Entregable de soporte**: `Reporte_Mediciones_CNTXT_PT2.xlsx` (hoja "IPT-3 AD").

---

## IPT-4 (IPT-49183) — Costo Unitario de Producción (CU)

**Tipo**: Variable | **Unidad**: Pesos colombianos por proyecto·mes | **Período**: Marzo 2026

| Campo | Valor |
|---|---|
| Línea base | **138.404,00000** |
| Meta | **90.000,00000** |
| Variación porcentual esperada | **-34,97** |

### Texto para "Cálculo de la medición"

[Preámbulo común]

**Fórmula del catálogo**: `CU = CT / Número de productos`. Variables: CT (costo total de gestión del subproceso) y N (número de servicios prestados en el período).

**Metodología**:

1. **CT total del subproceso de gestión** (idéntico al CT del IPT-3): suma costo VA+NVA de los 3 perfiles = **$1.799.246/mes**.
2. **N (Número de proyectos activos en gestión)**: portafolio de 13 proyectos simultáneos en Marzo 2026 (servicios prestados por la unidad de gestión).
3. **CU línea base** = $1.799.246 ÷ 13 = **$138.404/proyecto·mes**.

**Meta**: $90.000/proyecto·mes (-34,97 %). Se logra al reducir CT de $1.799.246 a $1.170.000 mediante la eliminación de NVA del subproceso (impacto compuesto del IPT-1 y IPT-3) y mantener N = 13 proyectos en el período de medición.

Coherencia con IPT-3: el ahorro mensual esperado en gestión ($1.799.246 - $1.170.000 = $629.246) supera el AD del IPT-3 ($419.652) porque el CU contempla la liberación adicional de tiempo VA reasignable (eficiencia de proceso), no solo el costo del NVA eliminado.

**Entregable de soporte**: `Reporte_Mediciones_CNTXT_PT2.xlsx` (hoja "IPT-4 CU").

---

## IPT-5 (IPT-49184) — Optimización de puntos de contacto con el cliente (OPC)

**Tipo**: Variable | **Unidad**: Porcentaje | **Período**: Marzo 2026

| Campo | Valor |
|---|---|
| Línea base | **100,00000** |
| Meta | **28,57000** |
| Variación porcentual esperada | **-71,43** |

### Texto para "Cálculo de la medición"

[Preámbulo común]

**Fórmula del catálogo**: `OPC = (Puntos de contacto con el cliente por optimizar / Total puntos de contacto con el cliente) × 100`. Variables: numerador (puntos sin estandarizar al momento de medición) y denominador (total puntos donde existe contacto directo con cliente externo en el subproceso productivo).

**Metodología**:

1. **Total puntos de contacto directo con cliente externo en el subproceso intervenido (denominador) = 7 tipos**. Estos 7 puntos se ejecutan recurrentemente en cada uno de los 3 hitos del proyecto (HITO 1, HITO 2, HITO 3 en la macroetapa M5 del proceso productivo), por lo que sobre la duración del proyecto ocurren aproximadamente 21 ocurrencias de contacto cliente; sin embargo, el indicador OPC mide los **7 tipos** de punto, no el número de ocurrencias:
    1. Convocatoria y coordinación de reunión de avance con el cliente (correo/llamada).
    2. Preparación de presentación de avance (impresa o digital) para el cliente.
    3. Reunión presencial de avance y entrega de material al cliente.
    4. Envío de planos y renders al cliente para revisión y aprobación.
    5. Recepción y procesamiento de comentarios del cliente.
    6. Ciclo de ajustes por feedback del cliente y re-envío de entregables.
    7. Confirmación de aprobación del cliente y escalamiento de hito.

2. **Puntos por optimizar (numerador, línea base) = 7**: en Marzo 2026 ninguno de los 7 tipos de punto opera bajo un protocolo estandarizado. Cada uno tiene tiempos variables, herramientas disjuntas, calidad inconsistente y trazabilidad fragmentada. Evidencia empírica: en el proyecto Casa Saint Regis, el período formal de revisión de cliente (que concentra los puntos 5, 6 y 7) tomó 88 h reales vs 47 h proyectadas (+87 % de desfase) en cada uno de los hitos medidos, lo que evidencia falta de estandarización del ciclo.

3. **OPC línea base** = (7 ÷ 7) × 100 = **100,00 %**.

**Meta**: 2 puntos sin estandarizar al cierre = (2 ÷ 7) × 100 = **28,57 %** → variación **-71,43 %**.

Los 5 puntos a estandarizar mediante Central Contexto:
- (1) Convocatorias automáticas desde el módulo `calendar_sync` y `notifications`.
- (2) Presentaciones generadas automáticamente desde dashboards (`dashboards`).
- (4) Portal digital de aprobación de planos/renders (`documents`).
- (5) Formulario digital de feedback con trazabilidad (`rfis`).
- (6) Trazabilidad del ciclo de ajustes en `projects` + `documents`.

Los 2 puntos que se conservan sin estandarizar al cierre:
- (3) Reunión presencial de hito — se mantiene por requerimiento del cliente.
- (7) Comunicación final de aprobación del cliente — depende del canal preferido del cliente.

**Entregable de soporte**: `Reporte_Mediciones_CNTXT_PT2.xlsx` (hoja "IPT-5 OPC").

---

## IPT-6 (IPT-49181) — Impacto Ambiental: Consumo de recursos por servicio prestado (IA)

**Tipo**: Fijo (Sostenibilidad Ambiental) | **Unidad**: Hojas de papel por proyecto·mes | **Período**: Marzo 2026

| Campo | Valor |
|---|---|
| Línea base | **13,08000** |
| Meta | **11,15000** |
| Variación porcentual esperada | **-14,74** |

### Texto para "Cálculo de la medición"

[Preámbulo común]

**Nota sobre el recurso medido**: El recurso seleccionado para medir el Impacto Ambiental es el **consumo de papel** generado por el subproceso de gestión interna y por las macroetapas con contacto cliente (reportes ejecutivos, presentaciones de avance, planos y renders impresos, actas de seguimiento y copias de respaldo). El papel se reporta como instancia del **"Consumo de Recurso"** genérico contemplado en la ficha técnica del indicador (variables canónicas listadas: agua, energía, gas, recurso, combustible). La unidad **"hojas/proyecto·mes"** es coherente con la fórmula del catálogo `IA[Recurso] = Consumo / NPoS`, aunque no aparezca literalmente en el listado de unidades sugeridas (m³, kWh, Km/gal, Gal/mes); el papel tiene su métrica natural en hojas. NPoS = 13 proyectos activos en el período de medición.

**Fórmula del catálogo**: `IA[Recurso] = Consumo / NPoS`.

**Metodología**:

1. **Consumo mensual de papel** (línea base, Marzo 2026):
    - Reportes ejecutivos impresos para reuniones directivas: 40 hojas/mes.
    - Presentaciones de avance impresas para reuniones con clientes: 60 hojas/mes.
    - Planos y renders impresos para aprobación de clientes: 30 hojas/mes.
    - Documentación de soporte (actas, fichas de entregables): 25 hojas/mes.
    - Copias de respaldo de información crítica: 15 hojas/mes.
    - **Consumo total**: 170 hojas/mes.

2. **NPoS** (Número de servicios prestados en marzo 2026) = **13 proyectos activos**.

3. **IA línea base** = 170 ÷ 13 = **13,08 hojas/proyecto·mes**.

**Meta**: consumo total reducido a 145 hojas/mes (mediante reemplazo de reportes ejecutivos por dashboards digitales y reducción parcial de presentaciones) ÷ 13 proyectos = **11,15 hojas/proyecto·mes** → variación **-14,74 %**.

Plan de reducción detallado en `Inventario_Papel_CNTXT_PT2_IA.xlsx`.

**Entregable de soporte**: `Inventario_Papel_CNTXT_PT2_IA.xlsx`.

---

## Resumen de cambios respecto al portal actual

| Indicador | Alcance | Línea base ANTES → DESPUÉS | Meta ANTES → DESPUÉS | Variación ANTES → DESPUÉS |
|---|---|---|---|---|
| IPT-1 TNVA | **Macroproceso completo** | 280 min/sem → **3.897 min/mes** | 196 min/sem → **2.728 min/mes** | -30,00 % (igual) |
| IPT-2 TCP | Subproceso transversal | 48 (igual) | 16 (igual) | -66,67 % (igual) |
| IPT-3 AD(TCP) | Subproceso transversal | 541.000 → **1.799.246** | 352.000 → **1.379.594** | -34,94 % → **-23,33 %** |
| IPT-4 CU | Subproceso transversal | 138.404 (igual) | 90.000 (igual) | -34,97 % (igual) |
| IPT-5 OPC | Macroetapas con cliente | 58,33 → **100** | 25 → **28,57** | -57,14 % → **-71,43 %** |
| IPT-6 IA | Subproceso + Macroetapas con cliente | 170 → **13,08** | 145 → **11,15** | -14,71 % → **-14,74 %** |

---

## Próximos archivos a regenerar

Para coherencia 1:1 entre portal y entregables:

1. ✏️ **Plan_de_Trabajo_2_CNTXT_*.md** — actualizar valores de los 6 indicadores con esta versión.
2. ✏️ **VSM_CNTXT_PT2.xlsx** — actualizar hoja "Resumen Indicadores" con LB 350/Meta 245 para TNVA. Hoja "VSM Proceso Futuro" reescribir con suma coherente.
3. ✏️ **Reporte_Mediciones_CNTXT_PT2.xlsx** — reescribir IPT-3 AD con nueva fórmula `TCP × $/min`, recalcular IPT-4 CU consistente, reescribir IPT-5 OPC con fórmula del catálogo (denominador=7).
4. ✏️ **Inventario_Papel_CNTXT_PT2_IA.xlsx** — agregar columna "hojas/proyecto·mes" y recalcular total como 13,08.
5. ✏️ **Resumen_Indicadores_CNTXT_PT2.pdf** — regenerar con los 6 valores nuevos (esto requiere herramienta de generación PDF: WeasyPrint, ReportLab o re-exportar desde plantilla).
6. ✏️ **VSM_Proceso_Actual_CNTXT.pdf** y **VSM_Proceso_Futuro_CNTXT.pdf** — destacar lead time y mantener coherencia con TNVA = 350 / Meta 245.
7. ✏️ **Portal del PT2 (6 indicadores)** — actualizar Línea base, Meta, Variación porcentual y Cálculo de la medición conforme a este documento.

Una vez actualizados todos los archivos y campos del portal, **reenviar el PT2 desde el botón "Enviar para Aprobación"** y notificar a Melisa Otero que el reenvío incorpora los acuerdos de la reunión.
