import axios from 'axios';

export const getAsignacionesTecnicos = async () => {
  const res = await axios.get('https://64.227.15.111/asignaciones-tecnicos');
  return res.data;
};