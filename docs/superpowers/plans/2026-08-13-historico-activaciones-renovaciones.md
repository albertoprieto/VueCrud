# Histórico de Activaciones / Renovaciones Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a "Histórico" screen for both Instalaciones Recientes and Renovaciones Recientes, showing multi-month trends (stacked bar + line combo, donut, and an exact-numbers table) driven by two new backend aggregation endpoints.

**Architecture:** Two new `GET .../historico` endpoints in `main.py` aggregate counts by month+status directly in SQL. Two new Vue components (`HistoricoActivaciones.vue`, `HistoricoRenovaciones.vue`) call them and render with ECharts via `vue-echarts`. A "Histórico" button is added next to the existing Mes filter in `Recientes.vue` and `RenovacionesRecientes.vue`, and two routes are registered.

**Tech Stack:** FastAPI + mysql.connector (existing), Vue 3 `<script setup>`, PrimeVue 4, ECharts + vue-echarts (new dependency), vue-router 4.

## Global Constraints

- No automated test suite exists in this project (`package.json` has no test script; `main.py` has no pytest setup). Every "test" step in this plan is a manual/curl verification, not an automated test file.
- Never run `npm run build` or any deploy script — the user builds and deploys this project themselves.
- The backend connects to MySQL with hardcoded credentials matching every existing endpoint (`host="localhost", user="usuario_vue", password="tu_password_segura", database="nombre_de_tu_db"`) — copy this pattern exactly, don't refactor it.
- All UI text is in Spanish, matching the rest of the app.
- Use PrimeVue 4 components only for non-chart UI (`Dropdown`, `DataTable`, `Column`, `Message`), matching existing imports style (`import X from 'primevue/x'`).
- Status colors (must match existing badges/mini-bars in `Recientes.vue`): `con_reporte` `#4caf50`, `sin_reporte` `#f44336`, `es_envio` `#2196f3`, `no_requiere` `#ff9800`. New colors introduced by this plan: `pendiente` `#607d8b`, `desconocido` `#9e9e9e`, `no_encontrado` `#9c27b0`.

---

## Task 1: Backend — `GET /activaciones-recientes/historico`

**Files:**
- Modify: `main.py:5112-5114` (insert new endpoint + helper before the `# ENDPOINTS: RENOVACIONES RECIENTES` section comment)

**Interfaces:**
- Produces: `_restar_meses(anio: int, mes: int, n: int) -> tuple[int, int]` — module-level helper, reused by Task 2.
- Produces: `GET /activaciones-recientes/historico?meses=<int, 1-36, default 12>` → `{"meses": [{"anio": int, "mes": int, "label": "YYYY-MM", "total": int, "por_status": {status: int, ...}}, ...]}`, ordered oldest → newest, one entry per calendar month in range (zero-filled if no data).

- [ ] **Step 1: Locate the insertion point**

Read `main.py` around line 5106-5116. You're looking for the end of `get_activaciones_stats()` (ends with `return {"por_status": ..., "total": ...}`) followed by:

```python
# =====================================================
# ENDPOINTS: RENOVACIONES RECIENTES
# =====================================================
```

- [ ] **Step 2: Insert the helper function and the new endpoint**

Insert this immediately before the `# ENDPOINTS: RENOVACIONES RECIENTES` comment block:

