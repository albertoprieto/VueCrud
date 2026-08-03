import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/operacion-imeis`;

export const getOperacionImeis = async (params = {}) => {
  const res = await axios.get(API_URL, { params });
  return res.data;
};
