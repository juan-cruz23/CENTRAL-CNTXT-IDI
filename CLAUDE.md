# CLAUDE.md — Central Contexto

Archivo de instrucciones para Claude Code en este proyecto.
Ver plantillas de issues en: `/home/mrodriguez/proyectos/PLANTILLAS.md`

---

## PROYECTO

**Nombre:** Central Contexto 2.0
**Cliente:** CNTXT — Casa de Diseño S.A.S. (NIT 900.948.892-7)
**Descripción:** Plataforma de gestión de proyectos inmobiliarios para CNTXT. Reemplaza tablas de Google Sheets y herramientas dispersas con una fuente única de verdad.
**Consultor:** Miguel Bernardo Rodríguez Torres — INDUNNOVA S.A.S.
**Intervención Fábricas de Productividad:** 09/04/2026 – 18/06/2026

---

## STACK TÉCNICO

- **Backend:** Django 5.x + Django REST Framework
- **Frontend:** HTMX + Crispy Forms + Tailwind CSS
- **BD local:** SQLite (`db.sqlite3`)
- **BD producción:** PostgreSQL (Google Cloud Run) — sin acceso directo
- **Tareas async:** Celery + Redis
- **Python:** 3.11+
- **Linter:** Ruff | **Templates:** djLint
- **Tests:** pytest-django + factory-boy

### Estructura de apps (`apps/`)
```
accounts        — Usuarios, roles, paquetes de acceso
calendar_sync   — Sincronización de calendarios
capacity        — Capacidad del equipo
common          — Utilidades compartidas
dashboards      — Dashboard principal y reportes
documents       — Documentos y prerrequisitos
financials      — Finanzas, pricing
geography       — Geografía (municipios, países)
imports         — Importación masiva de datos
metrics         — Indicadores (SPI, CPI, EVM)
notifications   — Notificaciones
organizations   — Clientes y terceros
projects        — Proyectos y módulo principal
rfis            — RFIs
satisfaction    — Satisfacción de clientes
services        — Servicios y pricing
terceros        — Terceros
timetracking    — Seguimiento de tiempo
```

---

## RESTRICCIONES — LEER ANTES DE CADA TAREA

1. **BD local = SQLite | BD producción = PostgreSQL**
2. **Sin acceso a BD producción ni a Google Cloud Run**
3. Antes de cada tarea: ¿se resuelve por código o necesita BD producción?
   - Si necesita BD producción → documentarlo en el issue, NO ejecutar
4. **No asumir, no inventar** — si algo no está claro, preguntar primero
5. No crear archivos innecesarios. Preferir editar archivos existentes.
6. No agregar features, refactors ni mejoras que no fueron pedidas.
7. No agregar docstrings, comentarios ni type hints en código no modificado.
8. Commits solo cuando el usuario lo pida explícitamente.

---

## FLUJO DE TRABAJO

### Antes de empezar una tarea
1. Leer este archivo y PLANTILLAS.md
2. Listar issues abiertos y cerrados de GitHub
3. Revisar si hay issues cerrados que deberían reabrirse
4. Priorizar por impacto en el piloto / fecha más próxima
5. Pregunta: ¿la tarea necesita BD producción?

### Al crear/actualizar issues
- Usar las plantillas de `/home/mrodriguez/proyectos/PLANTILLAS.md`
- Un issue por tema, nunca duplicar
- Etiquetar modelo al final del título: `[-H]` `[-S]` `[-O]`
- Etiquetar `@Indunnova` al crear issues

### Modelos (al final del título del issue)
| Etiqueta | Modelo | Cuándo usar |
|----------|--------|-------------|
| `[-H]` | Haiku | Bug simple, cambio pequeño, config puntual |
| `[-S]` | Sonnet | Bug medio, mejora, feature, dashboard |
| `[-O]` | Opus | Módulo nuevo, arquitectura, lógica compleja |

---

## CONVENCIONES DE CÓDIGO

- **Vistas:** Class-based views (CBV) con mixins de Django
- **Templates:** HTMX para interacciones parciales, sin SPA
- **Forms:** django-crispy-forms con layout de Tailwind
- **URLs:** `apps/<app>/urls.py` incluidas en `config/urls.py`
- **Tests:** `tests/` en raíz del proyecto, con factory-boy
- **Migraciones:** siempre crear (`makemigrations`) antes de `migrate`
- **Settings:** `config/settings/` — base, local, production, test

---

## PILOTO — FECHA CRÍTICA

**Reunión piloto:** 2026-04-08 (miércoles) — **FECHA YA PASADA** (hoy: 2026-04-17)
**Proyecto piloto:** Select (unidad de vivienda residencial)