```python
def _restar_meses(anio: int, mes: int, n: int) -> tuple[int, int]:
    """Resta n meses a un año/mes calendario, devolviendo (anio, mes) resultante."""
    total = (anio * 12 + (mes - 1)) - n
    return total // 12, total % 12 + 1


@app.get("/activaciones-recientes/historico")
def get_activaciones_historico(meses: int = Query(12, ge=1, le=36, description="Cantidad de meses hacia atrás a incluir")):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)

    hoy = datetime.now()
    anio_inicio, mes_inicio = _restar_meses(hoy.year, hoy.month, meses - 1)
    inicio = datetime(anio_inicio, mes_inicio, 1)

    cursor.execute("""
        SELECT
            YEAR(COALESCE(hora_activacion, fecha_carga)) AS anio,
            MONTH(COALESCE(hora_activacion, fecha_carga)) AS mes,
            status,
            COUNT(*) AS cantidad
        FROM activaciones_recientes
        WHERE COALESCE(hora_activacion, fecha_carga) >= %s
        GROUP BY anio, mes, status
        ORDER BY anio, mes
    """, (inicio,))
    filas = cursor.fetchall()
    cursor.close()
    db.close()

    buckets = {}
    anio_cursor, mes_cursor = anio_inicio, mes_inicio
    for _ in range(meses):
        clave = (anio_cursor, mes_cursor)
        buckets[clave] = {
            "anio": anio_cursor,
            "mes": mes_cursor,
            "label": f"{anio_cursor}-{mes_cursor:02d}",
            "total": 0,
            "por_status": {}
        }
        mes_cursor += 1
        if mes_cursor > 12:
            mes_cursor = 1
            anio_cursor += 1

    for fila in filas:
        clave = (fila["anio"], fila["mes"])
        if clave not in buckets:
            continue
        cantidad = fila["cantidad"]
        buckets[clave]["por_status"][fila["status"]] = cantidad
        buckets[clave]["total"] += cantidad

    return {"meses": list(buckets.values())}


```

- [ ] **Step 3: Verify the file has no syntax errors**

Run: `python -m py_compile main.py`
Expected: no output, exit code 0.

- [ ] **Step 4: Manual verification (after next deploy)**

This can't be run locally (DB is the production MySQL instance, and per project convention the user deploys, not the agent). Note for the user: once deployed, verify with:

```bash
curl "https://api.gpsubicacionapi.com/activaciones-recientes/historico?meses=3"
```

Expected: JSON with a `meses` array of exactly 3 objects, oldest first, each with `anio`, `mes`, `label`, `total`, `por_status`.

- [ ] **Step 5: Commit**

```bash
git add main.py
git commit -m "feat: add GET /activaciones-recientes/historico endpoint"
```

---

## Task 2: Backend — `GET /renovaciones-recientes/historico`

**Files:**
- Modify: `main.py:5616-5619` (insert new endpoint after `get_renovaciones_stats()`, before `@app.get("/operacion-imeis")`)

**Interfaces:**
- Consumes: `_restar_meses(anio, mes, n)` from Task 1 (same file, already defined above this point).
- Produces: `GET /renovaciones-recientes/historico?meses=<int, 1-36, default 12>` → same shape as Task 1's endpoint, but `por_status` can additionally contain `desconocido` and `no_encontrado`, and the source table is `renovaciones_recientes`.

- [ ] **Step 1: Locate the insertion point**

Read `main.py` around line 5608-5620. You're looking for the end of `get_renovaciones_stats()` (ends with `return {"por_status": ..., "por_periodo": ..., "ultimos_7_dias": ..., "total": ...}`) followed by two blank lines then `@app.get("/operacion-imeis")`.

- [ ] **Step 2: Insert the new endpoint**

Insert this immediately before `@app.get("/operacion-imeis")`:

```python
@app.get("/renovaciones-recientes/historico")
def get_renovaciones_historico(meses: int = Query(12, ge=1, le=36, description="Cantidad de meses hacia atrás a incluir")):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)

    hoy = datetime.now()
    anio_inicio, mes_inicio = _restar_meses(hoy.year, hoy.month, meses - 1)
    inicio = datetime(anio_inicio, mes_inicio, 1)

    cursor.execute("""
        SELECT
            YEAR(COALESCE(hora_activacion, fecha_carga)) AS anio,
            MONTH(COALESCE(hora_activacion, fecha_carga)) AS mes,
            status,
            COUNT(*) AS cantidad
        FROM renovaciones_recientes
        WHERE COALESCE(hora_activacion, fecha_carga) >= %s
        GROUP BY anio, mes, status
        ORDER BY anio, mes
    """, (inicio,))
    filas = cursor.fetchall()
    cursor.close()
    db.close()

    buckets = {}
    anio_cursor, mes_cursor = anio_inicio, mes_inicio
    for _ in range(meses):
        clave = (anio_cursor, mes_cursor)
        buckets[clave] = {
            "anio": anio_cursor,
            "mes": mes_cursor,
            "label": f"{anio_cursor}-{mes_cursor:02d}",
            "total": 0,
            "por_status": {}
        }
        mes_cursor += 1
        if mes_cursor > 12:
            mes_cursor = 1
            anio_cursor += 1

    for fila in filas:
        clave = (fila["anio"], fila["mes"])
        if clave not in buckets:
            continue
        cantidad = fila["cantidad"]
        buckets[clave]["por_status"][fila["status"]] = cantidad
        buckets[clave]["total"] += cantidad

    return {"meses": list(buckets.values())}


```

