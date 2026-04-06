# PLANTILLAS DE ISSUES — Indunnova

Archivo de referencia para Claude Code.
Usar junto con CLAUDE.md de cada proyecto.

REGLAS GENERALES:
- Un issue por tema, nunca duplicar
- Si algo no está claro → preguntar antes de ejecutar
- No asumir, no inventar
- BD local: SQLite | BD producción: PostgreSQL
- Si necesita BD producción → documentarlo en el issue
- Etiquetar @Indunnova al crear issues
- Modelo al final del título: [-H] [-S] [-O]

MODELOS:
[-H] Haiku  → bug simple, cambio pequeño, configuración puntual
[-S] Sonnet → bug medio, mejora, feature, importar/exportar, dashboard
[-O] Opus   → módulo nuevo, arquitectura, lógica compleja

---

## PLANTILLA A — MÓDULO NUEVO [-O]

Usar cuando: el cliente pide algo que NO existe en el sistema.
Ejemplos: "necesito un módulo de inventario", "quiero gestionar contratos"

```
# Modulo: [Nombre] [-O]
Fecha: [YYYY-MM-DD] | Proyecto: [Nombre]

## 1. Objetivo
[Qué hace y para quién, 2-3 líneas]

## 2. Problema que resuelve
[Dolor actual del usuario]

## 3. Funcionalidades esperadas
- [ ] Funcionalidad 1
- [ ] Funcionalidad 2

## 4. Reglas de negocio
- Regla 1

## 5. Datos involucrados
- Entidad 1: campos principales
- Relaciones entre entidades

## 6. Interfaces / Pantallas
- Pantalla 1: qué muestra, qué acciones tiene

## 7. Integraciones
[Describir o "Ninguna"]

## 8. Lo que NO incluye
- No incluye X

## 9. Como se que esta bien
- [ ] Criterio 1
- [ ] Criterio 2

## Requiere acceso a BD producción
[Sí / No — si Sí, documentar en el issue]
```

---

## PLANTILLA B — BUG [-H/-S]

Usar cuando: algo que YA EXISTE deja de funcionar.
Ejemplos: "me da error al guardar", "el botón no hace nada", "el cálculo está mal"

```
# Bug: [Titulo] [-H/-S]
Fecha: [YYYY-MM-DD] | Modulo: [Afectado] | Prioridad: [Alta/Media/Baja]

## 1. Que esta pasando
[Cuando hago X, pasa Y]

## 2. Que deberia pasar
[Cuando hago X, deberia pasar Z]

## 3. Pasos para reproducir
1. Ir a...
2. Hacer clic en...
3. Se observa que...

## 4. Donde creo que esta el problema
[Archivo o "No se, que Claude lo busque"]

## 5. Que NO se debe cambiar
[Lo que debe permanecer igual]

## 6. Como valido que se arreglo
- [ ] Criterio 1

## Requiere acceso a BD producción
[Sí / No]
```

---

## PLANTILLA C — MEJORA [-S]

Usar cuando: algo funciona pero el cliente quiere que funcione diferente o mejor.
Ejemplos: "quiero que también muestre X", "cambiar cómo se calcula Y", "agregar un filtro"

```
# Mejora: [Titulo] [-S]
Fecha: [YYYY-MM-DD] | Modulo: [Afectado]

## 1. Como funciona hoy
[Estado actual]

## 2. Que quiero cambiar
[Cambio concreto]

## 3. Por que
[Necesidad del usuario]

## 4. Reglas nuevas o modificadas
[Si aplica]

## 5. Archivos involucrados
[Lista o "No se"]

## 6. Lo que NO debe cambiar
[Funcionalidad que sigue igual]

## 7. Como se que quedo bien
- [ ] Criterio 1

## Requiere acceso a BD producción
[Sí / No]
```

---

## PLANTILLA D — CONFIGURACIÓN [-H]

Usar cuando: el cliente pide cambiar un dato, parámetro o ajuste puntual.
Ejemplos: "cambia el nombre de este campo", "el precio base debe ser X", "activa esta opción"

```
# Configuracion: [Titulo] [-H]
Fecha: [YYYY-MM-DD] | Modulo: [Afectado]

## 1. Que se necesita configurar
[Parámetro, dato o ajuste puntual]

## 2. Valor actual → Valor esperado
[Lo que está hoy] → [Lo que debería quedar]

## 3. Por que
[Razón del cambio]

## 4. Requiere acceso a BD producción
[Sí → confirmar con @Indunnova primero]
[No → Claude lo hace por código]

## 5. Como valido que quedo bien
- [ ] Criterio 1
```

---

## PLANTILLA E — CONSULTA / REPORTE [-S]

Usar cuando: el cliente pregunta por datos o necesita ver información del sistema.
Ejemplos: "¿cuántos clientes tenemos?", "dame ventas del mes", "¿por qué no aparece X?"

```
# Reporte: [Titulo] [-S]
Fecha: [YYYY-MM-DD] | Modulo: [Afectado]

## 1. Que necesita el cliente
[¿Cuántos X? / ¿Por qué Y? / Listado de Z]

## 2. Formato esperado
[Pantalla / Excel / CSV / PDF]

## 3. Filtros requeridos
[Fecha, estado, usuario, etc.]

## 4. Requiere acceso a BD producción
[Sí / No]

## 5. Como valido que quedo bien
- [ ] El dato es correcto
- [ ] Los filtros funcionan
```

---

## PLANTILLA F — IMPORTAR / EXPORTAR [-S]

Usar cuando: el cliente necesita subir datos al sistema o descargar información.
Ejemplos: "subir listado de productos en Excel", "exportar cotizaciones en PDF"

```
# Importar/Exportar: [Titulo] [-S]
Fecha: [YYYY-MM-DD] | Modulo: [Afectado]

## 1. Tipo
[ ] Importar datos al sistema
[ ] Exportar datos del sistema

## 2. Formato
[Excel / CSV / PDF / Otro]

## 3. Datos involucrados
[Campos y entidades]

## 4. Reglas de validacion al importar
[Qué debe validar]

## 5. Requiere acceso a BD producción
[Sí / No]

## 6. Como valido que quedo bien
- [ ] Importa sin errores
- [ ] Exporta con todos los campos correctos
```

---

## PLANTILLA G — TARJETA / DASHBOARD [-S]

Usar cuando: el cliente pide ver un número clave, indicador o resumen visual en pantalla.
Ejemplos: "total de ventas del mes en el inicio", "tarjeta con clientes activos"

```
# Dashboard: [Titulo] [-S]
Fecha: [YYYY-MM-DD] | Modulo: [Afectado]

## 1. Indicador o tarjeta
[Número clave, resumen visual, indicador]

## 2. Dato que muestra
[De dónde viene, qué calcula]

## 3. Filtros o segmentacion
[Por fecha, usuario, estado, etc.]

## 4. Ubicacion en el sistema
[En qué pantalla aparece]

## 5. Requiere acceso a BD producción
[Casi siempre No — es código puro]

## 6. Como valido que quedo bien
- [ ] El dato es correcto
- [ ] Se actualiza al recargar
```
