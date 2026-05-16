# Estrategia de ajustes al PT2 — Mayo 2026

**Empresa**: CNTXT — Casa de Diseño S.A.S. (NIT 900.948.892-7)
**Plan de Trabajo**: PT2 CONTEXTO ARQUITECTURA (Salesforce ID `a0URQ00000LxlgM2AR`)
**Línea de servicio**: Productividad Operacional
**Estado al 7-may-2026**: PT1 Aprobado / **PT2 Rechazado** (vigente desde 4/05/2026)
**Aprobador del rechazo vigente**: Melisa Otero (Líder de Línea)

---

## 1. Contexto del rechazo

Después de la reunión con Melisa Otero, Yoing Mauricio Barco (Gestor) y Laura Giordanelli (Supervisora), la solicitud específica para el reenvío del PT2 es:

> **Reflejar el alcance completo del proceso productivo (solicitud del cliente → diseño/coordinación → entrega → facturación) y delimitar explícitamente que los cálculos de los indicadores se realizan únicamente sobre el "pedacito" intervenido, que es la gestión interna de los proyectos. La herramienta habilitadora es Central Contexto.**

Esta solicitud es coherente con el **criterio #5** de la "Lista de chequeo cumplimiento V3" (hoja "Plan 2"):

> *"Detalle cuál es el alcance de la medición… Sea específico en el área, proceso, línea de producción, producto o servicio en el que se levantó la medición (este debe mantenerse en las mediciones intermedias y de cierre). Recuerde indicar no solo sobre qué producto, sino sobre cuánta producción, se está realizando el análisis."*

---

## 2. Histórico de aprobaciones (Salesforce ProcessSteps)

| # | Fecha | Paso | Estado | Por | Comentario clave |
|---|---|---|---|---|---|
| 1 | 17/03/2026 15:16 | Líder de Línea | Rechazado | Melisa Otero | PT1 mal alineado: enfoque transformación digital, no productividad operacional |
| 2 | 20/03/2026 11:35 | Gestor | Aprobado | Yoing M. Barco | Replanteo del PT1 hacia productividad operacional |
| 3 | 30/03/2026 03:53 | Líder de Línea | Aprobado (PT1) | Melisa Otero | Aviso anticipado: cuidar fórmulas y unidades en PT2 |
| 4 | 17/04/2026 19:28 | Solicitud aprobación | Enviado | INDUNNOVA | v1 del PT2 |
| 5 | 20/04/2026 08:35 | Gestor | Aprobado | Yoing M. Barco | Cumple lista de chequeo |
| 6 | **23/04/2026 21:03** | **Líder de Línea** | **Rechazado** | **Melisa Otero** | **3 indicadores con problemas técnicos (ver §3)** |
| 7 | 28/04/2026 10:08 | Solicitud aprobación | Enviado | INDUNNOVA | Reenvío con correcciones del primer rechazo |
| 8 | 28/04/2026 16:50 | Gestor | Rechazado | Yoing M. Barco | (sin comentario) |
| 9 | 29/04/2026 21:27 | Solicitud aprobación | Enviado | INDUNNOVA | Reenvío con correcciones (segunda iteración) |
| 10 | 30/04/2026 08:29 | Gestor | Aprobado | Yoing M. Barco | "Se aprueba luego de realizar los cambios requeridos" |
| 11 | **04/05/2026 10:14** | **Líder de Línea** | **Rechazado (vigente)** | **Melisa Otero** | "Solicito reunión con Extensionista, Gestor y Supervisor" |

---

## 3. Observaciones técnicas del rechazo del 23/04 (Líder de Línea)

Tres indicadores con problemas según Melisa Otero:

### IPT-49180 — Ahorro AD(TCP)
> "Se basa en la cuantificación de horas de desperdicio (TNVA y reprocesos) por perfil, y no en el tiempo de ciclo productivo total multiplicado por un valor por minuto, como lo establece la metodología."

