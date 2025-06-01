import axios from 'axios';

export const getAsignacionesTecnicos = async () => {
  const res = await axios.get('https://api.gpsubicacionapi.com/asignaciones-tecnicos');
  return res.data;
};