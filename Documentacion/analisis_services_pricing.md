# Análisis: 05. Services_05.25.xlsm — Motor de Pricing CNTXT

> Generado: 2026-04-06  
> Fuente: `/Documentacion/05. Services_05.25.xlsm`

---

## Hojas del archivo (8 en total)

1. `Dolores o Deseos`
2. `V.sual DATA`
3. `Detalle1`
4. `Acciones por Servicio`
5. `D.sign DATA`
6. `Buscador de dolor`
7. `Listas`
8. `Servicios`

---

## Hoja: `Servicios` — Catálogo maestro

Índice de todos los productos/servicios que CNTXT ofrece al mercado. Un registro por servicio.

| Campo | Ejemplo |
|-------|---------|
| # secuencial | 1 … 81 |
| LÍNEA OPERATIVA | `V` (V.sual) · `D` (D.sign) |
| COD. CAT | `0`–`7` |
| CÓDIGO | `V0.1`, `D1.1`, etc. |
| CÓDIGOS 2024 (legacy) | `V01`, `D4` |
| CATEGORÍA | `V0. Modelación 3D`, `D1. Parcelaciones y Condominios`, etc. |
| FASE DE DESARROLLO | `Fase 1` · `Fase 2` · `Fase 3` · None |
| NOMBRE DE SERVICIO | Nombre comercial |
| DESCRIPCIÓN | Texto largo comercial/técnico |

**Totales:** ~22 servicios V.sual + ~60 servicios D.sign = **~82 servicios activos**

---

## Hoja: `V.sual DATA` — Costos detallados línea V.sual

148 filas × 32 columnas. Cada fila = una **acción** dentro de un servicio.

### Servicios V.sual (22 códigos)

| Categoría | Códigos | Descripción |
|-----------|---------|-------------|
| V0. Modelación 3D | V0.1–V0.5 | Modelos 3D arquitectónicos |
| V1. Imágenes | V1.1–V1.3 | Renders fotorrealistas |
| V2. Videos Emocionales | V2.1–V2.5 | Videos arquitectónicos |
| V3. Recorridos 360° | V3.1–V3.2 | Tours virtuales |
| V4. Planimetría Comercial | V4.1–V4.2 | Planos comerciales |
| V5. Experiencias WEB | V5.1–V5.5 | Plataformas y microsites |

### Columnas de datos

| Col | Campo | Tipo |
|-----|-------|------|
| B | CÓDIGO | `V0.1`–`V5.5` |
| C | CATEGORÍA | e.g. `V0. Modelación 3D` |
| D | SUB CATEGORÍA | `01. Urb`, `02. Ed. Exterior`, `03. Ed. Interior`, `04. Todos` |
| E | NOMBRE DE SERVICIO | Texto |
| F | ENTREGABLE | `MODELO 3D`, `MP4`, `LINK`, etc. |
| G | UND ENTREGABLE | `SKP RVT`, `MP4`, `PDF PNG JPG`, `LINK` |
| H | CANTIDAD | Numérico |
| I | ACTIVIDADES CLAVES | Nombre de fase/actividad |
| J | # ACCIONES | Secuencial numérico |
| K | ACCIONES CLAVES | Descripción detallada de la acción |
| L | RESPONSABLE | Rol: `VL`, `VM`, `VS`, `PC`, `Outsoursing` |
| M | TIEMPO (HORAS) | Float |
| N | HONORARIOS POR HORA ($COP) | Float |
| O | SUBTOTAL HONORARIOS | = M × N |
| P | HARDWARE ($ DEPRECIACIÓN) | Float |
| Q | SOFTWARE (LICENCIAS) | Float |
| R | CONSUMIBLES ($ INSUMOS) | Float |
| S | SUBCONTRATOS | Float |
| T | COSTO DIRECTO ($COP) | = O + P + Q + R + S |
| U | PRORRATEO GASTOS | Float ($27,789/h × horas) |
| V | COSTOS OPERACIONALES | = T + U |
| W | DESFASE (%) | Float — contingencia 15–20% |
| X | DESFASE ($COP) | = V × W |
| Y | UTILIDAD (%) | Float — margen 20–30% |
| Z | UTILIDAD ($COP) | calculado |
| AA | VALOR NETO ($COP) | = V + X + Z |
| AB | MÁRGEN DE NEGOCIACIÓN (%) | Float (~5%) |
| AC | NEGOCIACIÓN ($COP) | calculado |
| AD | ICA ($COP) | ~0.414% sobre valor neto |
| AE | 4×1000 ($COP) | 0.4% sobre valor neto |
| AF | VALOR TOTAL SERVICIO ($COP) | Precio final al cliente |

### Roles V.sual

| Código | Nombre | Honorario/mes | Honorario/hora |
|--------|--------|---------------|----------------|
| VM | Visual Manager | $4,500,000 | $22,796 |
| VL | Visual Leader | $3,500,000 | $17,730 |
| VS | Visual Support | $3,000,000 | $15,198 |
| PC | Elena | $0 | $10,000 |
| Outsoursing | Externo | — | variable |

---

