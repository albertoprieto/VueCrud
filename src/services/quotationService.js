import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/cotizaciones`;

export const addQuotation = async (quotationData) => {
  const response = await axios.post(API_URL, quotationData);
  return response.data;
};

export const getQuotations = async () => {
  const response = await axios.get(API_URL);
  console.log('Quotations fetched:', response.data);
  
  return response.data;
};

export const updateQuotation = async (id, data) => {
  const response = await axios.put(`${API_URL}/${id}`, data);
  return response.data;
};

export async function getCotizacionesPendientes() {
  const res = await axios.get(API_URL);
  // Filtra cotizaciones con status 'Pendiente'
  return Array.isArray(res.data)
    ? res.data.filter(c => c.status === 'Pendiente').length
    : 0;
}

export const enviarCotizacionAlCliente = async ({ cotizacion_id, cliente_id, email_destino }) => {
  const res = await axios.post(`${import.meta.env.VITE_API_URL}/cotizaciones/enviar`, {
    cotizacion_id,
    cliente_id,
    email_destino,
    status: 'Sin aprobar'
  });
  return res.data;
};
