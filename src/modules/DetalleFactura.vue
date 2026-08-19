<template>
  <div class="detalle-factura-container">
    <Button icon="pi pi-arrow-left" label="Volver a Facturación" class="p-button-text mb-3" @click="router.push('/facturacion')" />

    <div v-if="loading" style="text-align:center;padding:3rem;"><i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i></div>

    <div v-else-if="item">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:0.75rem;flex-wrap:wrap;">
        <h2 class="detalle-title" style="margin-bottom:0;">Factura #{{ item.id }}</h2>
        <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
          <Button
            v-if="item.reporte_ids && item.reporte_ids.length"
            icon="pi pi-list" :label="`Ver Reportes de Servicio (${item.reporte_ids.length})`"
            class="p-button-outlined p-button-info" :loading="loadingReportes" @click="abrirReportesDialog"
          />
          <Button
            v-if="esEditable" icon="pi pi-plus" label="Agregar Servicios"
            class="p-button-outlined p-button-success" @click="abrirAgregarDialog"
          />
          <Button
            v-if="item.status === 'Timbrado' && esAdmin && !tieneRepsTimbrados" icon="pi pi-ban" label="Cancelar factura"
            class="p-button-danger p-button-outlined" @click="abrirCancelarDialog"
          />
          <span v-if="item.status === 'Timbrado' && esAdmin && tieneRepsTimbrados" style="font-size:0.8rem;opacity:0.7;">
            Cancela primero los complementos de pago (REP) para poder cancelar esta factura.
          </span>
        </div>
      </div>

      <div class="detalle-card">
        <div class="detalle-row"><strong>Órdenes:</strong> {{ (item.ordenes || []).join(', ') || '-' }}</div>
        <div class="detalle-row"><strong>Cliente:</strong> {{ item.cliente || '-' }}</div>
        <div class="detalle-row"><strong>Total:</strong> {{ formatTotal(item.total) }}</div>
        <div class="detalle-row"><strong>Fecha:</strong> {{ formatFecha(item.fecha) }}</div>
        <div class="detalle-row">
          <strong>Lugar de pago:</strong>
          <Dropdown v-model="lugarPagoSeleccionado" :options="lugaresDisponibles" showClear placeholder="Sin asignar"
            class="lugar-pago-select" @change="guardarLugarPago" />
        </div>
        <div class="detalle-row">
          <strong>Estatus:</strong>
          <span :class="'badge badge-' + badgeClass(item.status)" style="margin-left:0.5rem;">{{ item.status }}</span>
        </div>
        <div class="detalle-row">
          <strong>Pago:</strong>
          <span :class="'badge badge-' + (item.pagado ? 'success' : 'warning')" style="margin-left:0.5rem;">{{ item.pagado ? 'Pagada' : 'Pendiente pago' }}</span>
          <Button
            v-if="!esPPD"
            :label="item.pagado ? 'Marcar como pendiente' : 'Marcar como pagada'"
            icon="pi pi-dollar" class="p-button-sm p-button-text" style="margin-left:0.75rem;"
            :loading="guardandoPagado" @click="togglePagado"
          />
          <small v-else style="margin-left:0.75rem;color:var(--color-text);opacity:0.7;">
            Es PPD — se marca sola cuando se completan los complementos de pago (abajo).
          </small>
        </div>
      </div>

      <!-- ═══ Timbrado ═══ -->
      <div v-if="item.status === 'Pendiente timbre'" class="timbrado-card">
        <h3><i class="pi pi-verified" /> Timbrar factura</h3>

        <div v-if="timbrarForm.metodo_pago === 'PPD'" class="ppd-flujo-banner">
          <i class="pi pi-info-circle" />
          <div>
            <strong>Esta factura es PPD (pago diferido/parcialidades) — flujo en 2 pasos:</strong>
            <ol>
              <li>Timbras esta factura ahora <em>sin</em> registrar ningún pago (es el CFDI de ingreso, forma de pago "99 - Por definir").</li>
              <li>Cuando el cliente pague (todo o en parcialidades), regresas a esta pantalla y usas <strong>"Registrar pago"</strong> en la sección "Complementos de pago (REP)" que aparece abajo una vez timbrada. Cada pago genera su propio CFDI de tipo Pago, relacionado automáticamente con esta factura.</li>
            </ol>
          </div>
        </div>

        <div v-if="item.ultimo_error_timbrado" class="error-timbrado-banner">
          <i class="pi pi-exclamation-triangle" />
          <div>
            <strong>El último intento de timbrado falló{{ item.ultimo_error_timbrado_fecha ? ' (' + formatFecha(item.ultimo_error_timbrado_fecha) + ')' : '' }}:</strong>
            <p>{{ item.ultimo_error_timbrado }}</p>
            <small v-if="pareceErrorDeCsd(item.ultimo_error_timbrado)">
              <i class="pi pi-info-circle" /> Este mensaje suena a un problema con el certificado de sello digital (CSD) — revisa su vigencia con el PAC antes de reintentar.
            </small>
          </div>
        </div>

        <div v-if="cargandoCliente" style="text-align:center;padding:1.5rem;"><i class="pi pi-spin pi-spinner" /></div>

        <template v-else>
          <label class="publico-general-toggle">
            <input type="checkbox" v-model="publicoGeneral" />
            Venta a público en general (sin RFC específico del cliente)
          </label>

          <template v-if="!publicoGeneral">
            <!-- Datos fiscales del cliente: completos -> resumen; incompletos/inexistentes -> formulario -->
            <div v-if="datosFiscalesCompletos" class="fiscal-resumen">
              <div class="fiscal-resumen-item"><span>RFC</span><strong>{{ clienteFiscal.rfc }}</strong></div>
              <div class="fiscal-resumen-item"><span>C.P.</span><strong>{{ clienteFiscal.codigo_postal }}</strong></div>
              <div class="fiscal-resumen-item"><span>Régimen fiscal</span><strong>{{ clienteFiscal.regimen_fiscal }}</strong></div>
              <div class="fiscal-resumen-item"><span>Correo</span><strong>{{ clienteFiscal.correo }}</strong></div>
              <Button label="Editar" icon="pi pi-pencil" class="p-button-text p-button-sm" @click="editandoFiscal = true" />
            </div>

            <div v-if="!datosFiscalesCompletos || editandoFiscal" class="fiscal-form">
              <p class="fiscal-form-aviso">
                <i class="pi pi-info-circle" />
                {{ clienteExiste ? 'Faltan datos fiscales de este cliente.' : 'Este cliente no está registrado — se creará al guardar.' }}
                Sin esto no se puede timbrar.
              </p>
              <div class="fiscal-form-grid">
                <div class="fiscal-field">
                  <label>RFC</label>
                  <InputText v-model="fiscalForm.rfc" placeholder="XAXX010101000" class="w-full" :class="{ 'p-invalid': fiscalForm.rfc && !rfcValido }" />
                  <small v-if="fiscalForm.rfc && !rfcValido" class="fiscal-error">RFC con formato inválido</small>
                </div>
                <div class="fiscal-field">
                  <label>Código postal</label>
                  <InputText v-model="fiscalForm.codigo_postal" placeholder="64000" maxlength="5" class="w-full" />
                </div>
                <div class="fiscal-field">
                  <label>Régimen fiscal (SAT)</label>
                  <Dropdown v-model="fiscalForm.regimen_fiscal" :options="REGIMENES_FISCALES" optionLabel="label" optionValue="value" placeholder="Selecciona..." class="w-full" />
                </div>
                <div class="fiscal-field">
                  <label>Correo (para enviarle el CFDI)</label>
                  <InputText v-model="fiscalForm.correo" placeholder="cliente@correo.com" class="w-full" :class="{ 'p-invalid': fiscalForm.correo && !correoValido }" />
                  <small v-if="fiscalForm.correo && !correoValido" class="fiscal-error">Correo con formato inválido</small>
                </div>
              </div>
              <Button label="Guardar datos fiscales" icon="pi pi-save" class="p-button-sm" :loading="guardandoFiscal" @click="guardarDatosFiscales" />
            </div>
          </template>

          <div class="fiscal-form-grid" style="margin-top:1rem;">
            <div class="fiscal-field">
              <label>Uso CFDI</label>
              <Dropdown v-if="!publicoGeneral" v-model="timbrarForm.uso_cfdi" :options="USOS_CFDI" optionLabel="label" optionValue="value" placeholder="Selecciona..." class="w-full" />
              <InputText v-else value="S01 - Sin efectos fiscales (forzado)" class="w-full" disabled />
            </div>
            <div class="fiscal-field">
              <label>Método de pago</label>
              <Dropdown v-model="timbrarForm.metodo_pago" :options="[{ label: 'PUE - Pago en una sola exhibición', value: 'PUE' }, { label: 'PPD - Pago en parcialidades o diferido', value: 'PPD' }]" optionLabel="label" optionValue="value" placeholder="Selecciona..." class="w-full" />
            </div>
            <div class="fiscal-field">
              <label>Forma de pago</label>
              <Dropdown v-model="timbrarForm.forma_pago" :options="formasPago" optionLabel="label" optionValue="value" placeholder="Selecciona..." class="w-full" />
            </div>
          </div>
          <small class="fiscal-form-aviso" style="color:var(--color-text);opacity:0.75;font-weight:400;">
            <i class="pi pi-info-circle" /> Confirma estos tres campos según cómo se cobró realmente esta factura — no hay valor por defecto.
          </small>
          <small v-if="camposFaltantes.length" class="fiscal-error" style="display:block;margin-top:0.35rem;">
            <i class="pi pi-exclamation-triangle" /> Falta: {{ camposFaltantes.join(', ') }}
          </small>

          <div style="display:flex;gap:0.75rem;flex-wrap:wrap;align-items:center;">
            <Button
              :label="item.facturapi_draft_id ? 'Regenerar prefactura' : 'Generar prefactura'" icon="pi pi-file-edit"
              class="p-button-outlined" :disabled="!datosFiscalesListos" :loading="generandoPrefactura" @click="generarPrefactura"
            />
            <Button
              v-if="item.facturapi_draft_id" label="Ver PDF (borrador)" icon="pi pi-file-pdf"
              class="p-button-outlined p-button-warning" @click="verPrefacturaPdf"
            />
            <Button
              label="Timbrar" icon="pi pi-verified" class="p-button-success timbrar-btn"
              :disabled="!listoParaTimbrar" :loading="timbrando" @click="confirmarTimbrar"
            />
          </div>
        </template>
      </div>

      <!-- ═══ Timbrando (reservada, PAC en curso) ═══ -->
      <div v-else-if="item.status === 'Timbrando'" class="timbrado-card">
        <h3><i class="pi pi-spin pi-spinner" /> Timbrando…</h3>
        <p>Esta factura se está timbrando en este momento. Espera unos segundos y recarga la página.</p>
      </div>

      <!-- ═══ Ya timbrada / cancelada ═══ -->
      <div v-else class="timbrado-card">
        <h3><i class="pi pi-receipt" /> Datos del CFDI</h3>
        <div class="detalle-row"><strong>UUID:</strong> {{ item.cfdi_uuid || '-' }}</div>
        <div class="detalle-row"><strong>RFC cliente:</strong> {{ item.rfc_cliente || '-' }}</div>
        <div class="detalle-row"><strong>Fecha certificación:</strong> {{ item.cfdi_fecha_certificacion || '-' }}</div>
        <div v-if="item.timbrado_por" class="detalle-row"><strong>Timbrada por:</strong> {{ item.timbrado_por }}</div>
        <div v-if="item.status === 'Cancelado'" class="detalle-row"><strong>Motivo cancelación:</strong> {{ item.cfdi_cancelacion_motivo || '-' }}</div>
        <div v-if="item.status === 'Cancelado' && item.cancelado_por" class="detalle-row"><strong>Cancelada por:</strong> {{ item.cancelado_por }}</div>
        <div v-if="item.status === 'Cancelado'" class="detalle-row">
          <strong>Estatus ante el SAT:</strong>
          <span :class="'badge badge-' + estatusCancelacionBadge(item.cfdi_cancelacion_estatus)" style="margin-left:0.5rem;">
            {{ estatusCancelacionTexto(item.cfdi_cancelacion_estatus) }}
          </span>
        </div>
        <div v-if="item.cfdi_uuid" style="display:flex;gap:0.5rem;margin-top:0.75rem;flex-wrap:wrap;">
          <Button icon="pi pi-file" label="XML" class="p-button-sm p-button-outlined" @click="abrirArchivoCfdi(item.cfdi_xml_path)" />
          <Button icon="pi pi-file-pdf" label="PDF" class="p-button-sm p-button-outlined" @click="abrirArchivoCfdi(item.cfdi_pdf_path)" />
          <Button v-if="item.status === 'Timbrado'" icon="pi pi-send" label="Enviar por correo" class="p-button-sm p-button-outlined" @click="abrirEnviarDialog" />
        </div>

        <div v-if="item.status === 'Cancelado'" class="acuse-section">
          <h4><i class="pi pi-verified" /> Acuse de cancelación</h4>
          <div style="display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center;">
            <Button
              icon="pi pi-refresh" label="Verificar estatus" class="p-button-sm p-button-outlined"
              :loading="verificandoCancelacion" @click="verificarCancelacion"
            />
            <Button
              v-if="item.cfdi_acuse_cancelacion_xml_path" icon="pi pi-file" label="Acuse XML"
              class="p-button-sm p-button-outlined" @click="abrirArchivoCfdi(item.cfdi_acuse_cancelacion_xml_path)"
            />
            <Button
              v-if="item.cfdi_acuse_cancelacion_pdf_path" icon="pi pi-file-pdf" label="Acuse PDF"
              class="p-button-sm p-button-outlined" @click="abrirArchivoCfdi(item.cfdi_acuse_cancelacion_pdf_path)"
            />
            <small v-if="!item.cfdi_acuse_cancelacion_xml_path && !item.cfdi_acuse_cancelacion_pdf_path" style="color:var(--color-border);">
              Aún no disponible — el SAT puede tardar en aceptar la cancelación. Usa "Verificar estatus".
            </small>
          </div>
        </div>

        <!-- ═══ Complementos de pago (REP) — solo facturas PPD ya timbradas ═══ -->
        <div v-if="esPPD && item.status === 'Timbrado'" class="rep-section">
          <h4><i class="pi pi-wallet" /> Complementos de pago (REP)</h4>
          <div class="rep-saldo-banner" :class="{ 'rep-saldo-liquidado': saldoPendientePpd <= 0.01 }">
            <span>Pagado: <strong>{{ formatTotal(totalPagadoPpd) }}</strong> de {{ formatTotal(item.total) }}</span>
            <span v-if="saldoPendientePpd > 0.01">Saldo pendiente: <strong>{{ formatTotal(saldoPendientePpd) }}</strong></span>
            <span v-else><i class="pi pi-check-circle" /> Liquidada</span>
            <Button
              v-if="saldoPendientePpd > 0.01" label="Registrar pago" icon="pi pi-plus"
              class="p-button-sm p-button-success" @click="abrirRegistrarPagoDialog"
            />
          </div>

          <div v-if="cargandoPagosPpd" style="text-align:center;padding:1rem;"><i class="pi pi-spin pi-spinner" /></div>
          <div v-else-if="!pagosPpd.length" class="rep-empty">Sin complementos de pago registrados todavía.</div>
          <DataTable v-else :value="pagosPpd" size="small" responsiveLayout="scroll">
            <Column header="#"><template #body="{ data }">{{ data.parcialidad }}</template></Column>
            <Column header="Fecha"><template #body="{ data }">{{ formatFecha(data.fecha_pago) }}</template></Column>
            <Column header="Forma de pago"><template #body="{ data }">{{ labelFormaPago(data.forma_pago) }}</template></Column>
            <Column header="Monto"><template #body="{ data }">{{ formatTotal(data.monto) }}</template></Column>
            <Column header="Saldo tras pago"><template #body="{ data }">{{ formatTotal(data.saldo_insoluto) }}</template></Column>
            <Column header="Estatus">
              <template #body="{ data }">
                <span :class="'badge badge-' + repBadgeClass(data.status)">{{ data.status }}</span>
                <span v-if="data.status === 'Cancelado'" :class="'badge badge-' + estatusCancelacionBadge(data.cfdi_cancelacion_estatus)" style="margin-left:0.35rem;">
                  {{ estatusCancelacionTexto(data.cfdi_cancelacion_estatus) }}
                </span>
                <i
                  v-if="data.status === 'Error' && data.ultimo_error_timbrado"
                  class="pi pi-exclamation-triangle timbrado-error-icono"
                  :title="data.ultimo_error_timbrado"
                ></i>
              </template>
            </Column>
            <Column header="Acciones">
              <template #body="{ data }">
                <div style="display:flex;gap:0.4rem;flex-wrap:wrap;align-items:center;">
                  <template v-if="data.status === 'Timbrado'">
                    <Button icon="pi pi-file" class="p-button-sm p-button-text" title="XML" @click="abrirArchivoCfdi(data.cfdi_xml_path)" />
                    <Button icon="pi pi-file-pdf" class="p-button-sm p-button-text" title="PDF" @click="abrirArchivoCfdi(data.cfdi_pdf_path)" />
                    <Button icon="pi pi-ban" class="p-button-sm p-button-text p-button-danger" title="Cancelar" @click="abrirCancelarPagoDialog(data)" />
                  </template>
                  <template v-else-if="data.status === 'Error'">
                    <Button label="Reintentar" icon="pi pi-refresh" class="p-button-sm p-button-text" @click="reintentarPagoConError(data)" />
                  </template>
                  <template v-else-if="data.status === 'Cancelado'">
                    <Button
                      icon="pi pi-refresh" class="p-button-sm p-button-text" title="Verificar estatus"
                      :loading="verificandoCancelacionPago === data.id" @click="verificarCancelacionPago(data)"
                    />
                    <Button v-if="data.cfdi_acuse_cancelacion_xml_path" icon="pi pi-file" class="p-button-sm p-button-text" title="Acuse XML" @click="abrirArchivoCfdi(data.cfdi_acuse_cancelacion_xml_path)" />
                    <Button v-if="data.cfdi_acuse_cancelacion_pdf_path" icon="pi pi-file-pdf" class="p-button-sm p-button-text" title="Acuse PDF" @click="abrirArchivoCfdi(data.cfdi_acuse_cancelacion_pdf_path)" />
                    <small v-if="!data.cfdi_acuse_cancelacion_xml_path && !data.cfdi_acuse_cancelacion_pdf_path" style="color:var(--color-border);">Sin acuse aún</small>
                  </template>
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>

      <Dialog v-model:visible="prefacturaPdfVisible" header="Prefactura (borrador sin timbrar)" :modal="true" :style="{ width: '85vw' }" :draggable="false">
        <iframe v-if="prefacturaPdfUrl" :src="prefacturaPdfUrl" style="width:100%;height:80vh;border:none;" />
      </Dialog>

      <!-- Dialog: registrar complemento de pago (REP) -->
      <Dialog v-model:visible="registrarPagoDialogVisible" header="Registrar pago (complemento REP)" :modal="true" :style="{ width: '480px', maxWidth: '95vw' }" :draggable="false">
        <div class="timbrar-form">
          <p style="margin:0;color:var(--color-text);opacity:0.8;font-size:0.88rem;">
            Saldo pendiente: <strong>{{ formatTotal(saldoPendientePpd) }}</strong>
          </p>
          <div class="fiscal-field">
            <label>Fecha de pago</label>
            <Calendar v-model="nuevoPago.fecha_pago" dateFormat="yy-mm-dd" showIcon class="w-full" />
          </div>
          <div class="fiscal-field">
            <label>Forma de pago</label>
            <Dropdown v-model="nuevoPago.forma_pago" :options="formasPagoCatalogo" optionLabel="label" optionValue="value" placeholder="Selecciona..." class="w-full" />
          </div>
          <div class="fiscal-field">
            <label>Monto</label>
            <InputNumber v-model="nuevoPago.monto" mode="currency" currency="MXN" locale="es-MX" :max="saldoPendientePpd" class="w-full" />
          </div>
          <div class="fiscal-field">
            <label>Número de operación (opcional)</label>
            <InputText v-model="nuevoPago.numero_operacion" class="w-full" />
          </div>
        </div>
        <div style="display:flex;justify-content:flex-end;gap:0.75rem;margin-top:1.25rem;">
          <Button label="Cancelar" class="p-button-text" @click="registrarPagoDialogVisible = false" />
          <Button
            label="Registrar y timbrar" icon="pi pi-verified" class="p-button-success"
            :disabled="!pagoListoParaRegistrar" :loading="registrandoPago" @click="confirmarRegistrarPago"
          />
        </div>
      </Dialog>

      <!-- Dialog: cancelar complemento de pago (REP) -->
      <Dialog v-model:visible="cancelarPagoDialogVisible" header="Cancelar complemento de pago" :modal="true" :style="{ width: '480px', maxWidth: '95vw' }" :draggable="false">
        <div class="timbrar-form">
          <div class="fiscal-field">
            <label>Motivo de cancelación</label>
            <Dropdown v-model="cancelarPagoForm.motivo" :options="motivosCancelacion" optionLabel="label" optionValue="value" placeholder="Selecciona un motivo" class="w-full" />
          </div>
          <div class="fiscal-field" v-if="cancelarPagoForm.motivo === '01'">
            <label>UUID del complemento de pago que sustituye</label>
            <InputText v-model="cancelarPagoForm.folio_sustitucion" class="w-full" />
          </div>
          <small style="color:var(--color-border);">Esto cancela el CFDI de pago ante el SAT. No se puede deshacer.</small>
        </div>
        <div style="display:flex;justify-content:flex-end;gap:0.75rem;margin-top:1.25rem;">
          <Button label="Cerrar" class="p-button-text" @click="cancelarPagoDialogVisible = false" />
          <Button label="Cancelar pago" icon="pi pi-ban" class="p-button-danger" :disabled="!cancelarPagoForm.motivo || (cancelarPagoForm.motivo === '01' && !cancelarPagoForm.folio_sustitucion)" :loading="cancelandoPago" @click="confirmarCancelarPago" />
        </div>
      </Dialog>

      <!-- Comprobantes de pago -->
      <div class="comprobante-section">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
          <h3 style="margin:0;">Comprobantes de pago</h3>
          <Button
            v-if="item.reporte_ids && item.reporte_ids.length"
            label="Sincronizar de reportes" icon="pi pi-sync"
            class="p-button-sm p-button-outlined"
            :loading="sincronizandoComprobantes" @click="sincronizarComprobantes"
          />
        </div>
        <div v-if="item.comprobantes && item.comprobantes.length" class="comprobantes-lista">
          <div v-for="(comp, idx) in item.comprobantes" :key="idx" class="comprobante-item">
            <i class="pi pi-file" style="color:var(--color-primary);margin-right:0.5rem;"></i>
            <a :href="urlComprobante(comp)" target="_blank" rel="noopener noreferrer" style="color:var(--color-primary);font-weight:bold;flex:1;">{{ nombreArchivo(comp) }}</a>
            <Button icon="pi pi-trash" class="p-button-text p-button-danger p-button-sm" :loading="eliminandoComprobante === comp" @click="eliminarComprobanteFile(comp)" />
          </div>
        </div>
        <div v-else style="color:var(--color-border);margin-bottom:0.75rem;">No se han cargado comprobantes aún.</div>
        <div>
          <input type="file" @change="onFileChange" accept="application/pdf,image/*" />
          <Button label="Subir comprobante" icon="pi pi-upload" class="p-button-success mt-2" :disabled="!archivoSeleccionado" :loading="subiendo" @click="subirComprobanteFile" />
        </div>
      </div>

      <!-- Observaciones -->
      <div class="observaciones-section">
        <h3>Observaciones</h3>
        <Textarea v-model="observacionesTexto" rows="3" class="w-full" style="width:100%;resize:vertical;" />
        <Button label="Guardar observaciones" icon="pi pi-save" class="p-button-secondary mt-2" :loading="guardandoObs" :disabled="observacionesTexto === (item.observaciones || '')" @click="guardarObservaciones" />
      </div>

      <!-- Órdenes incluidas -->
      <div v-if="item.detalle_ordenes && item.detalle_ordenes.length" class="ordenes-detalle">
        <h3>Órdenes incluidas</h3>
        <DataTable :value="item.detalle_ordenes" responsiveLayout="scroll">
          <Column field="folio" header="Orden" />
          <Column field="tipo_servicio" header="Tipo" />
          <Column field="nombre_cliente" header="Cliente" />
          <Column field="total" header="Total">
            <template #body="{ data }">{{ formatTotal(data.total) }}</template>
          </Column>
        </DataTable>
      </div>
    </div>

    <div v-else style="text-align:center;padding:3rem;"><p>No se encontró la factura.</p></div>

    <!-- Dialog: reportes de servicio -->
    <Dialog v-model:visible="reportesDialogVisible" :header="`Reportes de Servicio (${reportesList.length})`" :modal="true" :style="{ width: '750px', maxWidth: '95vw' }" :draggable="false">
      <div v-if="!reportesList.length" style="text-align:center;padding:1rem;color:var(--color-border);">Sin reportes cargados.</div>
      <DataTable v-else :value="reportesList" responsiveLayout="scroll">
        <Column header="Folio"><template #body="{ data }">{{ data.folio || `SERVICIO-${String(data.id).padStart(5, '0')}` }}</template></Column>
        <Column field="tipo_servicio" header="Tipo de Servicio" />
        <Column field="nombre_cliente" header="Cliente" />
        <Column header="Fecha"><template #body="{ data }">{{ formatFecha(data.fecha) }}</template></Column>
        <Column header="Acciones">
          <template #body="{ data }">
            <div style="display:flex;gap:0.5rem;">
              <Button icon="pi pi-file-pdf" label="Ver PDF" class="p-button-sm p-button-warning" :loading="loadingPdf" @click="verPDF(data)" />
              <Button v-if="esEditable" icon="pi pi-times" label="Quitar" class="p-button-sm p-button-danger p-button-outlined" :loading="quitando === data.id" @click="quitarReporte(data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </Dialog>

    <Dialog v-model:visible="pdfDialogVisible" :header="pdfTitle" :modal="true" :style="{ width: '85vw' }" :draggable="false" @hide="cerrarPdfDialog">
      <iframe v-if="pdfUrl" :src="pdfUrl" style="width:100%;height:80vh;border:none;" />
    </Dialog>

    <!-- Dialog: agregar servicios -->
    <Dialog v-model:visible="agregarDialogVisible" :header="`Agregar servicios a Factura #${item?.id}`" :modal="true" :style="{ width: '75vw' }" :draggable="false">
      <div v-if="loadingDisponibles" style="text-align:center;padding:2rem;"><i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i></div>
      <template v-else>
        <div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-bottom:1rem;">
          <InputText v-model="filtroAgregarFolio" placeholder="Buscar por folio / OS" style="flex:1;min-width:150px;" />
          <InputText v-model="filtroAgregarCliente" placeholder="Buscar por cliente" style="flex:1;min-width:150px;" />
        </div>
        <p v-if="!reportesDisponiblesFiltrados.length" style="text-align:center;color:var(--color-border);">
          {{ reportesDisponibles.length ? 'Sin resultados.' : 'No hay reportes disponibles.' }}
        </p>
        <DataTable v-else v-model:selection="reportesSeleccionados" :value="reportesDisponiblesFiltrados" dataKey="id" :paginator="reportesDisponiblesFiltrados.length > 10" :rows="10" selectionMode="multiple" size="small">
          <Column selectionMode="multiple" style="width:3rem" />
          <Column field="folio" header="Folio" />
          <Column field="tipo_servicio" header="Tipo" />
          <Column field="nombre_cliente" header="Cliente" />
          <Column field="total" header="Total"><template #body="{ data }">{{ formatTotal(data.total) }}</template></Column>
        </DataTable>
        <div style="display:flex;justify-content:flex-end;gap:0.75rem;margin-top:1.25rem;">
          <Button label="Cancelar" class="p-button-text" @click="agregarDialogVisible = false" />
          <Button label="Agregar seleccionados" icon="pi pi-check" class="p-button-success" :disabled="!reportesSeleccionados.length" :loading="agregando" @click="confirmarAgregar" />
        </div>
      </template>
    </Dialog>

    <!-- Dialog: cancelar factura -->
    <Dialog v-model:visible="cancelarDialogVisible" header="Cancelar factura (CFDI)" :modal="true" :style="{ width: '480px', maxWidth: '95vw' }" :draggable="false">
      <div class="timbrar-form">
        <div class="fiscal-field">
          <label>Motivo de cancelación</label>
          <Dropdown v-model="cancelarForm.motivo" :options="motivosCancelacion" optionLabel="label" optionValue="value" placeholder="Selecciona un motivo" class="w-full" />
        </div>
        <div class="fiscal-field" v-if="cancelarForm.motivo === '01'">
          <label>UUID de la factura que sustituye</label>
          <InputText v-model="cancelarForm.folio_sustitucion" class="w-full" />
        </div>
        <small style="color:var(--color-border);">Esto cancela el CFDI ante el SAT. No se puede deshacer.</small>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:0.75rem;margin-top:1.25rem;">
        <Button label="Cerrar" class="p-button-text" @click="cancelarDialogVisible = false" />
        <Button label="Cancelar factura" icon="pi pi-ban" class="p-button-danger" :disabled="!cancelarForm.motivo || (cancelarForm.motivo === '01' && !cancelarForm.folio_sustitucion)" :loading="cancelando" @click="confirmarCancelar" />
      </div>
    </Dialog>

    <!-- Dialog: enviar CFDI por correo -->
    <Dialog v-model:visible="enviarDialogVisible" header="Enviar CFDI por correo" :modal="true" :style="{ width: '420px', maxWidth: '95vw' }" :draggable="false">
      <div class="fiscal-field">
        <label>Correo del destinatario</label>
        <InputText v-model="correoEnvio" placeholder="cliente@correo.com" class="w-full" :class="{ 'p-invalid': correoEnvio && !correoEnvioValido }" />
        <small v-if="correoEnvio && !correoEnvioValido" class="fiscal-error">Correo con formato inválido</small>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:0.75rem;margin-top:1.25rem;">
        <Button label="Cancelar" class="p-button-text" @click="enviarDialogVisible = false" />
        <Button label="Enviar" icon="pi pi-send" class="p-button-success" :disabled="!correoEnvioValido" :loading="enviando" @click="confirmarEnviar" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Calendar from 'primevue/calendar';