## Hoja: `D.sign DATA` — Costos detallados línea D.sign

1,380 filas × 33 columnas. Misma estructura que V.sual DATA + columna **FASES** (Fase 1/2/3).

### Servicios D.sign (~60 códigos en 8 categorías)

| Categoría | Códigos | Descripción |
|-----------|---------|-------------|
| D0. Proyecto | D0.1–D0.5 | Diagnóstico, conceptualización, presentaciones, presupuesto, ficha maestra |
| D1. Parcelaciones y Condominios | D1.1–D1.26 | Urbanismo, edificación, complementarios (3 fases) |
| D2. Edificación en Altura | D2.1–D2.8 | Modelos, planimetría, especificaciones por fase |
| D3. Vivienda Campestre | D3.1–D3.11 | Vivienda, personal shopper de lote |
| D4. Comercial | D4.1–D4.3 | Stands, layouts comerciales |
| D6. Diseño Interior | D6.1–D6.7 | Interiores, look & feel, "Diseña Tu Interior", "Renueva Tu Interior" |
| D7. Select | D7.1–D7.2 | Categoría especial (proyecto piloto) |

**Categorías declaradas sin servicios activos aún:** D5 Industrial, D7 Espacio Público, D8 Hotelería, D10 Equipamientos.

### Roles D.sign

| Código | Nombre | Honorario/mes | Honorario/hora |
|--------|--------|---------------|----------------|
| DM | Design Manager | $4,500,000 | $22,796 |
| LA | Leader Architect | $4,000,000 | $20,263 |
| SUPP | Support Architect | $3,500,000 | $17,730 |
| JUN | Junior Architect | $2,300,000 | $11,651 |
| INT | Intern Architect | $2,000,000 | $10,132 |

---

## Hoja: `Listas` — Catálogos maestros

### Gastos operacionales (prorrateo fijo para TODOS los servicios)

| Tipo | Mensual | Por hora |
|------|---------|---------|
| Gastos Administrativos | $15,187,526 | $13,393 |
| Gastos Financieros | $12,995,741 | $11,460 |
| Gastos de Ventas | $3,330,000 | $2,937 |
| **TOTAL** | **$31,513,267** | **$27,789** |

### Categorías CNTXT (tabla de referencia)

| Código | Categoría |
|--------|-----------|
| 0 | Proyecto |
| 1 | Parcelaciones y Condominios |
| 2 | Edificación en Altura |
| 3 | Vivienda Campestre |
| 4 | Comercial |
| 5 | Industrial |
| 6 | Diseño Interior |
| 7 | Espacio Público |
| 8 | Hotelería |
| 9 | Equipamientos |

### Sub categorías

| Código | Nombre |
|--------|--------|
| 00 | N/A |
| 01 | Urb / Urbanismo |
| 02 | Ed. Exterior / Edificación |
| 03 | Ed. Interior / Complementario |
| 04 | Todos |

### Software (licencias por línea)

| Software | Valor anual |
|----------|-------------|
| SketchUp (SKP) | $1,400,000 |
| Lumion | $6,600,000 |
| V-Ray | $3,300,000 |
| Revit | $12,400,000 |
| Adobe Photoshop | $451,000 |
| **Costo/hora software** | **$3,411** |

---

## Hoja: `Dolores o Deseos` — Propuesta de valor

Marco de segmentación CRM. 17 registros de dolores de clientes.

| Campo | Tipo | Ejemplo |
|-------|------|---------|
| TIPO DE CLIENTE | B2B · B2C | `B2B` |
| NECESIDAD O DESEO | Necesidad · Deseo | `Necesidad` |
| DOLOR O DESEO TÉCNICO | Texto corto | nombre del dolor |
| FEDPICA | Texto largo | descripción emocional en primera persona |
| CONSECUENCIA | Texto libre | qué pasa si no se resuelve |
| INSIGHT DE SOLUCIÓN | Texto libre | argumento de venta |
| LÍNEA DE SOLUCIÓN | D.sign · V.sual · Sales | |
| PAQUETES DE SOLUCIÓN | Nombre del paquete | `Visualiza tu proyecto` |
| SERVICIOS DE SOLUCIÓN | Código paquete | `V1`, `V2`, ..., `V8` |

> FEDPICA = acrónimo de emociones (framework interno de CNTXT).

---

## Fórmula de cálculo de precio (cascada por acción)

```
1. SUBTOTAL HONORARIOS    = TIEMPO_HORAS × HONORARIOS_POR_HORA
2. COSTO_DIRECTO          = SUBTOTAL_HON + HARDWARE_DEP + SOFTWARE_LIC + CONSUMIBLES + SUBCONTRATOS
3. COSTOS_OPERACIONALES   = COSTO_DIRECTO + PRORRATEO_GASTOS  ($27,789/h × horas)
4. DESFASE_$              = COSTOS_OPERACIONALES × DESFASE_%   (contingencia 15–20%)
5. UTILIDAD_$             = (COSTOS_OP + DESFASE_$) × UTILIDAD_%  (margen 20–30%)
6. VALOR_NETO             = COSTOS_OP + DESFASE_$ + UTILIDAD_$
7. NEGOCIACIÓN_$          = VALOR_NETO × MARGEN_NEGOCIACIÓN_%  (~5% descuento máximo)
8. ICA                    = VALOR_NETO × ~0.414%               (ICA Bogotá servicios profesionales)
9. 4×1000                 = VALOR_NETO × 0.4%                  (GMF)
10. VALOR_TOTAL_SERVICIO  = VALOR_NETO + NEGOCIACIÓN + ICA + 4×1000
```

