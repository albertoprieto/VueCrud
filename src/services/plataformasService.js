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
