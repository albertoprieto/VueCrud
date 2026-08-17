# Histórico de Activaciones / Renovaciones

## Contexto

`Recientes.vue` (Instalaciones Recientes) y `RenovacionesRecientes.vue` (Renovaciones Recientes) muestran datos filtrados por mes (default: mes actual), con desglose por `status`: `con_reporte`, `sin_reporte`, `es_envio`, `no_requiere` (activaciones) y esos mismos más `desconocido`, `no_encontrado` (renovaciones). Los datos ya están persistidos en MySQL (tablas `activaciones_recientes` y `renovaciones_recientes`), consultables por mes vía `anio`/`mes` en los endpoints existentes `GET /activaciones-recientes` y `GET /renovaciones-recientes`.

No existe hoy ninguna vista que muestre tendencias entre varios meses. Este spec agrega una pantalla de histórico por cada módulo, con gráficas dinámicas (ECharts) y una tabla de números exactos por mes.

## Alcance

- Un botón "Histórico" nuevo junto al filtro de Mes (agregado en la tarea anterior) en `Recientes.vue` y en `RenovacionesRecientes.vue`.
- Dos componentes nuevos: `HistoricoActivaciones.vue` y `HistoricoRenovaciones.vue` (no un componente combinado — decisión explícita del usuario).
- Dos endpoints nuevos en `main.py` que agregan conteos por mes+status en SQL.
- Librería de gráficas: **ECharts** vía el wrapper oficial `vue-echarts` (decisión explícita del usuario, sobre Chart.js/ApexCharts).
- Selector de rango fijo: 3 / 6 / 12 / 24 meses, default 12 (no rango de fechas libre — decisión explícita).

Fuera de alcance: exportar el histórico a Excel/PDF, comparar activaciones vs renovaciones en una misma vista, drill-down a los registros individuales de un mes desde el histórico.

## Backend

### `GET /activaciones-recientes/historico`

Query param: `meses: int = Query(12, ge=1, le=36)`.

Calcula el primer mes del rango con aritmética simple de calendario (sin `dateutil`, no está instalado):

```python
def _restar_meses(anio, mes, n):
    total = (anio * 12 + (mes - 1)) - n
    return total // 12, total % 12 + 1
```

SQL:

```sql
SELECT
    YEAR(COALESCE(hora_activacion, fecha_carga)) AS anio,
    MONTH(COALESCE(hora_activacion, fecha_carga)) AS mes,
    status,
    COUNT(*) AS cantidad
FROM activaciones_recientes
WHERE COALESCE(hora_activacion, fecha_carga) >= %s
GROUP BY anio, mes, status
ORDER BY anio, mes
```

`%s` = primer día del mes más antiguo del rango (`datetime(anio_inicio, mes_inicio, 1)`).

En Python se construye la lista completa de meses del rango (incluyendo meses sin ningún registro, en 0), y para cada uno se agrega `total` como suma de todos los `status` presentes. Formato de respuesta:

```json
{
  "meses": [
    {
      "anio": 2025, "mes": 9, "label": "2025-09",
      "total": 42,
      "por_status": { "con_reporte": 30, "sin_reporte": 10, "es_envio": 1, "no_requiere": 1 }
    }
  ]
}
```

`por_status` solo trae las claves que efectivamente tengan datos en ese mes (el frontend rellena con 0 lo que falte); esto evita fijar en el backend cuáles status son válidos para cada tabla.

### `GET /renovaciones-recientes/historico`

Idéntico al anterior pero contra `renovaciones_recientes`, mismo cálculo de rango, mismos nombres de campos en la respuesta. `por_status` puede incluir además `desconocido` y `no_encontrado`.

## Frontend — servicios

`src/services/activacionesService.js`:
```js
export async function getHistoricoActivaciones(meses = 12) {
  const response = await axios.get(`${API_URL}/activaciones-recientes/historico`, { params: { meses } });
  return response.data;
}
```