- [ ] **Step 3: Verify the file has no syntax errors**

Run: `python -m py_compile main.py`
Expected: no output, exit code 0.

- [ ] **Step 4: Manual verification (after next deploy)**

Note for the user: once deployed, verify with:

```bash
curl "https://api.gpsubicacionapi.com/renovaciones-recientes/historico?meses=3"
```

Expected: JSON with a `meses` array of exactly 3 objects, same shape as Task 1, `por_status` may include `desconocido`/`no_encontrado`.

- [ ] **Step 5: Commit**

```bash
git add main.py
git commit -m "feat: add GET /renovaciones-recientes/historico endpoint"
```

---

## Task 3: Frontend — service functions

**Files:**
- Modify: `src/services/activacionesService.js`
- Modify: `src/services/renovacionesService.js`

**Interfaces:**
- Consumes: the two endpoints from Task 1 and Task 2 (`GET /activaciones-recientes/historico`, `GET /renovaciones-recientes/historico`).
- Produces: `getHistoricoActivaciones(meses = 12): Promise<{meses: Array}>` exported from `@/services/activacionesService.js`.
- Produces: `getHistoricoRenovaciones(meses = 12): Promise<{meses: Array}>` exported from `@/services/renovacionesService.js`.
- Both are consumed by Task 4 and Task 5.

- [ ] **Step 1: Add `getHistoricoActivaciones` to `activacionesService.js`**

Insert after the closing brace of `getEstadisticasActivaciones` (currently ends at line 123, right before the `/**\n * Elimina activaciones antiguas` JSDoc block):

```js
/**
 * Obtiene el histórico agregado de activaciones por mes y status
 * @param {number} meses - Cantidad de meses hacia atrás a incluir (default 12)
 * @returns {Promise<{meses: Array}>}
 */
export async function getHistoricoActivaciones(meses = 12) {
  try {
    const response = await axios.get(`${API_URL}/activaciones-recientes/historico`, { params: { meses } });
    return response.data;
  } catch (error) {
    console.error("Error al obtener histórico de activaciones:", error);
    throw error;
  }
}

```

Then add `getHistoricoActivaciones,` to the `export default { ... }` object at the bottom of the file (after `getEstadisticasActivaciones,`).

- [ ] **Step 2: Add `getHistoricoRenovaciones` to `renovacionesService.js`**

Insert after the closing brace of `getEstadisticasRenovaciones` (currently ends at line 167, right before the `/**\n * Elimina renovaciones antiguas` JSDoc block):

```js
/**
 * Obtiene el histórico agregado de renovaciones por mes y status
 * @param {number} meses - Cantidad de meses hacia atrás a incluir (default 12)
 * @returns {Promise<{meses: Array}>}
 */
export async function getHistoricoRenovaciones(meses = 12) {
  try {
    const response = await axios.get(`${API_URL}/renovaciones-recientes/historico`, { params: { meses } });
    return response.data;
  } catch (error) {
    console.error("Error al obtener histórico de renovaciones:", error);
    throw error;
  }
}

```

Then add `getHistoricoRenovaciones,` to the `export default { ... }` object at the bottom of the file (after `getEstadisticasRenovaciones,`).

