<template>
  <div class="detalle-pago-container">
    <Button icon="pi pi-arrow-left" label="Volver a Pagos" class="p-button-text mb-3" @click="router.push('/pagos')" />

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <div v-else-if="item">
      <div style="display:flex; justify-content:space-between; align-items:center; gap:0.75rem;">
        <h2 class="detalle-title" style="margin-bottom:0;">
          Nota #{{ item.id }}
        </h2>
        <div style="display:flex; gap:0.75rem; align-items:center; flex-wrap:wrap;">
          <Button
            v-if="item.reporte_ids && item.reporte_ids.length"
            icon="pi pi-list"
            :label="`Ver Reportes de Servicio (${item.reporte_ids.length})`"
            class="p-button-outlined p-button-info"
            :loading="loadingReportes"
            @click="abrirReportesDialog"
          />
          <Button
            v-if="esEditable"
            icon="pi pi-plus"
            label="Agregar Servicios"
            class="p-button-outlined p-button-success"
            @click="abrirAgregarDialog"
          />
        </div>
      </div>

      <div class="detalle-card">
        <div class="detalle-row"><strong>Órdenes:</strong> {{ (item.ordenes || []).join(', ') }}</div>
        <div class="detalle-row"><strong>Cliente:</strong> {{ item.cliente || '-' }}</div>
        <div class="detalle-row"><strong>Total:</strong> {{ item.total != null ? '$' + Number(item.total).toFixed(2) : '-' }}</div>
        <div class="detalle-row"><strong>Fecha:</strong> {{ formatFecha(item.fecha) }}</div>
        <div class="detalle-row"><strong>Lugar de pago:</strong> {{ item.lugar_pago || '-' }}</div>
        <div class="detalle-row">
          <strong>Estatus actual:</strong>
          <span :class="'badge badge-' + badgeClass(item.status)" style="margin-left:0.5rem;">{{ item.status }}</span>
        </div>
      </div>

      <!-- Cambiar estatus y lugar de pago -->
      <div class="cambiar-status">
        <h3>Cambiar estatus y lugar de pago</h3>
        <div class="status-options">
          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Estatus:</label>
            <Dropdown
              v-model="nuevoStatus"
              :options="opcionesStatus"
              optionLabel="label"
              optionValue="value"
              placeholder="Seleccionar estatus"
              class="w-full"
            />
          </div>
          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Lugar de pago:</label>
            <Dropdown
              v-model="nuevoLugarPago"
              :options="lugaresDisponibles"
              placeholder="Seleccionar lugar de pago"
              class="w-full"
            />
          </div>
          <Button
            label="Guardar"
            icon="pi pi-save"
            :disabled="(!nuevoStatus || nuevoStatus === item.status) && (!nuevoLugarPago || nuevoLugarPago === item.lugar_pago)"
            @click="cambiarStatusYLugar"
            :loading="saving"
            style="align-self: flex-end;"
          />
        </div>
      </div>

      <!-- Comprobantes de pago -->
      <!-- <div class="comprobante-section">
        <h3>Comprobantes de pago</h3>
        <div v-if="item.comprobantes && item.comprobantes.length" class="comprobantes-lista">
          <div v-for="(comp, idx) in item.comprobantes" :key="idx">
            <div class="comprobante-item">
              <i class="pi pi-file" style="color:#1976d2;margin-right:0.5rem;"></i>
              <a :href="urlComprobante(comp)" target="_blank" rel="noopener noreferrer" style="color:#1976d2;font-weight:bold;flex:1;">
                {{ nombreArchivo(comp) }}
              </a>
              <Button
                icon="pi pi-wallet"
                label="Asignar a banco"
                class="p-button-outlined p-button-info p-button-sm"
                @click="toggleAsignar(comp)"
              />
              <Button
                icon="pi pi-trash"
                class="p-button-text p-button-danger p-button-sm"
                :loading="eliminandoComprobante === comp"
                @click="eliminarComprobante(comp)"
                v-tooltip.top="'Eliminar comprobante'"
              />
            </div>
            <div v-if="asignando === comp" style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:flex-end;padding:0.5rem 0 0.75rem 1.8rem;">
              <div>
                <label style="font-weight:bold;display:block;font-size:0.8rem;">Banco</label>
                <Dropdown v-model="formAsignar.banco" :options="lugaresDisponibles" placeholder="Selecciona banco" style="min-width:200px;" />
              </div>
              <div>
                <label style="font-weight:bold;display:block;font-size:0.8rem;">Monto</label>
                <input type="number" v-model.number="formAsignar.monto" min="0" step="0.01" style="padding:0.4rem;" />
              </div>
              <Button
                label="Confirmar" icon="pi pi-check" class="p-button-sm p-button-success"
                :disabled="!formAsignar.banco || !formAsignar.monto"
                :loading="asignandoGuardando"
                @click="confirmarAsignarComprobante(comp)"
              />
              <Button label="Cancelar" class="p-button-sm p-button-secondary" @click="asignando = null" />
            </div>
          </div>
        </div>
        <div v-else style="color:#999;margin-bottom:0.75rem;">No se han cargado comprobantes aún.</div>
        <div class="comprobante-upload">
          <label for="inputComprobante" style="font-weight:bold;display:block;margin-bottom:0.5rem;">Agregar comprobante:</label>
          <input id="inputComprobante" type="file" @change="onFileChange" accept="application/pdf,image/*" />
          <Button
            label="Subir comprobante"
            icon="pi pi-upload"
            class="p-button-success mt-2"
            :disabled="!archivoSeleccionado"
            :loading="subiendo"
            @click="subirComprobante"
          />
        </div>
      </div> -->

      <!-- Pagos adicionales a otro banco (ej. nota se paga en dos partes a bancos distintos) -->
     <!--  <div class="comprobante-section">
        <h3>Pagos adicionales a otro banco</h3>
        <div v-if="pagosAdicionales.length" class="comprobantes-lista">
          <div v-for="pago in pagosAdicionales" :key="pago.id" class="comprobante-item">
            <i class="pi pi-wallet" style="color:#1976d2;margin-right:0.5rem;"></i>
            <span style="flex:1;">
              <strong>{{ pago.banco }}</strong> — ${{ Number(pago.monto).toFixed(2) }}
              <a v-if="pago.comprobante_url" :href="pago.comprobante_url" target="_blank" rel="noopener noreferrer" style="margin-left:0.5rem;color:#1976d2;">ver comprobante</a>
            </span>
            <Button
              icon="pi pi-trash"
              class="p-button-text p-button-danger p-button-sm"
              :loading="eliminandoPago === pago.id"
              @click="eliminarPagoAdicional(pago)"
              v-tooltip.top="'Eliminar pago'"
            />
          </div>
        </div>
        <div v-else style="color:#999;margin-bottom:0.75rem;">Sin pagos adicionales registrados.</div>
        <div class="comprobante-upload" style="display:flex;gap:0.75rem;flex-wrap:wrap;align-items:flex-end;">
          <div>
            <label style="font-weight:bold;display:block;margin-bottom:0.5rem;">Banco</label>
            <Dropdown v-model="nuevoPago.banco" :options="lugaresDisponibles" placeholder="Selecciona banco" style="min-width:200px;" />
          </div>
          <div>
            <label style="font-weight:bold;display:block;margin-bottom:0.5rem;">Monto</label>
            <input type="number" v-model.number="nuevoPago.monto" min="0" step="0.01" style="padding:0.4rem;" />
          </div>
          <div>
            <label style="font-weight:bold;display:block;margin-bottom:0.5rem;">Comprobante (opcional)</label>
            <input type="file" @change="onFilePagoChange" accept="application/pdf,image/*" />
          </div>
          <Button
            label="Registrar pago"
            icon="pi pi-plus"
            class="p-button-success"
            :disabled="!nuevoPago.banco || !nuevoPago.monto"
            :loading="registrandoPago"
            @click="registrarPagoAdicional"
          />
        </div>
      </div>
 -->
      <!-- Ingresos bancarios ligados (comprobante primero, ver DetalleBanco.vue
           "Agregar ingreso") — alternativa a "Pagos adicionales" de arriba:
           el comprobante se sube desde Bancos ANTES de saber a qué nota
           corresponde, y aquí se liga. Si el monto no cubre exacto el saldo
           pendiente, el backend exige justificación (ver conciliación en
           main.py, TOLERANCIA_CONCILIACION_PAGOS). -->
      <div class="comprobante-section">
        <h3>Ingresos bancarios ligados</h3>
        <div v-if="ingresosLigados.length" class="comprobantes-lista">
          <div v-for="link in ingresosLigados" :key="link.id" class="ingreso-ligado">
            <div class="comprobante-item">
              <i class="pi pi-wallet" style="color:#1976d2;margin-right:0.5rem;"></i>
              <span style="flex:1;">
                <strong>{{ link.banco }}</strong> — ${{ Number(link.monto_aplicado).toFixed(2) }}
                <span v-if="link.requiere_justificacion" class="pi pi-exclamation-triangle" style="color:#b26a00;margin-left:0.4rem;" />
                <a v-if="link.comprobante_url" :href="link.comprobante_url" target="_blank" rel="noopener noreferrer" style="margin-left:0.5rem;color:#1976d2;">ver comprobante</a>
              </span>
              <Button
                icon="pi pi-times"
                label="Desligar"
                class="p-button-text p-button-warning p-button-sm"
                :loading="desligandoIngresoId === link.id"
                @click="desligarIngreso(link)"
              />
            </div>
            <!-- Detalle e historia del pago ligado -->
            <div class="ingreso-ligado-detalle">
              <div><strong>Monto del ingreso:</strong> {{ link.ingreso_monto != null ? '$' + Number(link.ingreso_monto).toFixed(2) : '-' }} · aplicado a esta nota: ${{ Number(link.monto_aplicado).toFixed(2) }}</div>
              <div v-if="Math.abs(Number(link.diferencia)) > 0.01">
                <strong>Diferencia:</strong>
                <span :style="{ color: Number(link.diferencia) > 0 ? '#b26a00' : '#1976d2' }">
                  {{ Number(link.diferencia) > 0 ? 'sobró ' : 'faltó ' }}${{ Math.abs(Number(link.diferencia)).toFixed(2) }}
                </span>
              </div>
              <div v-if="link.conceptos && link.conceptos.length">
                <strong>Conceptos:</strong>
                <ul style="margin:0.2rem 0 0.2rem 1.1rem;padding:0;">
                  <li v-for="(c, i) in link.conceptos" :key="i">{{ c.concepto }} — ${{ Number(c.monto).toFixed(2) }}</li>
                </ul>
              </div>
              <div><strong>Fecha de transacción:</strong> {{ formatFecha(link.fecha_transaccion) || '-' }}</div>
              <div v-if="link.imeis && link.imeis.length"><strong>IMEI(s):</strong> {{ link.imeis.join(', ') }}</div>
              <div v-if="link.referencia_comprobante"><strong>Referencia:</strong> {{ link.referencia_comprobante }}</div>
              <div v-if="link.clave_rastreo"><strong>Clave de rastreo:</strong> {{ link.clave_rastreo }}</div>
              <div v-if="link.cuenta_origen"><strong>Cuenta origen:</strong> {{ link.cuenta_origen }}</div>
              <div v-if="link.usuario"><strong>Usuario del ingreso:</strong> {{ link.usuario }}</div>
              <div><strong>Ligado por:</strong> {{ link.creado_por || '-' }}<span v-if="link.creado_fecha"> · {{ formatFechaHora(link.creado_fecha) }}</span></div>
            </div>
          </div>
        </div>
        <div v-else style="color:#999;margin-bottom:0.75rem;">Sin ingresos bancarios ligados.</div>
        <Button label="Ligar ingreso bancario" icon="pi pi-link" class="p-button-outlined p-button-info" @click="abrirLigarIngreso" />
      </div>

      <!-- Datos de pago y fiscales (para el PDF) -->
      <div class="datos-pago-section">
        <h3>Datos de pago y fiscales</h3>
        <div v-if="clienteFiscal" class="cliente-fiscal-info">
          <div><strong>RFC:</strong> {{ clienteFiscal.rfc || '-' }}</div>
          <div><strong>Domicilio:</strong> {{ [clienteFiscal.calle_numero, clienteFiscal.colonia, clienteFiscal.codigo_postal].filter(Boolean).join(', ') || '-' }}</div>
          <div><strong>Régimen fiscal:</strong> {{ clienteFiscal.regimen_fiscal || '-' }}</div>
          <small style="color:var(--color-text-muted,#888);">Estos datos se editan en Clientes.</small>
        </div>
        <div v-else style="color:#999;margin-bottom:0.5rem;">
          No se encontró un cliente registrado con este nombre — sin datos fiscales para el PDF.
        </div>
        <div class="datos-pago-form">
          <div class="datos-pago-field">
            <label>Método de pago</label>
            <Dropdown
              v-model="datosPagoForm.metodo_pago"
              :options="[{ label: 'PUE - Pago en una sola exhibición', value: 'PUE' }, { label: 'PPD - Pago en parcialidades o diferido', value: 'PPD' }]"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecciona método de pago"
              class="w-full"
            />
          </div>
          <div class="datos-pago-field">
            <label>Forma de pago</label>
            <Dropdown
              v-model="datosPagoForm.forma_pago"
              :options="formasPago"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecciona forma de pago"
              class="w-full"
            />
          </div>
        </div>
        <label style="display:block;margin-top:0.75rem;font-weight:600;">Notas / términos y condiciones</label>
        <Textarea
          v-model="datosPagoForm.notas_extra"
          rows="3"
          placeholder="Ej: Los equipos GPS tienen un año de garantía..."
          class="w-full"
          style="width:100%;resize:vertical;"
        />
        <Button
          label="Guardar datos de pago"
          icon="pi pi-save"
          class="p-button-secondary mt-2"
          :loading="guardandoDatosPago"
          @click="guardarDatosPago"
        />
      </div>

      <!-- Observaciones -->
      <div class="observaciones-section">
        <h3>Observaciones</h3>
        <Textarea
          v-model="observacionesTexto"
          rows="4"
          placeholder="Escribe observaciones sobre esta nota..."
          class="w-full"
          style="width:100%;resize:vertical;"
        />
        <Button
          label="Guardar observaciones"
          icon="pi pi-save"
          class="p-button-secondary mt-2"
          :loading="guardandoObs"
          :disabled="observacionesTexto === (item.observaciones || '')"
          @click="guardarObservaciones"
        />
      </div>

      <!-- Detalle de órdenes incluidas -->
      <div v-if="item.detalle_ordenes && item.detalle_ordenes.length" class="ordenes-detalle">
        <h3>Órdenes incluidas</h3>
        <DataTable :value="detalleOrdenesEnriquecido" responsiveLayout="scroll">
          <Column field="folio" header="Orden" />
          <Column field="tipo_servicio" header="Tipo" />
          <Column field="nombre_cliente" header="Cliente" />
          <Column header="IMEI(s)">
            <template #body="{ data }">
              {{ formatearImeisOrden(data) }}
            </template>
          </Column>
          <Column field="total" header="Total">
            <template #body="{ data }">
              {{ data.total != null ? '$' + Number(data.total).toFixed(2) : '-' }}
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <div v-else style="text-align:center;padding:3rem;">
      <p>No se encontró el registro.</p>
    </div>

    <!-- Dialog: Lista de Reportes de Servicio -->
    <Dialog
      v-model:visible="reportesDialogVisible"
      :header="`Reportes de Servicio (${reportesList.length})`"
      :modal="true"
      :style="{ width: '750px', maxWidth: '95vw' }"
      :draggable="false"
    >
      <div v-if="reportesList.length === 0" style="text-align:center;padding:1rem;color:#999;">
        Sin reportes cargados.
      </div>
      <DataTable v-else :value="reportesList" responsiveLayout="scroll">
        <Column header="Folio">
          <template #body="{ data }">
            {{ data.folio || `SERVICIO-${String(data.id).padStart(5, '0')}` }}
          </template>
        </Column>
        <Column field="tipo_servicio" header="Tipo de Servicio" />
        <Column field="nombre_cliente" header="Cliente" />
        <Column header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Acciones">
          <template #body="{ data }">
            <div style="display:flex;gap:0.5rem;">
              <Button
                icon="pi pi-file-pdf"
                label="Ver PDF"
                class="p-button-sm p-button-warning"
                :loading="loadingPdf"
                @click="verPDF(data)"
              />
              <Button
                v-if="esEditable"
                icon="pi pi-times"
                label="Quitar"
                class="p-button-sm p-button-danger p-button-outlined"
                :loading="quitando === data.id"
                @click="quitarReporte(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </Dialog>

    <!-- Dialog: PDF de Reporte de Servicio -->
    <Dialog
      v-model:visible="pdfDialogVisible"
      :header="pdfTitle"
      :modal="true"
      :style="{ width: '85vw' }"
      :draggable="false"
      @hide="cerrarPdfDialog"
    >
      <iframe
        v-if="pdfUrl"
        :src="pdfUrl"
        style="width:100%;height:80vh;border:none;"
      />
    </Dialog>

    <!-- Dialog: Agregar Servicios a la nota -->
    <Dialog
      v-model:visible="agregarDialogVisible"
      :header="`Agregar servicios a Nota #${item?.id}`"
      :modal="true"
      :style="{ width: '75vw' }"
      :draggable="false"
    >
      <div v-if="loadingDisponibles" style="text-align:center;padding:2rem;">
        <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
      </div>
      <template v-else>
        <div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-bottom:1rem;">
          <InputText v-model="filtroAgregarFolio" placeholder="Buscar por folio / OS" style="flex:1;min-width:150px;" />
          <InputText v-model="filtroAgregarCliente" placeholder="Buscar por cliente" style="flex:1;min-width:150px;" />
          <InputText v-model="filtroAgregarTipo" placeholder="Buscar por tipo" style="flex:1;min-width:150px;" />
        </div>
        <p v-if="!reportesDisponiblesFiltrados.length" style="text-align:center;color:var(--color-text-muted,#888);">
          {{ reportesDisponibles.length ? 'Sin resultados para los filtros aplicados.' : 'No hay reportes de servicio disponibles para agregar.' }}
        </p>
        <DataTable
          v-else
          v-model:selection="reportesSeleccionados"
          :value="reportesDisponiblesFiltrados"
          dataKey="id"
          :paginator="reportesDisponiblesFiltrados.length > 10"
          :rows="10"
          selectionMode="multiple"
          size="small"
        >
          <Column selectionMode="multiple" style="width:3rem" />
          <Column field="folio" header="Folio" />
          <Column field="tipo_servicio" header="Tipo" />
          <Column field="nombre_cliente" header="Cliente" />
          <Column field="total" header="Total">
            <template #body="{ data }">{{ data.total != null ? '$' + Number(data.total).toFixed(2) : '-' }}</template>
          </Column>
          <Column field="fecha" header="Fecha">
            <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
          </Column>
        </DataTable>
        <div style="display:flex;justify-content:flex-end;gap:0.75rem;margin-top:1.25rem;">
          <Button label="Cancelar" class="p-button-text" @click="agregarDialogVisible = false" />
          <Button
            label="Agregar seleccionados"
            icon="pi pi-check"
            class="p-button-success"
            :disabled="!reportesSeleccionados.length"
            :loading="agregando"
            @click="confirmarAgregar"
          />
        </div>
      </template>
    </Dialog>

    <!-- Dialog: ligar ingreso bancario a esta nota (conciliación) -->
    <Dialog v-model:visible="ligarDialogVisible" header="Ligar ingreso bancario" :modal="true" :style="{ width: '520px', maxWidth: '95vw' }" :draggable="false">
      <div v-if="!ingresoSeleccionado">
        <InputText v-model="filtroLigarBusqueda" placeholder="Buscar por banco o IMEI..." class="w-full" style="margin-bottom:0.75rem;" />
        <div v-if="loadingIngresosDisponibles" style="text-align:center;padding:1.5rem;"><i class="pi pi-spin pi-spinner"></i></div>
        <p v-else-if="!ingresosDisponiblesFiltrados.length" style="color:#999;text-align:center;">No hay ingresos bancarios disponibles para ligar.</p>
        <div v-else style="max-height:320px;overflow-y:auto;display:flex;flex-direction:column;gap:0.5rem;">
          <div
            v-for="g in ingresosDisponiblesFiltrados" :key="g.id"
            class="ingreso-opcion" @click="seleccionarIngreso(g)"
          >
            <strong>{{ g.banco }}</strong> — disponible ${{ Number(g.monto_disponible).toFixed(2) }} de ${{ Number(g.monto).toFixed(2) }}
            <div style="font-size:0.8rem;opacity:0.75;">IMEI: {{ (g.imeis || []).join(', ') || '-' }} · {{ formatFecha(g.fecha_transaccion) }}</div>
          </div>
        </div>
      </div>
      <div v-else>
        <p style="margin-top:0;"><strong>{{ ingresoSeleccionado.banco }}</strong> — disponible ${{ Number(ingresoSeleccionado.monto_disponible).toFixed(2) }}</p>
        <div class="form-group">
          <label style="font-weight:bold;display:block;margin-bottom:0.3rem;">Monto a aplicar a esta nota</label>
          <InputNumber v-model="montoAplicadoForm" mode="currency" currency="MXN" locale="es-MX" class="w-full" :min="0" :max="Number(ingresoSeleccionado.monto_disponible) || 0" />
        </div>
        <p style="font-size:0.8rem;opacity:0.75;display:flex;align-items:center;gap:0.5rem;">
          <span v-if="!editandoTotalNota">
            Saldo pendiente de la nota: ${{ saldoPendienteNota.toFixed(2) }} (total ${{ Number(item.total).toFixed(2) }})
            <a href="#" @click.prevent="abrirEditarTotalNota" style="margin-left:0.4rem;">corregir total</a>
          </span>
          <span v-else style="display:flex;align-items:center;gap:0.4rem;">
            Total real de la nota:
            <InputNumber v-model="totalNotaForm" mode="currency" currency="MXN" locale="es-MX" style="width:140px;" />
            <Button icon="pi pi-check" class="p-button-text p-button-success p-button-sm" :loading="guardandoTotalNota" @click="guardarTotalNota" />
            <Button icon="pi pi-times" class="p-button-text p-button-sm" @click="editandoTotalNota = false" />
          </span>
        </p>
        <p v-if="esUnderpay && !conceptosLlenados" style="font-size:0.8rem;color:#1976d2;">
          Pago parcial — quedan ${{ Math.abs(diferenciaLigar).toFixed(2) }} pendientes. La nota sigue abierta y se puede completar después con otro pago.
        </p>
        <div v-if="!cubierto" class="form-group">
          <label style="font-weight:bold;display:block;margin-bottom:0.3rem;color:#b26a00;">
            {{ esOverpay ? 'Se está aplicando de más a esta nota — obligatorio justificar' : 'Justificar el faltante cierra la nota como pagada (opcional)' }} —
            desglosa la diferencia (${{ Math.abs(diferenciaLigar).toFixed(2) }}) en conceptos
          </label>
          <div v-for="(c, idx) in conceptosForm" :key="idx" style="display:flex;gap:0.5rem;margin-bottom:0.4rem;align-items:center;">
            <InputText v-model="c.concepto" placeholder="Concepto (ej: descuento, recargo...)" style="flex:2;" />
            <InputNumber v-model="c.monto" mode="currency" currency="MXN" locale="es-MX" style="flex:1;" />
            <Button icon="pi pi-trash" class="p-button-text p-button-danger p-button-sm" :disabled="conceptosForm.length === 1" @click="quitarConcepto(idx)" />
          </div>
          <Button label="Agregar concepto" icon="pi pi-plus" class="p-button-text p-button-sm" @click="agregarConcepto" />
          <p v-if="conceptosLlenados || esOverpay" style="font-size:0.8rem;margin-top:0.4rem;" :style="{ color: conceptosCuadran ? '#2e7d32' : '#c62828' }">
            Suma de conceptos: ${{ totalConceptos.toFixed(2) }} / ${{ Math.abs(diferenciaLigar).toFixed(2) }} requerido
          </p>
        </div>
        <div style="display:flex;justify-content:flex-end;gap:0.75rem;">
          <Button label="Volver" class="p-button-text" @click="ingresoSeleccionado = null" />
          <Button
            label="Ligar" icon="pi pi-check" class="p-button-success" :loading="ligando"
            :disabled="!montoAplicadoForm || !puedeLigar"
            @click="confirmarLigarIngreso"
          />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import Textarea from 'primevue/textarea';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import { useToast } from 'primevue/usetoast';