`src/services/renovacionesService.js`: análogo, `getHistoricoRenovaciones(meses = 12)` contra `/renovaciones-recientes/historico`.

## Frontend — dependencias nuevas

```
npm install echarts vue-echarts
```

`vue-echarts` se registra localmente en cada componente histórico (import puntual del componente `VChart` + `use()` de ECharts con los módulos necesarios: `BarChart`, `LineChart`, `PieChart`, `GridComponent`, `TooltipComponent`, `LegendComponent`, `CanvasRenderer`), no globalmente en `main.js`, para no inflar el bundle de las pantallas que no usan gráficas.

## Frontend — componentes

`HistoricoActivaciones.vue` y `HistoricoRenovaciones.vue` comparten la misma estructura (código no compartido en un composable por ahora — son solo dos pantallas, YAGNI):

1. **Header**: título + Dropdown "Rango" (`Últimos 3 / 6 / 12 / 24 meses`, default 12). Cambiar el rango recarga el historico (`watch` sobre el ref, igual patrón que `mesFiltro` en las pantallas actuales).
2. **KPIs** (reusa clases `.info-card-mini` / `.mini-bar` ya existentes en `Recientes.vue` para consistencia visual):
   - Total del periodo (suma de `total` de todos los meses).
   - % con reporte (suma `con_reporte` / total del periodo).
   - % sin reporte (suma `sin_reporte` / total del periodo).
   - Promedio mensual (total del periodo / número de meses con datos).
3. **Gráfica combo** (ECharts `bar` apilado + `line`): eje X = `label` de cada mes; una serie de barras apiladas por cada `status` (colores: `con_reporte` #4caf50, `sin_reporte` #f44336, `es_envio` #2196f3, `no_requiere` #ff9800, y en renovaciones `desconocido` #9e9e9e, `no_encontrado` #9c27b0 — mismos colores que ya usan los badges/mini-bars actuales); una serie de línea con el `total` mensual superpuesta (eje Y secundario si la escala lo amerita). Tooltip compartido por eje (`trigger: 'axis'`) para comparar todos los status de un mes de un vistazo.
4. **Donut** (ECharts `pie`): % agregado por `status` sumando todos los meses del rango seleccionado, mismos colores que la gráfica combo.
5. **Tabla de números** (`DataTable` de PrimeVue, igual que las tablas existentes): una fila por mes, columnas = cada `status` + `Total`, para tener las cifras exactas a la vista además de las gráficas.

Estados: `loading` (spinner, igual patrón `processing` de las pantallas actuales), `error` (`Message` de PrimeVue), vacío (si todos los meses del rango están en 0, mensaje tipo "Sin datos en el rango seleccionado").

## Navegación

- `Recientes.vue`: botón `Histórico` (`icon="pi pi-chart-line"`, `p-button-outlined p-button-sm`) en el toolbar de Mes agregado en la tarea anterior, `@click="router.push('/historico-activaciones')"`.
- `RenovacionesRecientes.vue`: mismo botón, `@click="router.push('/historico-renovaciones')"`.
- `router/index.js`: dos rutas nuevas —
  - `{ path: '/historico-activaciones', name: 'historico-activaciones', component: HistoricoActivaciones }`
  - `{ path: '/historico-renovaciones', name: 'historico-renovaciones', component: HistoricoRenovaciones }`

## Testing

No hay suite de tests automatizados en este proyecto (verificación manual es el patrón existente). Verificación manual antes de dar por cerrada la tarea:
- Cargar cada pantalla histórico con datos reales del backend, cambiar el selector de rango (3/6/12/24) y confirmar que gráficas + tabla + KPIs se actualizan.
- Probar un rango sin ningún dato (ej. cuenta nueva) y confirmar el estado vacío.
- Confirmar que los botones "Histórico" navegan correctamente desde ambas pantallas de origen y que el botón "volver"/navegación del router funciona.
