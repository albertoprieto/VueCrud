import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export const addQuotation = async (quotationData) => {
  //
  const response = await axios.post(`${API_URL}/cotizaciones`, quotationData);
  return response.data;
};

export const getQuotations = async () => {
  const response = await axios.get(`${API_URL}/cotizaciones`);
  return response.data;
};

export const updateQuotation = async (id, data) => {
  const response = await axios.put(`${API_URL}/cotizaciones/${id}`, data);
  return response.data;
};

export async function getCotizacionesPendientes() {
  const res = await axios.get(`${API_URL}/cotizaciones`);
  return Array.isArray(res.data)
    ? res.data.filter(c => c.status === 'Pendiente').length
    : 0;
}

// ENVÍA COTIZACIÓN POR WHATSAPP (solo llamada a API)
export const enviarCotizacionWhatsapp = async ({ cotizacion_id, cliente_id, telefono, mensaje }) => {
  const res = await axios.post(`${API_URL}/cotizaciones/enviar-whatsapp`, {
    cotizacion_id,
    cliente_id,
    telefono,
    mensaje
  });
  return res.data;
};
