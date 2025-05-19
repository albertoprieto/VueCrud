import axios from 'axios';

const API_URL = 'http://64.227.15.111:8000/imeis';

export const addIMEI = async (imeiData) => {
  const response = await axios.post(API_URL, imeiData);
  return response.data;
};

export const getIMEIs = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const updateIMEI = async (imei, data) => {
  const response = await axios.put(`http://64.227.15.111:8000/imeis/${imei}`, data);
  return response.data;
};