import Textarea from 'primevue/textarea';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import {
  getFacturaById, actualizarLugarPagoFactura, actualizarObservacionesFactura,
  subirComprobanteFactura, eliminarComprobanteFactura, sincronizarComprobantesFactura,
  agregarReportesFactura, quitarReportesFactura,
  timbrarFactura, cancelarFactura, verificarCancelacionFactura, enviarCfdiFactura, getNotas, getFacturas,
  actualizarPagadoFactura,
  generarPrefacturaFactura, getPrefacturaPdfUrl,
  getPagosPpd, registrarPagoPpd, cancelarPagoPpd, verificarCancelacionPagoPpd,
} from '@/services/pagosService';
import { getClientes, addCliente, updateCliente } from '@/services/clientesService';
import { generarReporteServicioPDF } from '@/components/GeneraReporteServicioPDF.js';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const loginStore = useLoginStore();

const id = computed(() => route.params.id);
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');

const item = ref(null);
const loading = ref(false);
const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

const formatoMoneda = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2 });
function formatTotal(v) { return v != null ? formatoMoneda.format(Number(v)) : '-'; }
function formatFecha(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}
function badgeClass(status) {
  if (status === 'Timbrado') return 'success';
  if (status === 'Cancelado') return 'danger';
  return 'warning'; // Pendiente timbre / Timbrando
}
function urlComprobante(path) {
  if (!path) return '';
  const p = path.startsWith('/') ? path : `/${path}`;
  const encoded = p.split('/').map(seg => encodeURIComponent(seg)).join('/');
  return `${API_URL}${encoded}`;
}
function nombreArchivo(path) { return path ? path.split('/').pop() : 'comprobante'; }
function abrirArchivoCfdi(path) { if (path) window.open(urlComprobante(path), '_blank', 'noopener'); }

