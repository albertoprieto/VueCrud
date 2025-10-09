import axios from 'axios';
import { getReportesServicioTodos } from '@/services/reportesService';

const API_BASE = import.meta?.env?.VITE_API_URL || '';
const API_URL = API_BASE ? `${API_BASE}/tickets` : '';
const CONTEXT_URL_ALT = API_BASE ? `${API_BASE}/reportes-servicio` : '';

// LocalStorage fallback for development when backend endpoint is not ready
const LS_KEY = 'tickets_store_v1';

function readLS() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? JSON.parse(raw) : { tickets: [], lastId: 0 };
  } catch {
    return { tickets: [], lastId: 0 };
  }
}

function writeLS(state) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch {}
}

export async function getTickets(params = {}) {
  if (API_URL) {
    try {
      const res = await axios.get(API_URL, { params });
      const data = Array.isArray(res.data) ? res.data : [];
      return data.map(normalizeTicket);
    } catch (e) {
      console.warn('[ticketsService] GET fallback LS', e?.message);
    }
  }
  const s = readLS();
  // simple filter by estado if provided
  let list = s.tickets;
  if (params.estado) list = list.filter(t => t.estado === params.estado);
  if (params.reporteId) list = list.filter(t => Number(t.reporteId) === Number(params.reporteId));
  return list.map(normalizeTicket);
}

export async function getTicket(id) {
  if (API_URL) {
    try {
      const res = await axios.get(`${API_URL}/${id}`);
      return normalizeTicket(res.data);
    } catch (e) {
      console.warn('[ticketsService] GET/:id fallback LS', e?.message);
    }
  }
  const s = readLS();
  const row = s.tickets.find(t => String(t.id) === String(id));
  return row ? normalizeTicket(row) : null;
}

export async function createTicket(payload) {
  if (API_URL) {
    try {
      const res = await axios.post(API_URL, payload);
      return res.data;
    } catch (e) {
      console.warn('[ticketsService] POST fallback LS', e?.message);
    }
  }
  const s = readLS();
  const id = s.lastId + 1;
  const now = new Date().toISOString();
  const ticket = {
    id,
    estado: 'nuevo',
    prioridad: 'media',
    tipo: 'soporte',
    comentarios: [],
    ...payload,
    createdAt: now,
    updatedAt: now
  };
  s.lastId = id;
  s.tickets.unshift(ticket);
  writeLS(s);
  return ticket;
}

export async function updateTicket(id, patch) {
  if (API_URL) {
    try {
      const res = await axios.patch(`${API_URL}/${id}`, patch);
      return res.data;
    } catch (e) {
      console.warn('[ticketsService] PATCH fallback LS', e?.message);
    }
  }
  const s = readLS();
  const idx = s.tickets.findIndex(t => String(t.id) === String(id));
  if (idx >= 0) {
    s.tickets[idx] = { ...s.tickets[idx], ...patch, updatedAt: new Date().toISOString() };
    writeLS(s);
    return s.tickets[idx];
  }
  return null;
}

export async function addComment(id, comment) {
  if (API_URL) {
    try {
      const res = await axios.post(`${API_URL}/${id}/comments`, { comment });
      return res.data;
    } catch (e) {
      console.warn('[ticketsService] POST /comments fallback LS', e?.message);
    }
  }
  const s = readLS();
  const t = s.tickets.find(tt => String(tt.id) === String(id));
  if (t) {
    t.comentarios ||= [];
    t.comentarios.push({ id: String(Date.now()), text: comment, createdAt: new Date().toISOString() });
    t.updatedAt = new Date().toISOString();
    writeLS(s);
    return t;
  }
  return null;
}

export async function deleteTicket(id) {
  if (API_URL) {
    try {
      const res = await axios.delete(`${API_URL}/${id}`);
      return res.status >= 200 && res.status < 300;
    } catch (e) {
      console.warn('[ticketsService] DELETE fallback LS', e?.message);
    }
  }
  const s = readLS();
  const idx = s.tickets.findIndex(t => String(t.id) === String(id));
  if (idx >= 0) {
    const removed = s.tickets.splice(idx, 1)[0];
    writeLS(s);
    return !!removed;
  }
  return false;
}

// Contexto derivado del reporte de servicio (usa vista v_ticket_context en el backend)
export async function getTicketContextByReporte(reporteId) {
  // Prefer: GET /reportes-servicio/:id/context
  if (CONTEXT_URL_ALT) {
    try {
      const res = await axios.get(`${CONTEXT_URL_ALT}/${reporteId}/context`);
      return res.data;
    } catch (e) {
      console.warn('[ticketsService] context ALT failed', e?.message);
    }
  }
  // Fallback: GET /tickets/context?reporteId=
  if (API_BASE) {
    try {
      const res = await axios.get(`${API_BASE}/ticket-context`, { params: { reporteId } });
      return res.data;
    } catch (e) {
      console.warn('[ticketsService] context fallback failed', e?.message);
    }
  }
  // Fallback 2: construir desde reportes-servicio-todos (externo)
  try {
    const all = await getReportesServicioTodos();
    const row = (Array.isArray(all) ? all : []).find(r => Number(r.id) === Number(reporteId));
    if (row) return buildContextFromReporteRow(row);
  } catch (e) {
    console.warn('[ticketsService] context from reportes-servicio-todos failed', e?.message);
  }
  // As last resort, return minimal shape
  return { reporte_id: reporteId, imeis_concat: null, imeis_json: [], folio_reporte: null };
}

// Helpers
function normalizeTicket(row = {}) {
  // Mapear snake_case del backend a camelCase que usa el frontend
  const out = { ...row };
  out.reporteId = row.reporteId ?? row.reporte_id ?? row.reporteID;
  out.clienteNombre = row.clienteNombre ?? row.cliente_nombre;
  out.clienteId = row.clienteId ?? row.cliente_id;
  out.createdAt = row.createdAt ?? row.created_at;
  out.updatedAt = row.updatedAt ?? row.updated_at;
  // Normalizar comentarios
  if (Array.isArray(row.comentarios)) {
    out.comentarios = row.comentarios.map(c => ({
      ...c,
      createdAt: c.createdAt ?? c.created_at
    }));
  }
  // IMEIs ya vienen parseados en backend; mantener
  return out;
}

function buildContextFromReporteRow(r) {
  // r es un elemento de /reportes-servicio-todos
  const imeis = new Set();
  if (r?.imei) imeis.add(String(r.imei));
  const arr = Array.isArray(r?.imeis_articulos) ? r.imeis_articulos : [];
  for (const it of arr) {
    if (Array.isArray(it?.imeis)) {
      it.imeis.filter(Boolean).forEach(x => imeis.add(String(x)));
    }
  }
  return {
    reporte_id: r?.id,
    folio_reporte: r?.folio ?? null,
    cliente_id: null, // no viene en este endpoint
    cliente_nombre: r?.nombre_cliente ?? null,
    folio_venta: null,
    imeis_json: Array.from(imeis),
    imeis_concat: Array.from(imeis).join(',') || null,
  };
}