- [ ] **Step 3: Verify with a throwaway script**

Run (from project root, requires `VITE_API_URL` reachable — skip if it isn't, this is a syntax/import sanity check, not a network requirement):

```bash
node -e "require('@babel/core')" 2>/dev/null; node --input-type=module -e "import('./src/services/activacionesService.js').then(m => console.log(typeof m.getHistoricoActivaciones))"
```

Expected: `function` printed, no import errors. If this environment can't resolve the `@/` alias or `.js` ESM import standalone, it's fine — the real check is Task 4/5's dev-server verification.

- [ ] **Step 4: Commit**

```bash
git add src/services/activacionesService.js src/services/renovacionesService.js
git commit -m "feat: add historico service functions for activaciones and renovaciones"
```

---

## Task 4: Frontend — `HistoricoActivaciones.vue` + route + nav button

**Files:**
- Create: `src/modules/HistoricoActivaciones.vue`
- Modify: `src/router/index.js`
- Modify: `src/modules/Recientes.vue:184-189` (add "Histórico" button next to the Mes `Calendar`)
- Modify: `package.json` (new dependencies `echarts`, `vue-echarts`)

**Interfaces:**
- Consumes: `getHistoricoActivaciones` from Task 3 (`@/services/activacionesService.js`).
- Consumes: route `/historico-activaciones` (registered in this task).

- [ ] **Step 1: Install chart dependencies**

Run: `npm install echarts vue-echarts`
Expected: `package.json` `dependencies` gains `echarts` and `vue-echarts` entries; `npm install` exits 0.

- [ ] **Step 2: Create `src/modules/HistoricoActivaciones.vue`**

```vue
<template>
  <div class="historico-container">
    <h2 class="historico-title">Histórico de Instalaciones</h2>

    <div class="historico-toolbar">
      <span class="header-label">Rango</span>
      <Dropdown v-model="rango" :options="rangoOptions" optionLabel="label" optionValue="value" class="rango-input" />
    </div>

    <Message v-if="error" severity="error" :closable="true" @close="error = null">
      {{ error }}
    </Message>

    <div v-if="loading" class="loading-state">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Cargando histórico...</p>
    </div>

    <template v-else>
      <div v-if="totalPeriodo === 0" class="empty-state">
        <span class="pi pi-inbox empty-icon"></span>
        <p>Sin datos en el rango seleccionado</p>
      </div>

      <template v-else>
        <div class="kpi-row">
          <div class="kpi-card">
            <strong>{{ totalPeriodo }}</strong>
            <small>Total del periodo</small>
          </div>
          <div class="kpi-card">
            <strong>{{ pctConReporte }}%</strong>
            <small>Con reporte</small>
          </div>
          <div class="kpi-card">
            <strong>{{ pctSinReporte }}%</strong>
            <small>Sin reporte</small>
          </div>
          <div class="kpi-card">
            <strong>{{ promedioMensual }}</strong>
            <small>Promedio mensual</small>
          </div>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">Actividad por mes</h3>
          <v-chart class="chart" :option="chartComboOption" autoresize />
        </div>

        <div class="chart-card">
          <h3 class="chart-title">Distribución del periodo</h3>
          <v-chart class="chart chart-donut" :option="chartDonutOption" autoresize />
        </div>

        <DataTable :value="meses" class="historico-table" responsiveLayout="scroll">
          <Column field="label" header="Mes" />
          <Column v-for="s in STATUS_META" :key="s.key" :header="s.label">
            <template #body="slotProps">
              {{ slotProps.data.por_status[s.key] || 0 }}
            </template>
          </Column>
          <Column field="total" header="Total" />
        </DataTable>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Message from 'primevue/message';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart, PieChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { getHistoricoActivaciones } from '@/services/activacionesService';

use([CanvasRenderer, BarChart, LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent]);

const STATUS_META = [
  { key: 'con_reporte', label: 'Con reporte', color: '#4caf50' },
  { key: 'sin_reporte', label: 'Sin reporte', color: '#f44336' },
  { key: 'es_envio', label: 'Es envío', color: '#2196f3' },
  { key: 'no_requiere', label: 'No requiere', color: '#ff9800' },
  { key: 'pendiente', label: 'Pendiente', color: '#607d8b' }
];

const rangoOptions = [
  { label: 'Últimos 3 meses', value: 3 },
  { label: 'Últimos 6 meses', value: 6 },
  { label: 'Últimos 12 meses', value: 12 },
  { label: 'Últimos 24 meses', value: 24 }
];

const rango = ref(12);
const loading = ref(false);
const error = ref(null);
const meses = ref([]);

async function cargarHistorico() {
  loading.value = true;
  error.value = null;
  try {
    const resp = await getHistoricoActivaciones(rango.value);
    meses.value = resp.meses || [];
  } catch (e) {
    console.error('Error cargando histórico de activaciones:', e);
    error.value = 'No se pudo cargar el histórico. Intenta nuevamente.';
  } finally {
    loading.value = false;
  }
}

onMounted(cargarHistorico);
watch(rango, cargarHistorico);

const totalPeriodo = computed(() => meses.value.reduce((sum, m) => sum + (m.total || 0), 0));

const statusTotales = computed(() => {
  const totales = {};
  for (const s of STATUS_META) {
    totales[s.key] = meses.value.reduce((sum, m) => sum + (m.por_status[s.key] || 0), 0);
  }
  return totales;
});

const pctConReporte = computed(() => {
  if (!totalPeriodo.value) return '0.0';
  return ((statusTotales.value.con_reporte / totalPeriodo.value) * 100).toFixed(1);
});

const pctSinReporte = computed(() => {
  if (!totalPeriodo.value) return '0.0';
  return ((statusTotales.value.sin_reporte / totalPeriodo.value) * 100).toFixed(1);
});

const promedioMensual = computed(() => {
  const mesesConDatos = meses.value.filter(m => m.total > 0).length;
  if (!mesesConDatos) return '0.0';
  return (totalPeriodo.value / mesesConDatos).toFixed(1);
});

const chartComboOption = computed(() => {
  const labels = meses.value.map(m => m.label);
  const series = STATUS_META.map(s => ({
    name: s.label,
    type: 'bar',
    stack: 'total',
    itemStyle: { color: s.color },
    data: meses.value.map(m => m.por_status[s.key] || 0)
  }));
  series.push({
    name: 'Total',
    type: 'line',
    smooth: true,
    itemStyle: { color: '#212121' },
    lineStyle: { width: 3 },
    data: meses.value.map(m => m.total || 0)
  });
  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, type: 'scroll' },
    grid: { left: 40, right: 20, top: 30, bottom: 60, containLabel: true },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    series
  };
});

const chartDonutOption = computed(() => {
  const data = STATUS_META
    .map(s => ({ name: s.label, value: statusTotales.value[s.key] || 0, itemStyle: { color: s.color } }))
    .filter(d => d.value > 0);
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, type: 'scroll' },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      avoidLabelOverlap: true,
      data
    }]
  };
});
</script>

<style scoped>
@import '@/assets/main.css';

.historico-container {
  padding: 1.5rem;
  margin: 0 auto;
}

.historico-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-title);
  margin-bottom: 1.5rem;
}

.historico-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.header-label {
  font-weight: 500;
  color: var(--color-text);
}

.rango-input {
  width: 220px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text);
}

.empty-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.75rem;
  opacity: 0.6;
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.kpi-card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
}

.kpi-card strong {
  display: block;
  font-size: 1.6rem;
  color: var(--color-title);
}

.kpi-card small {
  color: var(--color-text);
  opacity: 0.8;
}

.chart-card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.chart-title {
  margin: 0 0 0.5rem;
  color: var(--color-title);
  font-size: 1.1rem;
}

.chart {
  height: 380px;
}

.chart-donut {
  height: 320px;
}

.historico-table {
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .historico-container {
    padding: 1rem;
  }
  .kpi-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
```

- [ ] **Step 3: Register the route**

In `src/router/index.js`, add the import after `import RenovacionesRecientes from '@/modules/RenovacionesRecientes.vue';` (line 36):

```js
import HistoricoActivaciones from '@/modules/HistoricoActivaciones.vue';
```

Then add the route after the `renovaciones-recientes` route entry (line 87):

```js
  ,{ path: '/historico-activaciones', name: 'historico-activaciones', component: HistoricoActivaciones }
```

- [ ] **Step 4: Add the "Histórico" button in `Recientes.vue`**

In `src/modules/Recientes.vue`, find (this is the toolbar added in the previous task, currently at lines 184-189):

```html
    <div class="table-header">
      <div class="header-left">
        <span class="header-label">Mes</span>
        <Calendar v-model="mesFiltro" view="month" dateFormat="mm/yy" showIcon iconDisplay="input" class="mes-input" />
      </div>
```

Replace with:

```html
    <div class="table-header">
      <div class="header-left">
        <span class="header-label">Mes</span>
        <Calendar v-model="mesFiltro" view="month" dateFormat="mm/yy" showIcon iconDisplay="input" class="mes-input" />
        <Button
          icon="pi pi-chart-line"
          label="Histórico"
          class="p-button-outlined p-button-sm"
          @click="router.push('/historico-activaciones')"
        />
      </div>
```

`router` is already available in this file (`const router = useRouter();` at line 371) — no new import needed.

- [ ] **Step 5: Manual verification in the browser**

Run: `npm run dev`

- Open the app, navigate to Instalaciones Recientes (`/recientes`).
- Confirm the new "Histórico" button appears right after the Mes calendar.
- Click it, confirm it navigates to `/historico-activaciones`.
- Confirm the Rango dropdown defaults to "Últimos 12 meses", KPIs/charts/table render (or the empty-state shows if there's genuinely no data), and switching the Rango dropdown reloads the charts and table.
- Stop the dev server when done (it does not need to stay running).

- [ ] **Step 6: Commit**

```bash
git add package.json package-lock.json src/modules/HistoricoActivaciones.vue src/router/index.js src/modules/Recientes.vue
git commit -m "feat: add historico view for instalaciones recientes"
```

---

## Task 5: Frontend — `HistoricoRenovaciones.vue` + route + nav button

**Files:**
- Create: `src/modules/HistoricoRenovaciones.vue`
- Modify: `src/router/index.js`
- Modify: `src/modules/RenovacionesRecientes.vue:209-214` (add "Histórico" button next to the Mes `Calendar`)

**Interfaces:**
- Consumes: `getHistoricoRenovaciones` from Task 3 (`@/services/renovacionesService.js`).
- Consumes: route `/historico-renovaciones` (registered in this task).
- Reuses `echarts`/`vue-echarts` installed in Task 4 — no new `npm install` needed here.

- [ ] **Step 1: Create `src/modules/HistoricoRenovaciones.vue`**

Same structure as `HistoricoActivaciones.vue` from Task 4, with these differences: title, `STATUS_META` includes `desconocido` and `no_encontrado`, and the import/call target the renovaciones service.

```vue
<template>
  <div class="historico-container">
    <h2 class="historico-title">Histórico de Renovaciones</h2>

    <div class="historico-toolbar">
      <span class="header-label">Rango</span>
      <Dropdown v-model="rango" :options="rangoOptions" optionLabel="label" optionValue="value" class="rango-input" />
    </div>

    <Message v-if="error" severity="error" :closable="true" @close="error = null">
      {{ error }}
    </Message>

    <div v-if="loading" class="loading-state">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Cargando histórico...</p>
    </div>

    <template v-else>
      <div v-if="totalPeriodo === 0" class="empty-state">
        <span class="pi pi-inbox empty-icon"></span>
        <p>Sin datos en el rango seleccionado</p>
      </div>

      <template v-else>
        <div class="kpi-row">
          <div class="kpi-card">
            <strong>{{ totalPeriodo }}</strong>
            <small>Total del periodo</small>
          </div>
          <div class="kpi-card">
            <strong>{{ pctConReporte }}%</strong>
            <small>Con reporte</small>
          </div>
          <div class="kpi-card">
            <strong>{{ pctSinReporte }}%</strong>
            <small>Sin reporte</small>
          </div>
          <div class="kpi-card">
            <strong>{{ promedioMensual }}</strong>
            <small>Promedio mensual</small>
          </div>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">Actividad por mes</h3>
          <v-chart class="chart" :option="chartComboOption" autoresize />
        </div>

        <div class="chart-card">
          <h3 class="chart-title">Distribución del periodo</h3>
          <v-chart class="chart chart-donut" :option="chartDonutOption" autoresize />
        </div>

        <DataTable :value="meses" class="historico-table" responsiveLayout="scroll">
          <Column field="label" header="Mes" />
          <Column v-for="s in STATUS_META" :key="s.key" :header="s.label">
            <template #body="slotProps">
              {{ slotProps.data.por_status[s.key] || 0 }}
            </template>
          </Column>
          <Column field="total" header="Total" />
        </DataTable>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Message from 'primevue/message';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart, PieChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { getHistoricoRenovaciones } from '@/services/renovacionesService';

use([CanvasRenderer, BarChart, LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent]);

const STATUS_META = [
  { key: 'con_reporte', label: 'Con reporte', color: '#4caf50' },
  { key: 'sin_reporte', label: 'Sin reporte', color: '#f44336' },
  { key: 'es_envio', label: 'Es envío', color: '#2196f3' },
  { key: 'no_requiere', label: 'No requiere', color: '#ff9800' },
  { key: 'pendiente', label: 'Pendiente', color: '#607d8b' },
  { key: 'desconocido', label: 'Desconocido', color: '#9e9e9e' },
  { key: 'no_encontrado', label: 'No encontrado', color: '#9c27b0' }
];

const rangoOptions = [
  { label: 'Últimos 3 meses', value: 3 },
  { label: 'Últimos 6 meses', value: 6 },
  { label: 'Últimos 12 meses', value: 12 },
  { label: 'Últimos 24 meses', value: 24 }
];

const rango = ref(12);
const loading = ref(false);
const error = ref(null);
const meses = ref([]);

async function cargarHistorico() {
  loading.value = true;
  error.value = null;
  try {
    const resp = await getHistoricoRenovaciones(rango.value);
    meses.value = resp.meses || [];
  } catch (e) {
    console.error('Error cargando histórico de renovaciones:', e);
    error.value = 'No se pudo cargar el histórico. Intenta nuevamente.';
  } finally {
    loading.value = false;
  }
}

onMounted(cargarHistorico);
watch(rango, cargarHistorico);

const totalPeriodo = computed(() => meses.value.reduce((sum, m) => sum + (m.total || 0), 0));

const statusTotales = computed(() => {
  const totales = {};
  for (const s of STATUS_META) {
    totales[s.key] = meses.value.reduce((sum, m) => sum + (m.por_status[s.key] || 0), 0);
  }
  return totales;
});

const pctConReporte = computed(() => {
  if (!totalPeriodo.value) return '0.0';
  return ((statusTotales.value.con_reporte / totalPeriodo.value) * 100).toFixed(1);
});

const pctSinReporte = computed(() => {
  if (!totalPeriodo.value) return '0.0';
  return ((statusTotales.value.sin_reporte / totalPeriodo.value) * 100).toFixed(1);
});

const promedioMensual = computed(() => {
  const mesesConDatos = meses.value.filter(m => m.total > 0).length;
  if (!mesesConDatos) return '0.0';
  return (totalPeriodo.value / mesesConDatos).toFixed(1);
});

const chartComboOption = computed(() => {
  const labels = meses.value.map(m => m.label);
  const series = STATUS_META.map(s => ({
    name: s.label,
    type: 'bar',
    stack: 'total',
    itemStyle: { color: s.color },
    data: meses.value.map(m => m.por_status[s.key] || 0)
  }));
  series.push({
    name: 'Total',
    type: 'line',
    smooth: true,
    itemStyle: { color: '#212121' },
    lineStyle: { width: 3 },
    data: meses.value.map(m => m.total || 0)
  });
  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, type: 'scroll' },
    grid: { left: 40, right: 20, top: 30, bottom: 60, containLabel: true },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    series
  };
});

const chartDonutOption = computed(() => {
  const data = STATUS_META
    .map(s => ({ name: s.label, value: statusTotales.value[s.key] || 0, itemStyle: { color: s.color } }))
    .filter(d => d.value > 0);
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, type: 'scroll' },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      avoidLabelOverlap: true,
      data
    }]
  };
});
</script>

<style scoped>
@import '@/assets/main.css';

.historico-container {
  padding: 1.5rem;
  margin: 0 auto;
}

.historico-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-title);
  margin-bottom: 1.5rem;
}

.historico-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.header-label {
  font-weight: 500;
  color: var(--color-text);
}

.rango-input {
  width: 220px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text);
}

.empty-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.75rem;
  opacity: 0.6;
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.kpi-card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
}

.kpi-card strong {
  display: block;
  font-size: 1.6rem;
  color: var(--color-title);
}

.kpi-card small {
  color: var(--color-text);
  opacity: 0.8;
}

.chart-card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.chart-title {
  margin: 0 0 0.5rem;
  color: var(--color-title);
  font-size: 1.1rem;
}

.chart {
  height: 380px;
}

.chart-donut {
  height: 320px;
}

.historico-table {
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .historico-container {
    padding: 1rem;
  }
  .kpi-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
```

- [ ] **Step 2: Register the route**

In `src/router/index.js`, add the import after the `HistoricoActivaciones` import added in Task 4:

```js
import HistoricoRenovaciones from '@/modules/HistoricoRenovaciones.vue';
```

Then add the route after the `historico-activaciones` route entry added in Task 4:

```js
  ,{ path: '/historico-renovaciones', name: 'historico-renovaciones', component: HistoricoRenovaciones }
```

- [ ] **Step 3: Add the "Histórico" button in `RenovacionesRecientes.vue`**

In `src/modules/RenovacionesRecientes.vue`, find (this is the toolbar added in the previous task, currently at lines 209-214):

```html
    <div class="table-header">
      <div class="header-left">
        <span class="header-label">Mes</span>
        <Calendar v-model="mesFiltro" view="month" dateFormat="mm/yy" showIcon iconDisplay="input" class="mes-input" />
      </div>
```

Replace with:

```html
    <div class="table-header">
      <div class="header-left">
        <span class="header-label">Mes</span>
        <Calendar v-model="mesFiltro" view="month" dateFormat="mm/yy" showIcon iconDisplay="input" class="mes-input" />
        <Button
          icon="pi pi-chart-line"
          label="Histórico"
          class="p-button-outlined p-button-sm"
          @click="router.push('/historico-renovaciones')"
        />
      </div>
```

`router` is already available in this file (`const router = useRouter();` at line 503) — no new import needed.

- [ ] **Step 4: Manual verification in the browser**

Run: `npm run dev`

- Open the app, navigate to Renovaciones Recientes (`/renovaciones-recientes`).
- Confirm the new "Histórico" button appears right after the Mes calendar.
- Click it, confirm it navigates to `/historico-renovaciones`.
- Confirm the Rango dropdown defaults to "Últimos 12 meses", KPIs/charts/table render (including the `desconocido`/`no_encontrado` columns in the table if that data exists), and switching the Rango dropdown reloads the charts and table.
- Stop the dev server when done.

- [ ] **Step 5: Commit**

```bash
git add src/modules/HistoricoRenovaciones.vue src/router/index.js src/modules/RenovacionesRecientes.vue
git commit -m "feat: add historico view for renovaciones recientes"
```