### IPT-49183 — Costo Unitario (CU)
> "Fórmula: `CU = CT / Número de productos`. Usted usa: Costo total desperdicios / 13 proyectos activos. Unidad de medida: Pesos colombianos. Usted afirma $28.673/proyecto/mes."

### IPT-49184 — Optimización Puntos de Contacto (OPC)
> "Definición: Optimización de los subprocesos y/o actividades en los cuales se tiene contacto directo con el cliente dentro del proceso productivo. Usted afirma: 'Número de puntos donde la información es transcrita, transferida o consolidada de una herramienta o persona a otra en el ciclo completo de reporte'. La medición realizada corresponde a puntos de transferencia interna de información. Adicionalmente, la línea base se expresa como 7 (valor absoluto), cuando la unidad de medida es porcentaje."

---

## 4. Estado portal-vs-documento (DESALINEACIÓN DETECTADA)

Las fichas en el portal fueron **modificadas el 29/04** para responder al primer rechazo del Gestor. Pero el documento maestro `Plan_de_Trabajo_2_CNTXT_Fabricas_de_Productividad.md` **no se actualizó** — quedó con los valores originales del envío v1.

| Indicador | LB en doc (`PT2.md`) | LB en portal (post-29/04) | Comentario |
|---|---|---|---|
| **TNVA** | 280 min/sem | 280 min/sem | ✅ alineado |
| **TCP** | 48 hs hábiles | 48 hs hábiles | ✅ alineado |
| **AD(TCP)** | $1.050.000/mes | **$541.000/mes** | ❌ desalineado |
| **CU** | $81.923/proy·mes | **$138.404/proy·mes** | ❌ desalineado |
| **OPC** | 7 puntos | **58,33 %** | ❌ desalineado |
| **IA** | 170 hojas/mes | 170 hojas/mes | ✅ alineado |

**Acción**: cuando definamos los valores definitivos para el reenvío, actualizar **ambos** (portal y `PT2.md`) en el mismo bloque para no volver a desincronizar.

---

## 5. Decisiones tomadas

1. **Periodo de medición**: dejar **Marzo 2026** (no se ha cuestionado oficialmente; si lo cuestionan, justificar como excepción autorizada por la fecha real de levantamiento).
2. **Impacto Ambiental**: mantener **papel** como recurso (los indicadores ya están definidos y no se pueden cambiar a esta altura).
3. **TNVA — alcance ampliado al MACROPROCESO COMPLETO + unidad mensual**: el TNVA mide las 12 NVAs distribuidas en las 7 macroetapas + el subproceso transversal. LB **3.897 min/mes** (= 900 min/sem × 4,33), meta **2.728 min/mes** (= 630 min/sem × 4,33), variación -30 %. Unidad mensual elegida para alinear con la "temporalidad mensual" exigida en la Lista de chequeo V3.
4. **AD(TCP)**: aplicar fórmula correcta `AD = TCP × $/min` — LB **$1.799.246/mes**, meta **$1.379.594/mes** (-23,33 %, escenario 70 % eliminación NVA). Alcance: solo subproceso transversal de gestión interna (donde se sustenta el cálculo de costo).
5. **OPC**: aplicar fórmula correcta del catálogo — LB **100 %** (7/7 puntos contacto cliente sin estandarizar), meta **28,57 %** (2/7), variación **-71,43 %**. Alcance: macroetapas con contacto cliente.
6. **IA papel**: aplicar fórmula `IA = Consumo / NPoS` — LB **13,08 hojas/proyecto·mes**, meta **11,15** (-14,74 %).
7. **Mapa del proceso**: el VSM se rediseña en dos niveles — flujo macro de 7 macroetapas (Captación → Propuesta → Estructuración → Producción → Aprobaciones → Entrega → Facturación) con el subproceso transversal de Gestión Interna superpuesto.
8. **Alcance**: luz verde para modificar portal + entregables (Excel) + PDFs + documento maestro PT2.md, todos en una sola versión coherente.