import {
  getNotaById,
  actualizarStatusNota,
  actualizarCamposNota,
  actualizarLugarPagoNota,
  actualizarObservacionesNota,
  actualizarDatosPagoNota,
  subirComprobanteNota,
  eliminarComprobanteNota,
  getPagosNota,
  crearPagoNota,
  eliminarPagoNota,
  asignarComprobanteComoPagoNota,
  agregarReportesNota,
  quitarReportesNota,
  getNotas,
  getFacturas
} from '@/services/pagosService';
import { generarPagoPDF } from '@/services/PagoPdfService.js';
import { getIngresosBanco, getIngresosLigadosANota, asignarIngresoANota, desligarIngresoNota } from '@/services/ingresosBancoService';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const id = computed(() => route.params.id);

const item = ref(null);
const loading = ref(false);
const saving = ref(false);
const nuevoStatus = ref('');
const nuevoLugarPago = ref('');
const observacionesTexto = ref('');
const guardandoObs = ref(false);
const datosPagoForm = ref({ metodo_pago: 'PUE', forma_pago: '03', notas_extra: '' });
const guardandoDatosPago = ref(false);
const clienteFiscal = ref(null);

const formasPago = [
  { label: '01 - Efectivo', value: '01' },
  { label: '02 - Cheque nominativo', value: '02' },
  { label: '03 - Transferencia electrónica de fondos', value: '03' },
  { label: '04 - Tarjeta de crédito', value: '04' },
  { label: '28 - Tarjeta de débito', value: '28' },
  { label: '99 - Por definir', value: '99' },
];
const archivoSeleccionado = ref(null);
const subiendo = ref(false);
const eliminandoComprobante = ref(null);

