import axios from 'axios';

const API_URL = 'https://64.227.15.111/usuarios';

export const getUsuarios = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};