## 5.1. Inconsistencias internas detectadas en V2 (al leer todos los entregables)

Tras descargar y leer los V2 del portal, se confirmaron varias **inconsistencias internas** que justifican aún más el reenvío:

| Inconsistencia | Ubicación | Detalle |
|---|---|---|
| TNVA discrepa entre portal y entregables | Portal vs PDF/Excel V2 | Portal: 280/196 — PDF: 350/245 — Excel suma: 280 NVAs (5) o 350 (7) |
| Meta TNVA del Excel V2 | VSM_ACTUALIZADO_1.xlsx | Hoja "VSM Proceso Futuro" tiene "TIEMPO NVA META: 196" pero hoja "Resumen Indicadores" dice meta 245 |
| AD(TCP) V2 sigue mal | Reporte_Mediciones (2).xlsx | Declara fórmula "AD = Σ (Horas TNVA × Costo/h)" — sigue siendo "horas NVA × tarifa" en lugar de `TCP × $/min` |
| OPC V2 fórmula equivocada | Reporte_Mediciones (2).xlsx | Declara denominador = "Total subprocesos del ciclo" (12) cuando el catálogo pide "Total puntos contacto cliente" (7) |
| Lead Time del VSM | VSM_ACTUALIZADO_1.xlsx | Suma 700 min/sem (420 VA + 280 NVA) — pero si NVA real son 350, debería ser 770 min/sem. Inconsistencia interna del Excel V2. |

**Implicación**: el reenvío necesita NO solo corregir las 3 observaciones técnicas de Melisa, también **subsanar las inconsistencias internas** entre los entregables y el portal. La luz verde del usuario para modificar todo permite hacer esto en una sola pasada.

---

## 6. Estrategia de respuesta — 3 capas

### Capa 1 — Preámbulo común para los 6 indicadores

Texto base a anteponer al campo "Cálculo de la medición" de cada uno de los 6 indicadores (con notas específicas adicionales en TCP e IA):

> **Alcance del proceso productivo de CNTXT — Casa de Diseño S.A.S.**
>
> CNTXT ejecuta proyectos de arquitectura, diseño, visualización y servicios BIM para el sector inmobiliario. El proceso productivo completo comprende: (1) recepción de la solicitud del cliente y briefing, (2) estructuración del proyecto y propuesta económica, (3) diseño arquitectónico, visualización y BIM, (4) coordinación con disciplinas externas (estructural, MEP, normatividad), (5) ciclo de aprobaciones del cliente, (6) entrega del proyecto y (7) facturación.
>
> La intervención de Fábricas de Productividad se delimita al **subproceso transversal de gestión interna de los 13 proyectos activos** — administración, coordinación, monitoreo y control de avance que ejecutan, de forma compartida, el Líder de Proyecto, el Director Ejecutivo y el Director Creativo.
>
> La herramienta digital habilitadora del rediseño es **Central Contexto**, plataforma propietaria desarrollada durante la intervención, que sustituye el uso disperso de Google Sheets, Trello y planillas físicas por una fuente única de verdad.
>
> Los cálculos del presente indicador se realizan exclusivamente sobre dicho subproceso de gestión interna. Los VSM adjuntos (`VSM_Proceso_Actual_CNTXT.pdf` y `VSM_Proceso_Futuro_CNTXT.pdf`) muestran el proceso productivo completo con el subproceso intervenido resaltado.

**Nota específica para TCP (IPT-49182)**:
> El "tiempo de ciclo productivo" reportado en este indicador NO corresponde al ciclo del proyecto inmobiliario completo (típicamente 6 a 18 meses por proyecto), sino al **ciclo de detección y respuesta a eventos operativos** dentro del subproceso de gestión interna: desde que ocurre un evento (cambio de estado, retraso de disciplina externa, repriorización por urgencia de cliente) hasta la decisión correctiva del equipo directivo. Esta delimitación es coherente con la oportunidad de mejora identificada en el diagnóstico del PT1.

