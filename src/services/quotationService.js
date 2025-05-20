import axios from 'axios';

const API_URL = 'http://64.227.15.111/cotizaciones';

export const addQuotation = async (quotationData) => {
  const response = await axios.post(API_URL, quotationData);
  return response.data;
};

export const getQuotations = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const updateQuotation = async (id, data) => {
  const response = await axios.put(`http://64.227.15.111/cotizaciones/${id}`, data);
  return response.data;
};