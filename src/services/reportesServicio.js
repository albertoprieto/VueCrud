import axios from 'axios';

export const addReporteServicio = async (data) => {
  return await axios.post('https://api.gpsubicacionapi.com/reportes-servicio', data);
};

export const getReportePorAsignacion = async (asignacion_id) => {
  const res = await axios.get(`https://api.gpsubicacionapi.com/reportes-servicio?asignacion_id=${asignacion_id}`);
  return res.data;
};