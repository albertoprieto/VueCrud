import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/cotizaciones`;

export const addQuotation = async (quotationData) => {
  const response = await axios.post(API_URL, quotationData);
  return response.data;
};

export const getQuotations = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const updateQuotation = async (id, data) => {
  const response = await axios.put(`${API_URL}/${id}`, data);
  return response.data;
};