El **prorrateo de gastos ($27,789/h)** se aplica uniformemente a cada acción de todos los servicios de ambas líneas.

---

## Relaciones entre hojas

```
Listas ──────────→ V.sual DATA      (tarifas por rol, software, hardware)
Listas ──────────→ D.sign DATA      (ídem)
Listas ──────────→ Prorrateo        ($27,789/h aplicado en col. U de ambas DATA)
Servicios ───────→ V.sual DATA      (catálogo de códigos y nombres)
Servicios ───────→ D.sign DATA      (ídem)
D.sign DATA ─────→ Acciones por Servicio  (tabla dinámica filtrada por CÓDIGO)
D.sign DATA ─────→ Detalle1         (pivot auxiliar de horas por persona)
Dolores o Deseos → Servicios        (via códigos de paquete V1–V8)
```

---

## Modelos Django propuestos

### Catálogos (datos maestros)

```python
LineaOperativa          # V.sual, D.sign
  codigo: V, D
  nombre: str

CategoriaServicio       # V0. Modelación 3D, D1. Parcelaciones…
  codigo: str           # V0, D1, etc.
  codigo_numerico: int  # 0–10
  nombre: str
  linea_operativa: FK

SubCategoria            # 01. Urb, 02. Ed. Exterior…
  codigo: str
  nombre: str

Rol                     # VM, VL, DM, LA, SUPP, JUN, INT, PC
  codigo: str
  nombre_completo: str
  honorario_mensual: Decimal
  honorario_hora: Decimal
  linea_operativa: FK

Software                # SKP, Lumion, Revit…
  nombre: str
  valor_anual: Decimal
  valor_hora: Decimal

GastoOperacional        # Admin, Financiero, Ventas
  tipo: str
  valor_mensual: Decimal
  valor_hora: Decimal
```

### Servicios y acciones

```python
Servicio                # Catálogo de productos
  codigo: str           # V0.1, D1.1 (PK natural)
  codigo_legacy: str    # V01, D4 (2024)
  linea_operativa: FK
  categoria: FK
  fase: choices Fase1/Fase2/Fase3/NA
  nombre: str
  descripcion: TextField
  numero_secuencial: int

AccionServicio          # Tabla de costos detallada (fuente del precio)
  servicio: FK
  subcategoria: FK
  entregable: str
  unidad_entregable: str
  cantidad: int
  actividad_clave: str
  numero_accion: int
  descripcion_accion: TextField
  responsable: FK Rol
  tiempo_horas: Decimal
  honorarios_por_hora: Decimal
  hardware_depreciacion: Decimal
  software_licencias: Decimal
  consumibles: Decimal
  subcontratos: Decimal
  # calculados (pueden ser @property o guardados):
  costo_directo: Decimal
  prorrateo_gastos: Decimal
  costos_operacionales: Decimal
  desfase_pct: Decimal
  utilidad_pct: Decimal
  margen_negociacion_pct: Decimal
  valor_total_servicio: Decimal
```

### CRM / Propuesta de valor

```python
DolorCliente
  tipo_cliente: choices B2B/B2C
  tipo: choices Necesidad/Deseo
  dolor_tecnico: str
  descripcion_fedpica: TextField
  consecuencia: TextField
  insight_solucion: TextField
  linea_solucion: str
  paquete_solucion: str
  codigo_servicio_solucion: str  # V1–V8
```

---

## Hallazgos clave

1. **El archivo es la fuente de verdad del pricing** — cada servicio tiene un costo construido desde cero: horas × tarifa + overhead + margen. No hay precios fijos arbitrarios.
2. **D7. Select** = categoría del proyecto piloto (2026-04-08). Solo tiene D7.1 y D7.2, aún sin descripción completa.
3. **Capacidad mensual V.sual:** 11 personas, honorarios totales ~$11,000,000/mes.
4. **Capacidad mensual D.sign:** 10 personas, honorarios totales ~$16,300,000/mes.
5. **Rango de precios:** desde ~$260,000 COP (servicios complementarios simples) hasta ~$24,700,000 COP (D2.1 Edificación en Altura completo).
6. **Categorías sin implementar aún:** D5 Industrial, D7 Espacio Público, D8 Hotelería, D10 Equipamientos — están en los catálogos pero sin acciones de costo.
7. **V6.3 Identidad Visual y Storytelling** aparece en Servicios pero sin data de costos en V.sual DATA.
8. **Fases:** D.sign tiene 3 fases de madurez (conceptual → técnico → detalle constructivo). V.sual no maneja fases explícitas.