const esEditable = computed(() => item.value?.status === 'Pendiente timbre' && !item.value?.facturapi_draft_id);

const PALABRAS_ERROR_CSD = ['certificado', 'csd', 'vigen', 'caduc', 'sello', 'expired', 'expir'];
function pareceErrorDeCsd(mensaje) {
  const m = (mensaje || '').toLowerCase();
  return PALABRAS_ERROR_CSD.some(p => m.includes(p));
}

const lugaresDisponibles = ['ASP Vianey', 'ASP Renovaciones', 'Comercializadora', 'BBVA PAU', 'Mercadopago Victor', 'Mercadopago Eliseo', 'Efectivo oficina', 'Efectivo tecnico'];
const lugarPagoSeleccionado = ref(null);
async function guardarLugarPago() {
  try {
    await actualizarLugarPagoFactura(id.value, lugarPagoSeleccionado.value || '');
    item.value.lugar_pago = lugarPagoSeleccionado.value;
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Lugar de pago actualizado.', life: 2500 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar.', life: 4000 });
  }
}

const guardandoPagado = ref(false);
async function togglePagado() {
  const nuevoValor = !item.value.pagado;
  guardandoPagado.value = true;
  try {
    await actualizarPagadoFactura(id.value, nuevoValor);
    item.value.pagado = nuevoValor;
    toast.add({ severity: 'success', summary: 'Guardado', detail: nuevoValor ? 'Factura marcada como pagada.' : 'Factura marcada como pendiente de pago.', life: 2500 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el estatus de pago.', life: 4000 });
  }
  guardandoPagado.value = false;
}

// ── Timbrado: datos fiscales del cliente ──
const REGIMENES_FISCALES = [
  { label: '601 - General de Ley Personas Morales', value: '601' },
  { label: '603 - Personas Morales con Fines no Lucrativos', value: '603' },
  { label: '605 - Sueldos y Salarios', value: '605' },
  { label: '606 - Arrendamiento', value: '606' },
  { label: '608 - Demás ingresos', value: '608' },
  { label: '612 - Personas Físicas con Actividades Empresariales', value: '612' },
  { label: '616 - Sin obligaciones fiscales', value: '616' },
  { label: '621 - Incorporación Fiscal', value: '621' },
  { label: '626 - Régimen Simplificado de Confianza (RESICO)', value: '626' },
];
// Catálogo SAT c_UsoCFDI (CFDI 4.0) — los D01-D10 (deducciones personales)
// solo aplican a régimen de persona física; el resto aplica a cualquier régimen.
const USOS_CFDI_CATALOGO = [
  { label: 'G01 - Adquisición de mercancías', value: 'G01' },
  { label: 'G02 - Devoluciones, descuentos o bonificaciones', value: 'G02' },
  { label: 'G03 - Gastos en general', value: 'G03' },
  { label: 'I01 - Construcciones', value: 'I01' },
  { label: 'I02 - Mobiliario y equipo de oficina por inversiones', value: 'I02' },
  { label: 'I03 - Equipo de transporte', value: 'I03' },
  { label: 'I04 - Equipo de computo y accesorios', value: 'I04' },
  { label: 'I08 - Otra maquinaria y equipo', value: 'I08' },
  { label: 'D01 - Honorarios médicos, dentales y gastos hospitalarios', value: 'D01', personaFisica: true },
  { label: 'D02 - Gastos médicos por incapacidad o discapacidad', value: 'D02', personaFisica: true },
  { label: 'D03 - Gastos funerales', value: 'D03', personaFisica: true },
  { label: 'D04 - Donativos', value: 'D04', personaFisica: true },
  { label: 'D10 - Pagos por servicios educativos (colegiaturas)', value: 'D10', personaFisica: true },
  { label: 'S01 - Sin efectos fiscales', value: 'S01' },
  { label: 'P01 - Por definir', value: 'P01' },
];
const REGIMENES_PERSONA_FISICA = new Set(['605', '606', '608', '612', '616', '621', '626']);

const formasPagoCatalogo = [
  { label: '01 - Efectivo', value: '01' },
  { label: '02 - Cheque nominativo', value: '02' },
  { label: '03 - Transferencia electrónica de fondos', value: '03' },
  { label: '04 - Tarjeta de crédito', value: '04' },
  { label: '28 - Tarjeta de débito', value: '28' },
  { label: '99 - Por definir', value: '99' }, // el SAT solo la permite con MétodoPago PPD
];
const RFC_REGEX = /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/i;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const RFC_PUBLICO_GENERAL = 'XAXX010101000';

const clientesCache = ref([]);
const clienteFiscal = ref(null);
const clienteExiste = computed(() => !!clienteFiscal.value?.id);
const cargandoCliente = ref(false);
const editandoFiscal = ref(false);
const guardandoFiscal = ref(false);
const fiscalForm = ref({ rfc: '', codigo_postal: '', regimen_fiscal: '', correo: '' });

const rfcValido = computed(() => RFC_REGEX.test((fiscalForm.value.rfc || '').trim()));
const correoValido = computed(() => EMAIL_REGEX.test((fiscalForm.value.correo || '').trim()));

// Venta a público en general: el backend fuerza RFC genérico + UsoCFDI S01 +
// régimen/domicilio del propio emisor sin importar lo que se mande — así que
// aquí no tiene sentido exigir datos fiscales del cliente ni dejarlo elegir uso CFDI.
const publicoGeneral = ref(false);

const datosFiscalesCompletos = computed(() =>
  publicoGeneral.value ||
  !!(clienteFiscal.value?.rfc && clienteFiscal.value?.codigo_postal && clienteFiscal.value?.regimen_fiscal
    && clienteFiscal.value?.correo && EMAIL_REGEX.test(clienteFiscal.value.correo))
);

const regimenReceptorActivo = computed(() => publicoGeneral.value ? '616' : (clienteFiscal.value?.regimen_fiscal || ''));

const USOS_CFDI = computed(() => {
  const esFisica = REGIMENES_PERSONA_FISICA.has(regimenReceptorActivo.value);
  return USOS_CFDI_CATALOGO.filter(u => !u.personaFisica || esFisica);
});

const formasPago = computed(() =>
  formasPagoCatalogo.filter(f => f.value !== '99' || timbrarForm.value.metodo_pago === 'PPD')
);

async function cargarClienteFiscal() {
  cargandoCliente.value = true;
  try {
    clientesCache.value = await getClientes();
    // Prefiere la FK explícita (facturas creadas desde NuevaPrefactura.vue) —
    // el match por nombre queda como respaldo para facturas viejas.
    const match = item.value?.cliente_id
      ? clientesCache.value.find(c => c.id === item.value.cliente_id)
      : clientesCache.value.find(c => (c.nombre || '').trim().toLowerCase() === (item.value?.cliente || '').trim().toLowerCase());
    clienteFiscal.value = match || { nombre: item.value?.cliente || '' };
    fiscalForm.value = {
      rfc: clienteFiscal.value.rfc || '',
      codigo_postal: clienteFiscal.value.codigo_postal || '',
      regimen_fiscal: clienteFiscal.value.regimen_fiscal || '',
      correo: clienteFiscal.value.correo || '',
    };
    editandoFiscal.value = false;
  } catch {
    clienteFiscal.value = { nombre: item.value?.cliente || '' };
  }
  cargandoCliente.value = false;
}

async function guardarDatosFiscales() {
  if (!rfcValido.value || !fiscalForm.value.codigo_postal || !fiscalForm.value.regimen_fiscal || !correoValido.value) {
    toast.add({ severity: 'warn', summary: 'Faltan datos', detail: 'Completa RFC, código postal, régimen fiscal y un correo válido (es el único medio para entregarle el CFDI).', life: 4000 });
    return;
  }
  guardandoFiscal.value = true;
  try {
    const payload = {
      nombre: item.value.cliente, rfc: fiscalForm.value.rfc.toUpperCase(), codigo_postal: fiscalForm.value.codigo_postal,
      regimen_fiscal: fiscalForm.value.regimen_fiscal, correo: fiscalForm.value.correo.trim(),
    };
    if (clienteExiste.value) {
      await updateCliente(clienteFiscal.value.id, { ...clienteFiscal.value, ...payload });
    } else {
      await addCliente(payload);
    }
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Datos fiscales guardados.', life: 2500 });
    await cargarClienteFiscal();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo guardar.', life: 4000 });
  }
  guardandoFiscal.value = false;
}

// Sin valores por defecto a propósito: el usuario debe elegir uso CFDI,
// método y forma de pago para cada factura (ver aviso en el template) —
// nunca se debe asumir "lo de siempre" porque cambia según cómo pagó cada cliente.
const timbrarForm = ref({ uso_cfdi: null, forma_pago: null, metodo_pago: null });
const timbrando = ref(false);

// El SAT solo permite FormaPago '99' cuando MétodoPago es PPD — si el usuario
// cambia a PUE con '99' seleccionado, hay que corregirlo o el PAC rechaza el CFDI.
watch(() => timbrarForm.value.metodo_pago, (metodo) => {
  if (metodo !== 'PPD' && timbrarForm.value.forma_pago === '99') {
    timbrarForm.value.forma_pago = '03';
  }
});
// Público en general fuerza Uso CFDI S01 en el backend sin importar lo que se mande.
watch(publicoGeneral, (activo) => {
  if (activo) timbrarForm.value.uso_cfdi = 'S01';
});

const datosFiscalesListos = computed(() => {
  if (!(!!timbrarForm.value.uso_cfdi && !!timbrarForm.value.forma_pago && !!timbrarForm.value.metodo_pago)) return false;
  if (publicoGeneral.value) return true;
  return datosFiscalesCompletos.value && RFC_REGEX.test(clienteFiscal.value?.rfc || '');
});

const listoParaTimbrar = computed(() => datosFiscalesListos.value);

const camposFaltantes = computed(() => {
  const faltan = [];
  if (!publicoGeneral.value && !timbrarForm.value.uso_cfdi) faltan.push('Uso CFDI');
  if (!timbrarForm.value.metodo_pago) faltan.push('Método de pago');
  if (!timbrarForm.value.forma_pago) faltan.push('Forma de pago');
  if (!publicoGeneral.value && !(datosFiscalesCompletos.value && RFC_REGEX.test(clienteFiscal.value?.rfc || ''))) {
    faltan.push('datos fiscales del cliente (RFC/CP/régimen/correo)');
  }
  return faltan;
});

function datosFiscalesPayload() {
  return publicoGeneral.value ? {
    rfc_cliente: RFC_PUBLICO_GENERAL,
    uso_cfdi: 'S01',
    forma_pago: timbrarForm.value.forma_pago,
    metodo_pago: timbrarForm.value.metodo_pago,
  } : {
    rfc_cliente: clienteFiscal.value.rfc,
    uso_cfdi: timbrarForm.value.uso_cfdi,
    forma_pago: timbrarForm.value.forma_pago,
    metodo_pago: timbrarForm.value.metodo_pago,
    domicilio_fiscal_receptor: clienteFiscal.value.codigo_postal,
    regimen_fiscal_receptor: clienteFiscal.value.regimen_fiscal,
  };
}

async function confirmarTimbrar() {
  timbrando.value = true;
  try {
    await timbrarFactura(id.value, datosFiscalesPayload());
    toast.add({ severity: 'success', summary: 'Timbrada', detail: 'CFDI generado y timbrado correctamente.', life: 4000 });
    await cargarDetalle();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error al timbrar', detail: e?.response?.data?.detail || 'No se pudo timbrar la factura.', life: 6000 });
  }
  timbrando.value = false;
}

const generandoPrefactura = ref(false);
async function generarPrefactura() {
  generandoPrefactura.value = true;
  try {
    await generarPrefacturaFactura(id.value, datosFiscalesPayload());
    await cargarDetalle();
    toast.add({ severity: 'success', summary: 'Prefactura generada', detail: 'Ya puedes ver el PDF del borrador antes de timbrar.', life: 4000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo generar la prefactura.', life: 5000 });
  }
  generandoPrefactura.value = false;
}

const prefacturaPdfVisible = ref(false);
const prefacturaPdfUrl = ref('');
async function verPrefacturaPdf() {
  prefacturaPdfUrl.value = await getPrefacturaPdfUrl(id.value);
  prefacturaPdfVisible.value = true;
}

// ── Comprobantes ──
const archivoSeleccionado = ref(null);
const subiendo = ref(false);
const eliminandoComprobante = ref(null);
function onFileChange(e) {
  const files = e?.target?.files;
  archivoSeleccionado.value = files && files.length ? files[0] : null;
}
async function subirComprobanteFile() {
  if (!archivoSeleccionado.value) return;
  subiendo.value = true;
  try {
    await subirComprobanteFactura(id.value, archivoSeleccionado.value);
    toast.add({ severity: 'success', summary: 'Subido', detail: 'Comprobante cargado.', life: 3000 });
    archivoSeleccionado.value = null;
    await cargarDetalle();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo subir el comprobante.', life: 4000 });
  }
  subiendo.value = false;
}
async function eliminarComprobanteFile(path) {
  eliminandoComprobante.value = path;
  try {
    await eliminarComprobanteFactura(id.value, path);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Comprobante eliminado.', life: 3000 });
    await cargarDetalle();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar.', life: 4000 });
  }
  eliminandoComprobante.value = null;
}

const sincronizandoComprobantes = ref(false);
async function sincronizarComprobantes() {
  sincronizandoComprobantes.value = true;
  try {
    const res = await sincronizarComprobantesFactura(id.value);
    if (res.agregados > 0) {
      toast.add({ severity: 'success', summary: 'Sincronizado', detail: `Se agregaron ${res.agregados} comprobante(s) de los reportes ligados.`, life: 4000 });
    } else {
      toast.add({ severity: 'info', summary: 'Sin novedades', detail: 'No hay comprobantes nuevos en los reportes ligados.', life: 3500 });
    }
    await cargarDetalle();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo sincronizar.', life: 4000 });
  }
  sincronizandoComprobantes.value = false;
}

// ── Observaciones ──
const observacionesTexto = ref('');
const guardandoObs = ref(false);
async function guardarObservaciones() {
  guardandoObs.value = true;
  try {
    await actualizarObservacionesFactura(id.value, observacionesTexto.value);
    item.value.observaciones = observacionesTexto.value;
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Observaciones guardadas.', life: 2500 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron guardar.', life: 4000 });
  }
  guardandoObs.value = false;
}

// ── Reportes de servicio ──
const reportesDialogVisible = ref(false);
const pdfDialogVisible = ref(false);
const reportesList = ref([]);
const loadingReportes = ref(false);
const pdfUrl = ref('');
const pdfTitle = ref('');
const loadingPdf = ref(false);
const quitando = ref(null);

async function abrirReportesDialog() {
  if (!item.value?.reporte_ids?.length) return;
  loadingReportes.value = true;
  try {
    const results = await Promise.all(item.value.reporte_ids.map(rid => axios.get(`${API_URL}/reportes-servicio/${rid}`).then(r => r.data)));
    reportesList.value = results;
    reportesDialogVisible.value = true;
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los reportes.', life: 4000 });
  }
  loadingReportes.value = false;
}

async function verPDF(reporte) {
  loadingPdf.value = true;
  try {
    const resp = await axios.get(`${API_URL}/reportes-servicio/${reporte.id}`);
    const merged = { ...reporte, ...resp.data };
    const url = await generarReporteServicioPDF({ reporte: merged, mode: 'bloburl' });
    if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value);
    pdfUrl.value = url;
    pdfTitle.value = merged.folio || `Reporte #${merged.id}`;
    pdfDialogVisible.value = true;
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo generar el PDF.', life: 4000 });
  }
  loadingPdf.value = false;
}
function cerrarPdfDialog() {
  pdfDialogVisible.value = false;
  if (pdfUrl.value) { URL.revokeObjectURL(pdfUrl.value); pdfUrl.value = ''; }
}
async function quitarReporte(reporte) {
  quitando.value = reporte.id;
  try {
    await quitarReportesFactura(id.value, [reporte.id]);
    reportesList.value = reportesList.value.filter(r => r.id !== reporte.id);
    if (!reportesList.value.length) reportesDialogVisible.value = false;
    await cargarDetalle();
    toast.add({ severity: 'success', summary: 'Quitado', detail: `Reporte quitado.`, life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo quitar.', life: 4000 });
  }
  quitando.value = null;
}

// ── Agregar servicios ──
const agregarDialogVisible = ref(false);
const reportesDisponibles = ref([]);
const loadingDisponibles = ref(false);
const reportesSeleccionados = ref([]);
const agregando = ref(false);
const filtroAgregarCliente = ref('');
const filtroAgregarFolio = ref('');

const reportesDisponiblesFiltrados = computed(() => reportesDisponibles.value.filter(r => {
  const cliente = filtroAgregarCliente.value.trim().toLowerCase();
  const folio = filtroAgregarFolio.value.trim().toLowerCase();
  if (cliente && !(r.nombre_cliente || '').toLowerCase().includes(cliente)) return false;
  if (folio && !(r.folio || '').toLowerCase().includes(folio)) return false;
  return true;
}));

async function abrirAgregarDialog() {
  loadingDisponibles.value = true;
  agregarDialogVisible.value = true;
  try {
    const [todosReportes, notas, facturas] = await Promise.all([
      axios.get(`${API_URL}/reportes-servicio-todos`).then(r => r.data),
      getNotas(), getFacturas(),
    ]);
    const asignados = new Set();
    const currentIds = new Set(item.value?.reporte_ids || []);
    for (const n of notas) for (const rid of (n.reporte_ids || [])) asignados.add(rid);
    for (const f of facturas) {
      if (f.id === Number(id.value)) continue;
      for (const rid of (f.reporte_ids || [])) asignados.add(rid);
    }
    reportesDisponibles.value = todosReportes.filter(r => !asignados.has(r.id) && !currentIds.has(r.id));
    reportesSeleccionados.value = [];
    filtroAgregarCliente.value = '';
    filtroAgregarFolio.value = '';
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
    await agregarReportesFactura(id.value, nuevos_ids);
    agregarDialogVisible.value = false;
    reportesSeleccionados.value = [];
    await cargarDetalle();
    toast.add({ severity: 'success', summary: 'Agregado', detail: `Se agregaron ${nuevos_ids.length} servicio(s).`, life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudieron agregar.', life: 4000 });
  }
  agregando.value = false;
}

// ── Cancelar factura ──
const cancelarDialogVisible = ref(false);
const cancelando = ref(false);
const cancelarForm = ref({ motivo: '', folio_sustitucion: '' });
const motivosCancelacion = [
  { label: '01 - Comprobante emitido con errores con relación', value: '01' },
  { label: '02 - Comprobante emitido con errores sin relación', value: '02' },
  { label: '03 - No se llevó a cabo la operación', value: '03' },
  { label: '04 - Operación nominativa en factura global', value: '04' },
];
function abrirCancelarDialog() {
  cancelarForm.value = { motivo: '', folio_sustitucion: '' };
  cancelarDialogVisible.value = true;
}
async function confirmarCancelar() {
  cancelando.value = true;
  try {
    await cancelarFactura(id.value, { ...cancelarForm.value });
    toast.add({ severity: 'success', summary: 'Cancelada', detail: 'CFDI cancelado ante el SAT.', life: 4000 });
    cancelarDialogVisible.value = false;
    await cargarDetalle();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo cancelar.', life: 5000 });
  }
  cancelando.value = false;
}

// ── Acuse de cancelación ──
const ESTATUS_CANCELACION = {
  accepted: { texto: 'Aceptada por el SAT', badge: 'success' },
  pending: { texto: 'Pendiente de aceptación', badge: 'warning' },
  verifying: { texto: 'En verificación por el SAT', badge: 'warning' },
  rejected: { texto: 'Rechazada por el SAT', badge: 'danger' },
};
function estatusCancelacionTexto(estatus) {
  if (!estatus) return 'Desconocido';
  return ESTATUS_CANCELACION[estatus]?.texto || estatus;
}
function estatusCancelacionBadge(estatus) {
  return ESTATUS_CANCELACION[estatus]?.badge || 'warning';
}

const verificandoCancelacion = ref(false);
async function verificarCancelacion() {
  verificandoCancelacion.value = true;
  try {
    const res = await verificarCancelacionFactura(id.value);
    await cargarDetalle();
    toast.add({
      severity: 'success', summary: 'Estatus actualizado',
      detail: `Estatus: ${estatusCancelacionTexto(res.estatus)}${res.acuse_xml_path || res.acuse_pdf_path ? ' — acuse disponible.' : ''}`,
      life: 4000
    });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo verificar el estatus.', life: 5000 });
  }
  verificandoCancelacion.value = false;
}

async function cargarDetalle() {
  loading.value = true;
  try {
    item.value = await getFacturaById(id.value);
    lugarPagoSeleccionado.value = item.value?.lugar_pago || null;
    observacionesTexto.value = item.value?.observaciones || '';
    if (item.value?.status === 'Pendiente timbre') await cargarClienteFiscal();
    if (esPPD.value && item.value?.status === 'Timbrado') await cargarPagosPpd();
  } catch {
    item.value = null;
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el detalle.', life: 4000 });
  }
  loading.value = false;
}

// ── Enviar CFDI por correo ──
const enviarDialogVisible = ref(false);
const enviando = ref(false);
const correoEnvio = ref('');
const correoEnvioValido = computed(() => EMAIL_REGEX.test((correoEnvio.value || '').trim()));

async function abrirEnviarDialog() {
  correoEnvio.value = '';
  try {
    const clientes = await getClientes();
    const match = clientes.find(c => (c.nombre || '').trim().toLowerCase() === (item.value?.cliente || '').trim().toLowerCase());
    correoEnvio.value = match?.correo || '';
  } catch {
    // sin bloquear el flujo si no se puede prellenar el correo
  }
  enviarDialogVisible.value = true;
}

async function confirmarEnviar() {
  if (!correoEnvioValido.value) return;
  enviando.value = true;
  try {
    await enviarCfdiFactura(id.value, correoEnvio.value.trim());
    toast.add({ severity: 'success', summary: 'Enviado', detail: 'CFDI enviado por correo.', life: 3000 });
    enviarDialogVisible.value = false;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo enviar el correo.', life: 5000 });
  }
  enviando.value = false;
}

// ── Complementos de pago (REP) — facturas PPD ──
const esPPD = computed(() => (item.value?.metodo_pago || '').toUpperCase() === 'PPD');
const pagosPpd = ref([]);
const cargandoPagosPpd = ref(false);

const totalPagadoPpd = computed(() =>
  pagosPpd.value.filter(p => p.status === 'Timbrado').reduce((sum, p) => sum + Number(p.monto || 0), 0)
);
const saldoPendientePpd = computed(() => Math.max(0, round2(Number(item.value?.total || 0) - totalPagadoPpd.value)));
// No se puede cancelar el CFDI de ingreso mientras existan complementos de
// pago (REP) timbrados apuntando a él — el backend lo rechaza igual.
const tieneRepsTimbrados = computed(() => pagosPpd.value.some(p => p.status === 'Timbrado'));
function round2(n) { return Math.round(n * 100) / 100; }

function labelFormaPago(codigo) {
  return formasPagoCatalogo.find(f => f.value === codigo)?.label || codigo;
}
function repBadgeClass(status) {
  if (status === 'Timbrado') return 'success';
  if (status === 'Error') return 'danger';
  if (status === 'Cancelado') return 'danger';
  return 'warning';
}

async function cargarPagosPpd() {
  cargandoPagosPpd.value = true;
  try {
    pagosPpd.value = await getPagosPpd(id.value);
  } catch {
    pagosPpd.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los complementos de pago.', life: 4000 });
  }
  cargandoPagosPpd.value = false;
}

const registrarPagoDialogVisible = ref(false);
const registrandoPago = ref(false);
const nuevoPago = ref({ fecha_pago: new Date(), forma_pago: null, monto: 0, numero_operacion: '' });

function abrirRegistrarPagoDialog() {
  nuevoPago.value = { fecha_pago: new Date(), forma_pago: null, monto: saldoPendientePpd.value, numero_operacion: '' };
  registrarPagoDialogVisible.value = true;
}

function reintentarPagoConError(pagoFallido) {
  nuevoPago.value = {
    fecha_pago: pagoFallido.fecha_pago ? new Date(pagoFallido.fecha_pago) : new Date(),
    forma_pago: pagoFallido.forma_pago || null,
    monto: Number(pagoFallido.monto) || saldoPendientePpd.value,
    numero_operacion: pagoFallido.numero_operacion || '',
  };
  registrarPagoDialogVisible.value = true;
}

const pagoListoParaRegistrar = computed(() =>
  !!nuevoPago.value.fecha_pago && !!nuevoPago.value.forma_pago && Number(nuevoPago.value.monto) > 0
  && Number(nuevoPago.value.monto) <= saldoPendientePpd.value + 0.01
);

function fechaISO(d) {
  const dt = (d instanceof Date) ? d : new Date(d);
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
}

async function confirmarRegistrarPago() {
  if (!pagoListoParaRegistrar.value) return;
  registrandoPago.value = true;
  try {
    const res = await registrarPagoPpd(id.value, {
      fecha_pago: fechaISO(nuevoPago.value.fecha_pago),
      forma_pago: nuevoPago.value.forma_pago,
      monto: Number(nuevoPago.value.monto),
      numero_operacion: nuevoPago.value.numero_operacion?.trim() || undefined,
    });
    toast.add({
      severity: 'success', summary: 'Complemento de pago timbrado',
      detail: res.factura_liquidada ? 'Factura liquidada — saldo en $0.' : `Saldo restante: ${formatTotal(res.saldo_insoluto)}.`,
      life: 4500
    });
    registrarPagoDialogVisible.value = false;
    await cargarPagosPpd();
    await cargarDetalle();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error al timbrar el pago', detail: e?.response?.data?.detail || 'No se pudo timbrar el complemento de pago.', life: 6000 });
    await cargarPagosPpd();
  }
  registrandoPago.value = false;
}

const cancelarPagoDialogVisible = ref(false);
const cancelandoPago = ref(false);
const cancelarPagoForm = ref({ motivo: '', folio_sustitucion: '' });
const pagoACancelar = ref(null);

function abrirCancelarPagoDialog(pago) {
  pagoACancelar.value = pago;
  cancelarPagoForm.value = { motivo: '', folio_sustitucion: '' };
  cancelarPagoDialogVisible.value = true;
}

async function confirmarCancelarPago() {
  if (!pagoACancelar.value || !cancelarPagoForm.value.motivo) return;
  if (cancelarPagoForm.value.motivo === '01' && !cancelarPagoForm.value.folio_sustitucion) return;
  cancelandoPago.value = true;
  try {
    await cancelarPagoPpd(id.value, pagoACancelar.value.id, cancelarPagoForm.value.motivo, cancelarPagoForm.value.folio_sustitucion);
    toast.add({ severity: 'success', summary: 'Cancelado', detail: 'Complemento de pago cancelado ante el SAT.', life: 4000 });
    cancelarPagoDialogVisible.value = false;
    await cargarPagosPpd();
    await cargarDetalle();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo cancelar el complemento de pago.', life: 5000 });
  }
  cancelandoPago.value = false;
}

const verificandoCancelacionPago = ref(null);
async function verificarCancelacionPago(pago) {
  verificandoCancelacionPago.value = pago.id;
  try {
    const res = await verificarCancelacionPagoPpd(id.value, pago.id);
    await cargarPagosPpd();
    toast.add({
      severity: 'success', summary: 'Estatus actualizado',
      detail: `Estatus: ${estatusCancelacionTexto(res.estatus)}${res.acuse_xml_path || res.acuse_pdf_path ? ' — acuse disponible.' : ''}`,
      life: 4000
    });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo verificar el estatus.', life: 5000 });
  }
  verificandoCancelacionPago.value = null;
}

onMounted(() => {
  if (!esAdmin.value) {
    router.replace('/');
    return;
  }
  cargarDetalle();
});
</script>

<style scoped>
.detalle-factura-container { margin: 2rem auto; padding: 2rem 1.5rem; max-width: 1100px; }
.mb-3 { margin-bottom: 1rem; }
.mt-2 { margin-top: 0.5rem; }
.w-full { width: 100%; }
.detalle-title { color: var(--color-title); }
.detalle-card { background: var(--color-card); border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0; border: 1px solid var(--color-border); }
.detalle-row { padding: 0.5rem 0; border-bottom: 1px solid var(--color-border); display: flex; align-items: center; gap: 0.5rem; }
.detalle-row:last-child { border-bottom: none; }
.lugar-pago-select { width: 220px; }
.badge { padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85rem; font-weight: bold; }
.badge-success { background: color-mix(in srgb, var(--color-success) 22%, transparent); color: var(--color-success); }
.badge-warning { background: color-mix(in srgb, var(--color-warning) 25%, transparent); color: var(--color-warning); }
.badge-danger  { background: color-mix(in srgb, var(--color-error) 20%, transparent); color: var(--color-error); }

.timbrado-card { background: var(--color-card); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid var(--color-border); }
.timbrado-card h3 { display: flex; align-items: center; gap: 0.5rem; margin: 0 0 1rem; color: var(--color-title); }
.fiscal-resumen { display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; padding: 0.9rem 1.1rem; border-radius: 10px; background: color-mix(in srgb, var(--color-success) 10%, transparent); border: 1px solid color-mix(in srgb, var(--color-success) 30%, transparent); margin-bottom: 1rem; }
.fiscal-resumen-item { display: flex; flex-direction: column; gap: 0.15rem; font-size: 0.85rem; color: var(--color-text); }
.fiscal-resumen-item strong { color: var(--color-title); font-size: 0.95rem; }
.fiscal-form { padding: 1rem; border-radius: 10px; background: color-mix(in srgb, var(--color-warning) 8%, transparent); border: 1px solid color-mix(in srgb, var(--color-warning) 30%, transparent); margin-bottom: 1rem; }
.fiscal-form-aviso { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--color-warning); margin: 0 0 0.9rem; font-weight: 600; }
.fiscal-form-grid { display: flex; gap: 1rem; flex-wrap: wrap; }
.fiscal-field { flex: 1; min-width: 200px; }
.fiscal-field label { display: block; font-weight: 600; margin-bottom: 0.3rem; font-size: 0.85rem; }
.fiscal-error { color: var(--color-error); }
.timbrar-btn { margin-top: 1.25rem; width: 100%; }
.acuse-section { margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid var(--color-border); }
.acuse-section h4 { display: flex; align-items: center; gap: 0.5rem; margin: 0 0 0.75rem; color: var(--color-title); font-size: 0.95rem; }
.publico-general-toggle { display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; font-weight: 600; margin-bottom: 1rem; cursor: pointer; }
.error-timbrado-banner {
  display: flex; gap: 0.75rem; align-items: flex-start;
  padding: 0.9rem 1.1rem; border-radius: 10px; margin-bottom: 1rem;
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-error) 30%, transparent);
  color: var(--color-error);
}
.error-timbrado-banner .pi-exclamation-triangle { font-size: 1.2rem; margin-top: 0.15rem; }
.error-timbrado-banner p { margin: 0.25rem 0 0.4rem; color: var(--color-text); font-size: 0.88rem; }
.error-timbrado-banner small { display: flex; align-items: center; gap: 0.35rem; color: var(--color-text); opacity: 0.8; }
.timbrar-form { display: flex; flex-direction: column; gap: 0.9rem; }

.ppd-flujo-banner {
  display: flex; gap: 0.75rem; align-items: flex-start;
  padding: 0.9rem 1.1rem; border-radius: 10px; margin-bottom: 1rem;
  background: color-mix(in srgb, var(--color-info, #3b82f6) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-info, #3b82f6) 30%, transparent);
  font-size: 0.88rem; color: var(--color-text);
}
.ppd-flujo-banner .pi-info-circle { font-size: 1.2rem; margin-top: 0.15rem; color: var(--color-info, #3b82f6); }
.ppd-flujo-banner ol { margin: 0.35rem 0 0; padding-left: 1.1rem; display: flex; flex-direction: column; gap: 0.3rem; }

.comprobante-section, .observaciones-section, .ordenes-detalle { margin-bottom: 1.5rem; }
.comprobante-section h3, .observaciones-section h3, .ordenes-detalle h3 { margin-bottom: 0.75rem; color: var(--color-title); }
.comprobantes-lista { margin-bottom: 0.75rem; }
.comprobante-item { display: flex; align-items: center; padding: 0.4rem 0; border-bottom: 1px solid var(--color-border); }
.comprobante-item:last-child { border-bottom: none; }

.rep-section { margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid var(--color-border); }
.rep-section h4 { display: flex; align-items: center; gap: 0.5rem; margin: 0 0 0.9rem; color: var(--color-title); font-size: 0.95rem; }
.rep-saldo-banner {
  display: flex; align-items: center; gap: 1.25rem; flex-wrap: wrap;
  padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.88rem;
  background: color-mix(in srgb, var(--color-warning) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-warning) 30%, transparent);
}
.rep-saldo-banner.rep-saldo-liquidado {
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
  border-color: color-mix(in srgb, var(--color-success) 30%, transparent);
  color: var(--color-success);
}
.rep-empty { color: var(--color-border); padding: 0.5rem 0 1rem; }
</style>
