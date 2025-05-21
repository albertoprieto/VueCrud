import axios from 'axios';

const API_URL = 'https://64.227.15.111/imeis';

export const addIMEI = async (imeiData) => {
  const response = await axios.post(API_URL, imeiData);
  return response.data;
};

export const getIMEIs = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const updateIMEI = async (imei, data) => {
  const response = await axios.put(`https://64.227.15.111/imeis/${imei}`, data);
  return response.data;
};
