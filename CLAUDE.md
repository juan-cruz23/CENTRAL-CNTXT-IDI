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

**Reunión piloto:** 2026-04-08 (miércoles)
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
| #2 | Módulo Cronograma — renombrar Hitos y nuevas funcionalidades | Mejora | [-O] | 🟡 Rename completado (5d61c6a). Pendiente: integración Pricing, fechas automáticas, festivos, asignación, revisiones. |
| #3 | Módulo Usuarios / Accesos — roles y permisos | Mejora | [-S] | 🔴 Pendiente |
| #4 | Módulo Servicios / Pricing — sincronización | Mejora + Bug | [-S] | 🔴 Pendiente |
| #5 | Módulo Configuración / Maestros — nuevas tablas | Mejora | [-O] | 🟡 Categorías de proyecto ya implementadas. Resto pendiente. |
| #6 | Módulo Clientes / Terceros — CRM y carga masiva | Mejora | [-O] | 🔴 Pendiente |
| #7 | Módulo Documentos / Prerrequisitos — checklist | Mejora + Bug | [-S] | 🟡 Bloque 2 y 3 resueltos (e936c29). Pendiente: bloquear avance por requisitos. |
| #8 | Módulo Dashboard / Reportes — seguimiento | Mejora | [-S] | 🔴 Pendiente |
| #9 | Piloto — primer proyecto real en el sistema | Hito | [-S] | 📅 2026-04-08 |

### Últimos commits
| Commit | Descripción |
|--------|-------------|
| 5d61c6a | fix: rename Hitos → Cronograma/Actividades en UI restante |
| 922c39b | fix: botón Atrás en edición y filtro por código en lista de proyectos |
| e936c29 | feat: audiencia docs, DocumentTemplate, fix botón Agregar HTMX 2.0 |
| 464c980 | feat: maestro de categorías de proyecto con CRUD completo |
| c36466b | feat: filtros de usuarios por rol en formularios y visibilidad de proyectos |