**Nota específica para IA (IPT-49181)**:
> El recurso seleccionado para medir el Impacto Ambiental es el **consumo de papel** generado por el subproceso de gestión interna (reportes ejecutivos, presentaciones de avance, planos y renders impresos para reuniones presenciales con cliente, actas de seguimiento y copias de respaldo). El consumo se cuantifica en hojas/mes y se divide por el Número de Productos o Servicios prestados (NPoS = 13 proyectos activos en el periodo de medición), siguiendo la fórmula `IA[Papel] = Consumo / NPoS`.

### Capa 2 — Correcciones técnicas en los 3 con error de fórmula

#### IPT-49180 AD(TCP) — recálculo con fórmula del catálogo

Fórmula oficial: `AD[TCP] = TCP × Valor por minuto`

| Variable | Cálculo |
|---|---|
| TCP total mensual del subproceso | (555 + 165 + 120) min/sem × 4,33 sem/mes = **3.637,20 min/mes** |
| CT (de IPT-49183) | $1.799.246/mes |
| Valor por minuto | $1.799.246 / 3.637,20 = **$494,69/min** |
| **AD inicial** | 3.637,20 × $494,69 = **$1.799.246/mes** |

**Alerta**: la meta cargada actual de **-34,94 %** ($352.000) implica reducir AD a $1.170.486 → reducir TCP a 2.366 min/mes → eliminar 1.271 min/mes. Pero el TNVA total identificado es solo 1.212 min/mes. **La meta -34,94 % es matemáticamente inalcanzable** solo eliminando NVA.

Escenarios viables:

| Escenario | TCP final | AD final | Variación | Valoración |
|---|---|---|---|---|
| Eliminar 30 % del NVA | 3.273 min | $1.619.342 | -9,99 % | Apenas pasa el 8 % mínimo |
| Eliminar 50 % del NVA | 3.031 min | $1.499.665 | -16,65 % | Holgado |
| **Eliminar 70 % del NVA** | **2.788 min** | **$1.379.594** | **-23,33 %** | **Recomendado: ambicioso pero sustentado** |
| Eliminar 100 % del NVA | 2.425 min | $1.199.785 | -33,33 % | Cero NVA al cierre — irreal |

**Decisión pendiente**: confirmar escenario.

#### IPT-49184 OPC — corrección de fórmula

Fórmula oficial: `OPC = (Puntos por optimizar / Total puntos contacto cliente) × 100`

| | Antes (cargado) | Propuesto |
|---|---|---|
| Denominador | 12 (total subprocesos del ciclo) | **7** (total puntos contacto con cliente) |
| Numerador inicial | 7 (puntos con cliente) | **7** (puntos sin estandarizar al inicio) |
| Numerador final | — | **2** (puntos sin estandarizar al cierre) |
| Línea base | 58,33 % | **100,00 %** |
| Meta | 25,00 % | **28,57 %** |
| Variación | -57,14 % | **-71,43 %** |

Los 7 puntos de contacto con cliente identificados (válidos):
1. Convocatoria y coordinación de reunión de avance con el cliente
2. Preparación de presentación de avance impresa
3. Reunión presencial de avance con entrega de material impreso
4. Envío de planos y renders al cliente para revisión y aprobación
5. Recepción y procesamiento de comentarios del cliente
6. Ciclo de ajustes por feedback del cliente y re-envío
7. Confirmación de aprobación del cliente y escalamiento de hito

**Decisión pendiente**: confirmar cuántos puntos quedan sin estandarizar al cierre (propuesto: 2).

#### IPT-49181 IA papel — dividir por NPoS

Fórmula oficial: `IA[Recurso] = Consumo / NPoS`