const pagosAdicionales = ref([]);
const nuevoPago = ref({ banco: '', monto: null, comprobante: null });
const registrandoPago = ref(false);
const eliminandoPago = ref(null);

const asignando = ref(null);
const formAsignar = ref({ banco: '', monto: null });
// Al asignar un comprobante a banco se preselecciona el banco donde se
// registró el pago (lugar_pago de la nota).
function toggleAsignar(comp) {
  if (asignando.value === comp) { asignando.value = null; return; }
  asignando.value = comp;
  formAsignar.value = { banco: item.value?.lugar_pago || '', monto: null };
}
const asignandoGuardando = ref(false);
const detalleOrdenesMap = ref({});

// Ingresos bancarios ligados (ver ingresosBancoService.js) — alternativa a
// "Pagos adicionales": el comprobante se sube desde Bancos.vue/DetalleBanco.vue
// sin nota, y aquí se liga con conciliación de monto (backend calcula la
// diferencia contra el saldo pendiente y exige justificación si no cuadra).
const ingresosLigados = ref([]);
const ligarDialogVisible = ref(false);
const loadingIngresosDisponibles = ref(false);
const ingresosDisponibles = ref([]);
const filtroLigarBusqueda = ref('');
const ingresoSeleccionado = ref(null);
const montoAplicadoForm = ref(null);
const conceptosForm = ref([{ concepto: '', monto: null }]);
const ligando = ref(false);
const desligandoIngresoId = ref(null);
// Corregir el total de la nota directo desde el diálogo de ligar — para
// cuando la diferencia no es un descuento/recargo real sino que el total
// capturado en la nota está mal, así se elimina en vez de "justificarla".
const editandoTotalNota = ref(false);
const totalNotaForm = ref(null);
const guardandoTotalNota = ref(false);
function abrirEditarTotalNota() {
  totalNotaForm.value = Number(item.value?.total) || 0;
  editandoTotalNota.value = true;
}
async function guardarTotalNota() {
  if (totalNotaForm.value == null) return;
  guardandoTotalNota.value = true;
  try {
    await actualizarCamposNota(item.value.id, { total: Number(totalNotaForm.value) });
    item.value.total = Number(totalNotaForm.value);
    editandoTotalNota.value = false;
    toast.add({ severity: 'success', summary: 'Total actualizado', life: 2500 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el total.', life: 4000 });
  }
  guardandoTotalNota.value = false;
}

const saldoPendienteNota = computed(() => {
  const total = Number(item.value?.total) || 0;
  const cubiertoPagos = pagosAdicionales.value.reduce((s, p) => s + (Number(p.monto) || 0), 0);
  const cubiertoIngresos = ingresosLigados.value.reduce((s, l) => s + (Number(l.monto_aplicado) || 0), 0);
  return total - cubiertoPagos - cubiertoIngresos;
});
// diferencia = lo que se va a aplicar menos lo que la nota realmente debe.
// El status "pagada" se decide solo (sin checkbox), igual que el backend:
// cuadra exacto -> pagada sin conceptos. Sobra (overpay) -> conceptos
// obligatorios, pagada. Falta (underpay) -> conceptos opcionales: vacíos
// deja la nota abierta (pago parcial), llenados y cuadrando la cierra pagada.
const diferenciaLigar = computed(() => (Number(montoAplicadoForm.value) || 0) - saldoPendienteNota.value);
const cubierto = computed(() => Math.abs(diferenciaLigar.value) <= 1);
const esOverpay = computed(() => diferenciaLigar.value > 1);
const esUnderpay = computed(() => diferenciaLigar.value < -1);
const totalConceptos = computed(() => conceptosForm.value.reduce((s, c) => s + (Number(c.monto) || 0), 0));
const conceptosLlenados = computed(() => conceptosForm.value.some(c => c.concepto.trim() || Number(c.monto) > 0));
const conceptosCuadran = computed(() => conceptosLlenados.value && Math.abs(totalConceptos.value - Math.abs(diferenciaLigar.value)) <= 1);
const puedeLigar = computed(() => {
  if (cubierto.value) return true;
  if (esOverpay.value) return conceptosCuadran.value;
  return !conceptosLlenados.value || conceptosCuadran.value;
});
function agregarConcepto() {
  conceptosForm.value.push({ concepto: '', monto: null });
}
function quitarConcepto(idx) {
  conceptosForm.value.splice(idx, 1);
}
const ingresosDisponiblesFiltrados = computed(() => {
  const q = filtroLigarBusqueda.value.trim().toLowerCase();
  return ingresosDisponibles.value.filter(g => {
    if (g.estado_asignacion === 'asignado') return false;
    if (!q) return true;
    return (g.banco || '').toLowerCase().includes(q) || (g.imeis || []).some(i => String(i).toLowerCase().includes(q));
  });
});

// Agregar servicios
const agregarDialogVisible = ref(false);
const reportesDisponibles = ref([]);
const loadingDisponibles = ref(false);
const reportesSeleccionados = ref([]);
const agregando = ref(false);
const filtroAgregarCliente = ref('');
const filtroAgregarFolio = ref('');
const filtroAgregarTipo = ref('');

const reportesDisponiblesFiltrados = computed(() => {
  return reportesDisponibles.value.filter(r => {
    const cliente = filtroAgregarCliente.value.trim().toLowerCase();
    const folio = filtroAgregarFolio.value.trim().toLowerCase();
    const tipo = filtroAgregarTipo.value.trim().toLowerCase();
    if (cliente && !(r.nombre_cliente || '').toLowerCase().includes(cliente)) return false;
    if (folio && !(r.folio || '').toLowerCase().includes(folio)) return false;
    if (tipo && !(r.tipo_servicio || '').toLowerCase().includes(tipo)) return false;
    return true;
  });
});

const detalleOrdenesEnriquecido = computed(() => {
  const ordenes = item.value?.detalle_ordenes || [];
  return ordenes.map(orden => ({
    ...orden,
    ...(detalleOrdenesMap.value[orden.id] || {})
  }));
});

const esEditable = computed(() => {
  if (!item.value?.status) return false;
  const s = item.value.status.toLowerCase();
  return !['pagado', 'cancelado'].includes(s);
});

// Reportes de servicio
const reportesDialogVisible = ref(false);
const pdfDialogVisible = ref(false);
const reportesList = ref([]);
const loadingReportes = ref(false);
const pdfUrl = ref('');
const pdfTitle = ref('');
const loadingPdf = ref(false);
const quitando = ref(null);  // ID del reporte que se está quitando

const lugaresDisponibles = [
  'ASP Vianey',
  'ASP Renovaciones',
  'Comercializadora',
  'BBVA PAU',
  'Mercadopago Victor',
  'Mercadopago Eliseo',
  'Efectivo oficina',
  'Efectivo tecnico'
];

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

function urlComprobante(path) {
  if (!path) return '';
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${API_URL}${p}`;
}

function nombreArchivo(path) {
  if (!path) return 'comprobante';
  return path.split('/').pop();
}

const opcionesStatus = [
  { label: 'Pendiente de pago', value: 'pendiente de pago' },
  { label: 'Pagado', value: 'pagado' },
  { label: 'Cancelado', value: 'cancelado' }
];

function formatFecha(f) {
  if (!f) return '';
  const [y, m, d] = String(f).slice(0, 10).split('-');
  return `${d}/${m}/${y}`;
}

function formatFechaHora(f) {
  if (!f) return '';
  const s = String(f);
  const fecha = formatFecha(s);
  const hora = s.slice(11, 16);
  return hora ? `${fecha} ${hora}` : fecha;
}

function badgeClass(status) {
  if (status === 'pagado') return 'success';
  if (status === 'cancelado') return 'danger';
  return 'warning';
}

function formatearImeisOrden(orden) {
  const imeis = new Set();

  if (orden?.imei) imeis.add(String(orden.imei));

  if (Array.isArray(orden?.imeis_articulos)) {
    for (const articulo of orden.imeis_articulos) {
      if (!Array.isArray(articulo?.imeis)) continue;
      for (const imei of articulo.imeis) {
        if (imei) imeis.add(String(imei));
      }
    }
  }

  return imeis.size ? Array.from(imeis).join(', ') : '-';
}

async function cargarDetalleOrdenesEnriquecido() {
  const ordenes = item.value?.detalle_ordenes || [];
  if (!ordenes.length) {
    detalleOrdenesMap.value = {};
    return;
  }

  try {
    const detalles = await Promise.all(
      ordenes.map(async orden => {
        try {
          const resp = await axios.get(`${API_URL}/reportes-servicio/${orden.id}`);
          return [orden.id, resp.data];
        } catch {
          return [orden.id, null];
        }
      })
    );

    detalleOrdenesMap.value = Object.fromEntries(detalles.filter(([, data]) => !!data));
  } catch {
    detalleOrdenesMap.value = {};
  }
}

async function cargarDetalle() {
  loading.value = true;
  try {
    item.value = await getNotaById(id.value);
    nuevoStatus.value = item.value?.status || '';
    nuevoLugarPago.value = item.value?.lugar_pago || '';
    observacionesTexto.value = item.value?.observaciones || '';
    datosPagoForm.value = {
      metodo_pago: item.value?.metodo_pago || 'PUE',
      forma_pago: item.value?.forma_pago || '03',
      notas_extra: item.value?.notas_extra || '',
    };
    await cargarDetalleOrdenesEnriquecido();
    await cargarClienteFiscal();
    if (!nuevoPago.value.banco) nuevoPago.value.banco = item.value?.lugar_pago || '';
    pagosAdicionales.value = await getPagosNota(id.value);
    ingresosLigados.value = await getIngresosLigadosANota(id.value);
  } catch {
    item.value = null;
    detalleOrdenesMap.value = {};
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el detalle.', life: 4000 });
  }
  loading.value = false;
}

async function cargarClienteFiscal() {
  clienteFiscal.value = null;
  if (!item.value?.cliente) return;
  try {
    const resp = await axios.get(`${API_URL}/clientes`);
    const match = (resp.data || []).find(
      c => (c.nombre || '').trim().toLowerCase() === item.value.cliente.trim().toLowerCase()
    );
    clienteFiscal.value = match || null;
  } catch {
    clienteFiscal.value = null;
  }
}

async function guardarDatosPago() {
  guardandoDatosPago.value = true;
  try {
    await actualizarDatosPagoNota(id.value, { ...datosPagoForm.value });
    Object.assign(item.value, datosPagoForm.value);
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Datos de pago guardados correctamente.', life: 3000 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron guardar los datos de pago.', life: 4000 });
  }
  guardandoDatosPago.value = false;
}

async function cambiarStatusYLugar() {
  const statusChanged = nuevoStatus.value && nuevoStatus.value !== item.value?.status;
  const lugarChanged = nuevoLugarPago.value && nuevoLugarPago.value !== item.value?.lugar_pago;

  if (!statusChanged && !lugarChanged) return;

  saving.value = true;
  try {
    if (statusChanged) {
      await actualizarStatusNota(id.value, nuevoStatus.value);
      item.value.status = nuevoStatus.value;
    }
    if (lugarChanged) {
      await actualizarLugarPagoNota(id.value, nuevoLugarPago.value);
      item.value.lugar_pago = nuevoLugarPago.value;
    }
    toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Datos actualizados correctamente.', life: 3000 });
    // Si se canceló, recargar para reflejar que reporte_ids quedó vacío
    if (statusChanged && nuevoStatus.value === 'cancelado') await cargarDetalle();
  } catch (error) {
    console.error(error);
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar los datos.', life: 4000 });
  }
  saving.value = false;
}

async function descargarPDF() {
  if (!item.value) return;
  try {
    await generarPagoPDF('nota', item.value);
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo generar el PDF.', life: 4000 });
  }
}

async function guardarObservaciones() {
  guardandoObs.value = true;
  try {
    await actualizarObservacionesNota(id.value, observacionesTexto.value);
    item.value.observaciones = observacionesTexto.value;
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Observaciones guardadas correctamente.', life: 3000 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron guardar las observaciones.', life: 4000 });
  }
  guardandoObs.value = false;
}

onMounted(() => {
  cargarDetalle();
});

function onFileChange(event) {
  const files = event?.target?.files;
  archivoSeleccionado.value = files && files.length ? files[0] : null;
}

async function subirComprobante() {
  if (!archivoSeleccionado.value) return;
  subiendo.value = true;
  try {
    await subirComprobanteNota(id.value, archivoSeleccionado.value);
    toast.add({ severity: 'success', summary: 'Subido', detail: 'Comprobante cargado correctamente.', life: 3000 });
    archivoSeleccionado.value = null;
    const inputEl = document.getElementById('inputComprobante');
    if (inputEl) inputEl.value = '';
    await cargarDetalle();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo subir el comprobante.', life: 4000 });
  }
  subiendo.value = false;
}

async function eliminarComprobante(path) {
  eliminandoComprobante.value = path;
  try {
    await eliminarComprobanteNota(id.value, path);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Comprobante eliminado.', life: 3000 });
    await cargarDetalle();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el comprobante.', life: 4000 });
  }
  eliminandoComprobante.value = null;
}

function onFilePagoChange(event) {
  const files = event?.target?.files;
  nuevoPago.value.comprobante = files && files.length ? files[0] : null;
}

async function registrarPagoAdicional() {
  if (!nuevoPago.value.banco || !nuevoPago.value.monto) return;
  registrandoPago.value = true;
  try {
    await crearPagoNota(id.value, nuevoPago.value);
    toast.add({ severity: 'success', summary: 'Registrado', detail: 'Pago registrado correctamente.', life: 3000 });
    nuevoPago.value = { banco: '', monto: null, comprobante: null };
    await cargarDetalle();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo registrar el pago.', life: 4000 });
  }
  registrandoPago.value = false;
}

async function confirmarAsignarComprobante(path) {
  if (!formAsignar.value.banco || !formAsignar.value.monto) return;
  asignandoGuardando.value = true;
  try {
    await asignarComprobanteComoPagoNota(id.value, { path, ...formAsignar.value });
    toast.add({ severity: 'success', summary: 'Asignado', detail: 'Comprobante asignado como pago adicional.', life: 3000 });
    asignando.value = null;
    formAsignar.value = { banco: '', monto: null };
    await cargarDetalle();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo asignar el comprobante.', life: 4000 });
  }
  asignandoGuardando.value = false;
}

async function eliminarPagoAdicional(pago) {
  eliminandoPago.value = pago.id;
  try {
    await eliminarPagoNota(id.value, pago.id);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Pago eliminado.', life: 3000 });
    await cargarDetalle();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el pago.', life: 4000 });
  }
  eliminandoPago.value = null;
}

async function abrirLigarIngreso() {
  ingresoSeleccionado.value = null;
  filtroLigarBusqueda.value = '';
  ligarDialogVisible.value = true;
  loadingIngresosDisponibles.value = true;
  try {
    ingresosDisponibles.value = await getIngresosBanco();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los ingresos bancarios.', life: 4000 });
  }
  loadingIngresosDisponibles.value = false;
}

function seleccionarIngreso(g) {
  ingresoSeleccionado.value = g;
  const pendiente = Math.max(saldoPendienteNota.value, 0);
  montoAplicadoForm.value = Math.min(Number(g.monto_disponible) || 0, pendiente) || Number(g.monto_disponible) || 0;
  conceptosForm.value = [{ concepto: '', monto: null }];
  editandoTotalNota.value = false;
}

async function confirmarLigarIngreso() {
  if (!ingresoSeleccionado.value || !montoAplicadoForm.value) return;
  ligando.value = true;
  try {
    const conceptos = conceptosForm.value
      .filter(c => c.concepto.trim() && Number(c.monto) > 0)
      .map(c => ({ concepto: c.concepto.trim(), monto: Number(c.monto) }));
    await asignarIngresoANota(ingresoSeleccionado.value.id, {
      nota_id: Number(id.value),
      monto_aplicado: Number(montoAplicadoForm.value),
      conceptos,
    });
    toast.add({ severity: 'success', summary: 'Ligado', detail: 'Ingreso ligado a la nota.', life: 3000 });
    ligarDialogVisible.value = false;
    await cargarDetalle();
  } catch (e) {
    const detail = e?.response?.data?.detail || '';
    toast.add({ severity: detail.includes('conceptos') ? 'warn' : 'error', summary: detail.includes('conceptos') ? 'Faltan conceptos' : 'Error', detail: detail || 'No se pudo ligar el ingreso.', life: 5000 });
  }
  ligando.value = false;
}

async function desligarIngreso(link) {
  desligandoIngresoId.value = link.id;
  try {
    await desligarIngresoNota(link.id);
    toast.add({ severity: 'success', summary: 'Desligado', detail: 'Ingreso desligado de la nota.', life: 3000 });
    await cargarDetalle();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo desligar.', life: 4000 });
  }
  desligandoIngresoId.value = null;
}

async function abrirReportesDialog() {
  if (!item.value?.reporte_ids?.length) return;
  loadingReportes.value = true;
  try {
    const results = await Promise.all(
      item.value.reporte_ids.map(rid =>
        axios.get(`${API_URL}/reportes-servicio/${rid}`).then(r => r.data)
      )
    );
    reportesList.value = results;
    reportesDialogVisible.value = true;
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los reportes de servicio.', life: 4000 });
  }
  loadingReportes.value = false;
}

async function verPDF(reporte) {
  loadingPdf.value = true;
  try {
    const resp = await axios.get(`${API_URL}/reportes-servicio/${reporte.id}`);
    const merged = { ...reporte, ...resp.data };
    const { generarReporteServicioPDF } = await import('@/components/GeneraReporteServicioPDF.js');
    const url = await generarReporteServicioPDF({ reporte: merged, mode: 'bloburl' });
    if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value);
    pdfUrl.value = url;
    pdfTitle.value = merged.folio || `Reporte #${merged.id}`;
    pdfDialogVisible.value = true;
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo generar el PDF del reporte.', life: 4000 });
  }
  loadingPdf.value = false;
}

function cerrarPdfDialog() {
  pdfDialogVisible.value = false;
  if (pdfUrl.value) {
    URL.revokeObjectURL(pdfUrl.value);
    pdfUrl.value = '';
  }
}

async function quitarReporte(reporte) {
  quitando.value = reporte.id;
  try {
    await quitarReportesNota(id.value, [reporte.id]);
    reportesList.value = reportesList.value.filter(r => r.id !== reporte.id);
    if (reportesList.value.length === 0) reportesDialogVisible.value = false;
    await cargarDetalle();
    toast.add({ severity: 'success', summary: 'Quitado', detail: `Reporte "${reporte.folio || '#' + reporte.id}" quitado correctamente.`, life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo quitar el reporte.', life: 4000 });
  }
  quitando.value = null;
}

async function abrirAgregarDialog() {
  loadingDisponibles.value = true;
  agregarDialogVisible.value = true;
  try {
    const [todosReportes, notas, facturas] = await Promise.all([
      axios.get(`${API_URL}/reportes-servicio-todos`).then(r => r.data),
      getNotas(),
      getFacturas()
    ]);
    const asignados = new Set();
    const currentIds = new Set(item.value?.reporte_ids || []);
    for (const n of notas) {
      for (const rid of (n.reporte_ids || [])) {
        if (n.id === Number(id.value)) continue;
        asignados.add(rid);
      }
    }
    for (const f of facturas) {
      for (const rid of (f.reporte_ids || [])) {
        asignados.add(rid);
      }
    }
    reportesDisponibles.value = todosReportes.filter(r => !asignados.has(r.id) && !currentIds.has(r.id));
    reportesSeleccionados.value = [];
    filtroAgregarCliente.value = '';
    filtroAgregarFolio.value = '';
    filtroAgregarTipo.value = '';
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los reportes disponibles.', life: 4000 });
    agregarDialogVisible.value = false;
  }
  loadingDisponibles.value = false;
}

async function confirmarAgregar() {
  if (!reportesSeleccionados.value.length) return;
  agregando.value = true;
  try {
    const nuevos_ids = reportesSeleccionados.value.map(r => r.id);
    await agregarReportesNota(id.value, nuevos_ids);
    agregarDialogVisible.value = false;
    reportesSeleccionados.value = [];
    await cargarDetalle();
    toast.add({ severity: 'success', summary: 'Agregado', detail: `Se agregaron ${nuevos_ids.length} servicio(s) correctamente.`, life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudieron agregar los servicios.', life: 4000 });
  }
  agregando.value = false;
}
</script>

<style scoped>
.detalle-pago-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  max-width: 1200px;
}
.detalle-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-title);
}
.detalle-card {
  background: var(--color-card);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid var(--color-border);
}
.detalle-row {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}
.detalle-row:last-child { border-bottom: none; }
.cambiar-status {
  margin-bottom: 2rem;
}
.cambiar-status h3 {
  margin-bottom: 0.75rem;
  color: var(--color-title);
}
.status-options {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}
.status-options .w-full {
  flex: 1;
  min-width: 200px;
}
.ordenes-detalle h3 {
  margin-bottom: 0.75rem;
  color: var(--color-title);
}
.observaciones-section {
  margin-bottom: 2rem;
}
.observaciones-section h3 {
  margin-bottom: 0.75rem;
  color: var(--color-title);
}
.datos-pago-section {
  margin-bottom: 2rem;
}
.datos-pago-section h3 {
  margin-bottom: 0.75rem;
  color: var(--color-title);
}
.cliente-fiscal-info {

  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.datos-pago-form {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
.datos-pago-field {
  flex: 1;
  min-width: 220px;
}
.datos-pago-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.3rem;
  font-size: 0.85rem;
}
.comprobante-section {
  margin-bottom: 2rem;
}
.comprobante-section h3 {
  margin-bottom: 0.75rem;
  color: var(--color-title);
}
.comprobante-actual {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}
.comprobantes-lista {
  margin-bottom: 0.75rem;
}
.comprobante-item {
  display: flex;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-border);
}
.comprobante-item:last-child {
  border-bottom: none;
}
.comprobante-upload {
  margin-top: 0.5rem;
}
.mt-2 { margin-top: 0.5rem; }
.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: bold;
}
.badge-success { background: #c8e6c9; color: #256029; }
.badge-warning { background: #fff3cd; color: #856404; }
.badge-danger  { background: #f8d7da; color: #721c24; }
.mb-3 { margin-bottom: 1rem; }
.ingreso-opcion {
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
}
.ingreso-opcion:hover {
  background: var(--color-bg-light, #f5f5f5);
}
.w-full { width: 100%; }
.form-group { margin-bottom: 1rem; }
.ingreso-ligado {
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.5rem;
}
.ingreso-ligado:last-child { border-bottom: none; }
.ingreso-ligado .comprobante-item { border-bottom: none; }
.ingreso-ligado-detalle {
  font-size: 0.83rem;
  opacity: 0.85;
  padding: 0.25rem 0 0.4rem 1.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
</style>