Checklist previo:
- [ ] Desplegar todos los cambios a producción
- [ ] Crear usuario por cada rol activo
- [ ] Parametrizar maestros base (categorías, estados, festivos, geografía)
- [ ] Cargar plantilla de prerrequisitos para categoría del proyecto piloto
- [ ] Crear proyecto piloto con datos reales (Select)
- [ ] Verificar filtros, fechas y cronograma
- [ ] Verificar flujo de documentos: carga, aprobación, trazabilidad

---

## ISSUES ACTIVOS (resumen rápido)

| # | Título | Tipo | Modelo | Estado |
|---|--------|------|--------|--------|
| #1 | Módulo Proyectos — UI, filtros y campos | Mejora + Bug | [-S] | 🟡 Bugs resueltos: botón Agregar (e936c29), botón Atrás y filtro código (922c39b). Fase actual ya estaba. Resto pendiente. |
| #2 | Módulo Cronograma — renombrar Hitos y nuevas funcionalidades | Mejora | [-O] | 🟡 Avance significativo: árbol de acciones con agrupación por fase (db80110), modal agregar servicio con árbol y responsables (b710c8d), fixes z-index y CSRF (5beab0c, 6782cf7), registro de avance por acción y aprobación de servicios (072249f). Pendiente: integración hitos, fechas por fases, revisiones. |
| #3 | Módulo Usuarios / Accesos — roles y permisos | Mejora | [-S] | 🔴 Pendiente |
| #4 | Módulo Servicios / Pricing — sincronización | Mejora + Bug | [-S] | 🔴 Pendiente |
| #5 | Módulo Configuración / Maestros — nuevas tablas | Mejora | [-O] | 🟡 Reabierto: Deliverable (f4e96c9), KeyActivity (3a224d7), ServiceActivity (4a3e120) con CRUD y seed desde Excel. Base anterior cerrada (seed_cntxt_masters). |
| #6 | Módulo Clientes / Terceros — CRM y carga masiva | Mejora | [-O] | 🔴 Pendiente |
| #7 | Módulo Documentos / Prerrequisitos — checklist | Mejora + Bug | [-S] | 🟡 Bloque 2 y 3 resueltos (e936c29). Pendiente: bloquear avance por requisitos. |
| #8 | Módulo Dashboard / Reportes — seguimiento | Mejora | [-S] | 🟡 Gantt colapsable con entregables, actividades y acciones (fa06de0), servicios del cronograma en Gantt (1397ceb), scroll independiente X/Y (d3d8476), servicios en sección Fases y Servicios (9ebb4f4). Pendiente: indicadores SPI/CPI, reportes. |
| #9 | Piloto — primer proyecto real en el sistema | Hito | [-S] | 📅 2026-04-08 — fecha pasada, verificar estado real |
| #10 | feat(servicios): desglose de pricing en ServiceTemplate | Mejora | [-S] | 🟡 Gestión inline de entregables, actividades y acciones con pricing unificado (1483f54), importar/exportar Excel con árbol jerárquico completo (e4ea2f3). Pendiente: validar en producción. |
| #11 | feat(cronograma): agregar servicios con fecha planeada y cálculo automático | Mejora | [-S] | ✅ Implementado (c826829): agregar servicios desde pricing, fecha entrega automática (horas+jornada+festivos), selector responsable por rol con preselección, auto-sync fechas y valor total del proyecto vía señal, equipo con roles requeridos, prerrequisitos automáticos por categoría, fix form proyecto. |

### Últimos commits
| Commit | Descripción |
|--------|-------------|
| 072249f | feat(cronograma): registro de avance por acción y aprobación de servicios |
| 9ebb4f4 | feat(dashboard): mostrar servicios del cronograma en sección Fases y Servicios |
| d3d8476 | fix(gantt): collapsible tree funcional + scroll independiente en X e Y |
| fa06de0 | feat(dashboard): Gantt colapsable con entregables, actividades y acciones |
| 1397ceb | fix(dashboard): incluir servicios del cronograma en Gantt del proyecto |
| db80110 | feat(cronograma): árbol de acciones, agrupación por fase y modal de edición |
| b710c8d | feat(cronograma): modal de agregar servicio con árbol de acciones y responsables |
| e4ea2f3 | feat(servicios): importar/exportar Excel con árbol completo y detalle jerárquico |
| 1483f54 | feat(servicios): gestión inline de entregables, actividades y acciones con pricing unificado |
| 4a3e120 | feat(maestros): agregar acciones clave (ServiceActivity) con CRUD y seed |
| 3a224d7 | feat(maestros): agregar modelo KeyActivity con CRUD y seed desde Excel |
| f4e96c9 | feat(maestros): agregar modelo Deliverable con CRUD y seed desde Excel |