| | Antes | Propuesto |
|---|---|---|
| Línea base | 170 hojas/mes (sin dividir) | **13,08 hojas/proyecto·mes** (= 170 / 13) |
| Meta | 145 hojas/mes (sin dividir) | **11,15 hojas/proyecto·mes** (= 145 / 13) |
| Variación | -14,71 % | **-14,74 %** (igual) |

Pendiente verificar si el campo "unidad de medida" del sistema permite cambiar a "hojas/proyecto/mes". Si no, dejarlo en el campo de cálculo y aclarar.

### Capa 3 — Aclaración de alcance en los 3 conceptualmente correctos

**TNVA, TCP, CU**: solo agregar el preámbulo de Capa 1; el cálculo se mantiene.

Adicional para **TCP**: agregar la nota específica del subproceso (capa 1).

---

## 7. Validación contra "Lista de chequeo cumplimiento V3" (Innpulsa)

| Criterio | Aplicación a este reenvío |
|---|---|
| #5 — Detallar alcance específico (área, proceso, producto/servicio) | ✅ Cubierto por preámbulo de Capa 1 |
| #6 — Conservar fórmula del catálogo, evidenciar numerador/denominador/resultado | ✅ Cubierto por correcciones de Capa 2 (AD, OPC, IA) |
| #9 — Decimales (mínimo 2, máximo 5) | ✅ Todos los indicadores en formato 2 decimales |
| #11 — Periodo (mes y año) | ✅ Marzo 2026 declarado en los 6 |
| #19 — Meta por lógica del indicador, no por el 8 % mínimo | ✅ todas las metas > 8 % y sustentadas |
| #21 — Variación porcentual ≥ 8 % | ✅ Todos cumplen (-9,99 % en escenario conservador AD; resto >14 %) |
| #22-23 — Unidad de medida no debe cambiarse | ⚠️ Verificar IA (unidad sugerida no contempla "hojas") |
| #28 — Productividad Operacional: VSM con tiempos de ciclo, NVA, lead time, puntos críticos | ⚠️ Verificar que los VSM cargados muestran lead time y puntos críticos explícitos |

---

## 8. Próximos pasos

1. ⏳ **Definir escenario AD(TCP)** (Miguel decide).
2. ⏳ **Definir numerador final OPC** (Miguel decide).
3. ⏳ Revisar VSM cargados (`VSM_Proceso_Actual_CNTXT.pdf`, `VSM_Proceso_Futuro_CNTXT.pdf`) para confirmar que cumplen criterio #28.
4. ⏳ Aplicar Capa 1 (preámbulo) en los 6 indicadores en el portal vía `b.py`.
5. ⏳ Aplicar correcciones de Capa 2 en AD, OPC, IA.
6. ⏳ Actualizar `Plan_de_Trabajo_2_CNTXT_Fabricas_de_Productividad.md` con los números finales para mantener portal y doc alineados.
7. ⏳ Reenviar el PT2 desde el botón "Enviar para Aprobación" del Plan de Trabajo.
8. ⏳ Notificar a Melisa Otero que el reenvío incorpora lo conversado en la reunión.

---

## Referencias

- Lista de chequeo del programa: `~/Documents/Lista chequeo cumplimiento V3.xlsx`
- Documento maestro del PT2: `Plan_de_Trabajo_2_CNTXT_Fabricas_de_Productividad.md`
- VSM y reportes: `VSM_CNTXT_PT2.xlsx`, `Reporte_Mediciones_CNTXT_PT2.xlsx`, `Inventario_Papel_CNTXT_PT2_IA.xlsx`
- Automatización portal: `~/repos/fabricas_playwright/` (`daemon.py` + `b.py`)
- URL del PT en el portal: `https://innpulsacolombia.my.site.com/fabricasdeproductividad/s/fp-plantrabajo-obj/a0URQ00000LxlgM2AR/plan-de-trabajo-contexto-arquitectura`
