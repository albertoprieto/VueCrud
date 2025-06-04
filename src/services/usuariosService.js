import axios from 'axios';


const API_URL = `${import.meta.env.VITE_API_URL}/usuarios`;
export const getUsuarios = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};

export const addUsuario = async (usuario) => {
  const res = await axios.post(API_URL, usuario);
  return res.data;
};

export const updateUsuario = async (id, usuario) => {
  const res = await axios.put(`${API_URL}/${id}`, usuario);
  return res.data;
};

export const deleteUsuario = async (id) => {
  const res = await axios.delete(`${API_URL}/${id}`);
  return res.data;
};