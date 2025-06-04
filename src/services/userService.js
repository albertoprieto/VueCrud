import axios from 'axios';


const API_URL = import.meta.env.VITE_API_URL;

export const getUsuarios = async () => {
  const response = await axios.get(`${import.meta.env.VITE_API_URL}/usuarios`)
  return response.data;
};

// Nuevo método para login seguro
export const loginUsuario = async (username, password) => {
  const response = await axios.post(`${API_URL}/usuarios/login`, { username, password });
  return response.data;
};
