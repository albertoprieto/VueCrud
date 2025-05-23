const STORAGE_KEY = 'articulos';

export const getArticulos = async () => {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : [];
};

export const addArticulo = async (articulo) => {
  const articulos = await getArticulos();
  const newId = articulos.length ? Math.max(...articulos.map(a => a.id)) + 1 : 1;
  const nuevo = { ...articulo, id: newId };
  articulos.push(nuevo);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(articulos));
  return nuevo;
};

export const updateArticulo = async (articulo) => {
  const articulos = await getArticulos();
  const idx = articulos.findIndex(a => a.id === articulo.id);
  if (idx !== -1) {
    articulos[idx] = articulo;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(articulos));
  }
};

export const deleteArticulo = async (id) => {
  let articulos = await getArticulos();
  articulos = articulos.filter(a => a.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(articulos));
};