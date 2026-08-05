import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

/**
 * Busca dispositivos en IOP o Tracksolid.
 * @param {string} query - Texto de búsqueda (IMEI, nombre, cuenta)
 * @param {'iop'|'tracksolid'} plataforma
 * @returns {Promise<{plataforma: string, total: number, resultados: Array}>}
 */
export const buscarDispositivosPlataforma = async (query, plataforma) => {
  const res = await axios.get(`${API_URL}/api/plataformas/buscar`, {
    params: { q: query, plataforma }
  });
  return res.data;
};

/**
 * Obtiene detalle completo de un dispositivo por IMEI.
 * @param {string} imei
 * @param {'iop'|'tracksolid'} plataforma
 * @returns {Promise<{plataforma: string, dispositivo: object}>}
 */
export const obtenerDetalleDispositivo = async (imei, plataforma) => {
  const res = await axios.get(`${API_URL}/api/plataformas/dispositivo/${encodeURIComponent(imei)}`, {
    params: { plataforma }
  });
  return res.data;
};

/**
 * Teléfono de contacto asociado al dispositivo — IOP y Tracksolid lo guardan
 * en lugares distintos de la respuesta de /api/plataformas/buscar:
 * IOP: item.account.contactTel · Tracksolid: item.sim (driverPhone viene
 * vacío siempre en la práctica — el número real es el de la SIM).
 * Espera un item crudo de `resultados[]` (buscarDispositivosPlataforma), no
 * el objeto ya aplanado.
 * @param {object} item
 * @param {'iop'|'tracksolid'} plataforma
 * @returns {string}
 */
export const extraerTelefonoContacto = (item, plataforma) => {
  if (!item) return '';
  if (plataforma === 'iop') return item.account?.contactTel || '';
  if (plataforma === 'tracksolid') return item.sim || item.driverPhone || '';
  return '';
};
