import axios from 'axios';

const API_URL = 'https://64.227.15.111/usuarios';

export const getUsuarios = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

// Nuevo método para login seguro
export const loginUsuario = async (username, password) => {
  const response = await axios.post(`${API_URL}/login`, { username, password });
  return response.data;
};