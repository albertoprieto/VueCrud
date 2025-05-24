import axios from 'axios';

const API_URL = 'https://64.227.15.111/articulos';

export const getArticulos = async () => {
    const response = await axios.get(API_URL);
    return response.data;
};

export const addArticulo = async (articulo) => {
    const response = await axios.post(API_URL, articulo);
    return response.data;
};

export const updateArticulo = async (articulo) => {
    const response = await axios.put(`${API_URL}/${articulo.id}`, articulo);
    return response.data;
};

export const deleteArticulo = async (id) => {
    const response = await axios.delete(`${API_URL}/${id}`);
    return response.data;
};