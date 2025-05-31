import axios from 'axios';

export const addReporteServicio = async (data) => {
  return await axios.post('https://64.227.15.111/reportes-servicio', data);
};

export const getReportePorAsignacion = async (asignacion_id) => {
  const res = await axios.get(`https://64.227.15.111/reportes-servicio?asignacion_id=${asignacion_id}`);
  return res.data;
};