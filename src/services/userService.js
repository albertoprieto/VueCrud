import axios from 'axios';


const API_URL = import.meta.env.VITE_API_URL;

export const getUsuarios = async () => {
  const response = await axios.get(`${import.meta.env.VITE_API_URL}/usuarios`)
  return response.data;
};

export const loginUsuario = async (username, password) => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  // Usar el endpoint estándar de OAuth2
  const response = await axios.post(`${API_URL}/token`, params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  return response.data; // { access_token, token_type, user }
};
