import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { getClientes } from '@/services/clientesService';
import { getVentas, addVenta, getDetalleVenta } from '@/services/ventasService';
import { getIMEIs } from '@/services/imeiService';
import { sincronizarStockArticulos } from '@/services/articulosService';

export function useVentas() {
  const toast = useToast();
  const today = new Date().toISOString().slice(0, 10);

  const clientes = ref([]);
  const articulosDisponibles = ref([]);
  const ventas = ref([]);
  const ventaSeleccionada = ref(null);
  const detalleVenta = ref([]);
  const imeis = ref([]);
  const showDialog = ref(false);

  const venta = reactive({
    cliente_id: null,
    fecha: today,
    observaciones: '',
    articulos: []
  });

  const totalVenta = computed(() =>
    venta.articulos.reduce((sum, a) => sum + (a.cantidad * a.precio_unitario), 0)
  );

  const articulosAgrupados = computed(() => {
    const grupos = {};
    imeis.value
      .filter(i => i.status === 'Disponible' || i.status === 'Devuelto')
      .forEach(i => {
        if (!grupos[i.articulo_nombre]) {
          grupos[i.articulo_nombre] = [];
        }
        grupos[i.articulo_nombre].push(i);
      });
    return Object.entries(grupos).map(([articulo_nombre, imeisArr]) => ({
      articulo_nombre,
      cantidad: imeisArr.length,
      imeis: imeisArr
    }));
  });

  function getStockDisponible(articulo_id, row = null) {
    const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
    if (!articulo) return 0;
    if (articulo.tipo && articulo.tipo.toLowerCase() === 'servicio') return null;
    const grupo = articulosAgrupados.value.find(g => g.articulo_nombre === articulo.nombre);
    const totalStock = grupo ? grupo.cantidad : 0;
    const enVenta = venta.articulos
      .filter(a => a.articulo_id === articulo_id && (!row || a !== row))
      .reduce((sum, a) => sum + a.cantidad, 0);
    return totalStock - enVenta;
  }

  function articulosConStock(row = null) {
    return articulosDisponibles.value.filter(art => {
      if (art.tipo && art.tipo.toLowerCase() === 'servicio') return true;
      const stock = getStockDisponible(art.id, row);
      if (row && row.articulo_id === art.id) return true;
      return stock > 0;
    });
  }

  function imeisDisponiblesPorArticulo(articulo_id, row = null, idx = null) {
    const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
    if (!articulo) return [];
    let imeisSeleccionados = [];
    if (row && Array.isArray(row.imeis)) {
      imeisSeleccionados = row.imeis.filter((imei, i) => imei && i !== idx);
    }
    const imeisSeleccionadosOtrasFilas = venta.articulos
      .filter(a => a.articulo_id === articulo_id && a !== row && Array.isArray(a.imeis))
      .flatMap(a => a.imeis.filter(Boolean));
    const imeisNoDisponibles = [...imeisSeleccionados, ...imeisSeleccionadosOtrasFilas];
    return imeis.value.filter(i =>
      i.articulo_nombre === articulo.nombre &&
      (i.status === 'Disponible' || i.status === 'Devuelto') &&
      !imeisNoDisponibles.includes(i.imei)
    );
  }

  function mostrarColumnaIMEI(articulo_id, row = null, idx = null) {
    const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
    if (!articulo) return false;
    if (articulo.tipo && articulo.tipo.toLowerCase() === 'servicio') return false;
    // Mostrar si hay al menos un IMEI disponible o devuelto
    return imeis.value.some(i =>
      i.articulo_nombre === articulo.nombre &&
      (i.status === 'Disponible' || i.status === 'Devuelto')
    );
  }

  function addArticulo() {
    venta.articulos.push({ articulo_id: null, cantidad: 1, precio_unitario: 0, imei: null });
  }
  function removeArticulo(index) {
    venta.articulos.splice(index, 1);
  }

  function validateCantidad(row) {
    const articulo = articulosDisponibles.value.find(a => a.id === row.articulo_id);
    if (articulo && articulo.tipo && articulo.tipo.toLowerCase() === 'servicio') {
      if (row.cantidad < 1) row.cantidad = 1;
      return;
    }
    if (mostrarColumnaIMEI(row.articulo_id)) {
      // Inicializa el array imeis si no existe
      if (!Array.isArray(row.imeis)) row.imeis = [];
      // Ajusta el tamaño del array imeis según la cantidad
      if (row.cantidad > row.imeis.length) {
        for (let i = row.imeis.length; i < row.cantidad; i++) row.imeis.push(null);
      } else if (row.cantidad < row.imeis.length) {
        row.imeis.length = row.cantidad;
      }
    } else {
      row.imeis = [];
      const stock = getStockDisponible(row.articulo_id, row);
      if (row.cantidad > stock) row.cantidad = stock;
      if (row.cantidad < 1) row.cantidad = 1;
    }
  }

  function onArticuloChange(articulo_id, row) {
    const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
    if (articulo) {
      row.precio_unitario = Number(articulo.precioVenta) || 0;
      row.cantidad = 1;
      row.imei = null;
      // Inicializa imeis si corresponde
      if (!Array.isArray(row.imeis)) row.imeis = [];
      if (mostrarColumnaIMEI(articulo_id)) {
        row.imeis = [null];
      } else {
        row.imeis = [];
      }
    }
  }

  async function cargarClientes() {
    clientes.value = await getClientes();
  }
  async function cargarArticulos() {
    // Debe traer tipo de artículo
    articulosDisponibles.value = await import('@/services/articulosService').then(m => m.getTodosArticulos()).then(res => res || []);
  }
  async function cargarIMEIs() {
    imeis.value = await getIMEIs();
  }
  async function cargarVentas() {
    ventas.value = await getVentas();
  }

  async function guardarVenta() {
    const clienteExiste = clientes.value.some(c => c.id === venta.cliente_id);
    if (!clienteExiste) {
      toast.add({ severity: 'error', summary: 'Cliente inválido', detail: 'Selecciona un cliente válido.', life: 4000 });
      return;
    }
    for (const art of venta.articulos) {
      const articulo = articulosDisponibles.value.find(a => a.id === art.articulo_id);
      if (!articulo) {
        toast.add({ severity: 'error', summary: 'Artículo inválido', detail: 'Selecciona un artículo válido.', life: 4000 });
        return;
      }
      if (!(articulo.tipo && articulo.tipo.toLowerCase() === 'servicio')) {
        if (art.cantidad > getStockDisponible(art.articulo_id, art)) {
          toast.add({ severity: 'error', summary: 'Stock insuficiente', detail: `No hay suficiente stock para el artículo seleccionado.`, life: 4000 });
          return;
        }
        if (mostrarColumnaIMEI(art.articulo_id)) {
          if (Array.isArray(art.imeis)) {
            if (art.imeis.length !== art.cantidad || art.imeis.some(i => !i)) {
              toast.add({ severity: 'error', summary: 'IMEI requerido', detail: 'Selecciona todos los IMEIs para este artículo.', life: 4000 });
              return;
            }
            const todosImeis = venta.articulos.flatMap(a => Array.isArray(a.imeis) ? a.imeis : a.imei ? [a.imei] : []).filter(Boolean);
            if (new Set(todosImeis).size !== todosImeis.length) {
              toast.add({ severity: 'error', summary: 'IMEI duplicado', detail: 'No puedes vender el mismo IMEI dos veces.', life: 4000 });
              return;
            }
          } else if (!art.imei) {
            toast.add({ severity: 'error', summary: 'IMEI requerido', detail: 'Selecciona un IMEI para este artículo.', life: 4000 });
            return;
          }
        }
      }
    }
    try {
      const articulosParaEnviar = venta.articulos.flatMap(art => {
        const articulo = articulosDisponibles.value.find(a => a.id === art.articulo_id);
        if (articulo && articulo.tipo && articulo.tipo.toLowerCase() === 'servicio') {
          return [{
            articulo_id: art.articulo_id,
            cantidad: art.cantidad,
            precio_unitario: art.precio_unitario
          }];
        }
        if (Array.isArray(art.imeis) && art.imeis.length > 0) {
          // Un objeto por cada IMEI seleccionado
          return art.imeis
            .filter(imei => imei)
            .map(imei => ({
              articulo_id: art.articulo_id,
              cantidad: 1,
              precio_unitario: art.precio_unitario,
              imei
            }));
        } else if (art.imei) {
          return [{
            articulo_id: art.articulo_id,
            cantidad: 1,
            precio_unitario: art.precio_unitario,
            imei: art.imei
          }];
        } else {
          return [{
            articulo_id: art.articulo_id,
            cantidad: art.cantidad,
            precio_unitario: art.precio_unitario
          }];
        }
      });

      await addVenta({
        cliente_id: venta.cliente_id,
        fecha: venta.fecha,
        observaciones: venta.observaciones,
        total: totalVenta.value,
        articulos: articulosParaEnviar
      });
      await sincronizarStockArticulos();
      showDialog.value = true;
      toast.add({ severity: 'success', summary: 'Venta registrada', life: 3000 });
      venta.cliente_id = null;
      venta.observaciones = '';
      venta.articulos = [];
      await cargarIMEIs();
      await cargarArticulos();
      await cargarVentas();
    } catch (e) {
      toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo registrar la venta.', life: 4000 });
    }
  }

  async function cargarDetalleVenta(event) {
    if (!event?.data?.id) return;
    detalleVenta.value = await getDetalleVenta(event.data.id);
    ventaSeleccionada.value = event.data;
  }

  watch(
    () => venta.articulos.map(a => a.imei),
    (nuevosImeis, viejosImeis) => {
      nuevosImeis.forEach((imei, idx) => {
        if (imei && imei !== viejosImeis[idx]) {
          console.log('IMEI asignado a payload:', imei, 'en artículo', venta.articulos[idx]);
        }
      });
    }
  );

  const clienteSeleccionado = computed(() =>
    clientes.value.find(c => c.id === venta.cliente_id)
  );

  function agregarUsuario() {
    if (clienteSeleccionado.value) {
      if (!Array.isArray(clienteSeleccionado.value.usuarios)) clienteSeleccionado.value.usuarios = [];
      clienteSeleccionado.value.usuarios.push('');
    }
  }

  function agregarPlataforma() {
    if (clienteSeleccionado.value) {
      if (!Array.isArray(clienteSeleccionado.value.plataformas)) clienteSeleccionado.value.plataformas = [];
      clienteSeleccionado.value.plataformas.push('');
    }
  }

  onMounted(() => {
    cargarClientes();
    cargarArticulos();
    cargarIMEIs();
    cargarVentas();
  });

  return {
    today,
    clientes,
    articulosDisponibles,
    ventas,
    ventaSeleccionada,
    detalleVenta,
    imeis,
    showDialog,
    venta,
    totalVenta,
    articulosConStock,
    getStockDisponible,
    imeisDisponiblesPorArticulo,
    mostrarColumnaIMEI,
    addArticulo,
    removeArticulo,
    validateCantidad,
    onArticuloChange,
    guardarVenta,
    cargarDetalleVenta,
    clienteSeleccionado,
    agregarUsuario,
    agregarPlataforma,
    getVentas
  };
}