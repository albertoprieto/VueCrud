import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { getClientes } from '@/services/clientesService';
import { getVentas, addVenta, getDetalleVenta } from '@/services/ventasService';
import { getIMEIs } from '@/services/imeiService';

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
    imeis.value.forEach(i => {
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
    const grupo = articulosAgrupados.value.find(g => g.articulo_nombre === articulo.nombre);
    const totalStock = grupo ? grupo.cantidad : 0;
    const enVenta = venta.articulos
      .filter(a => a.articulo_id === articulo_id && (!row || a !== row))
      .reduce((sum, a) => sum + a.cantidad, 0);
    return totalStock - enVenta;
  }

  function articulosConStock(row = null) {
    return articulosDisponibles.value.filter(art => {
      const stock = getStockDisponible(art.id, row);
      if (row && row.articulo_id === art.id) return true;
      return stock > 0;
    });
  }

  function imeisDisponiblesPorArticulo(articulo_id, currentRow = null) {
    const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
    if (!articulo) return [];
    const imeisSeleccionados = venta.articulos
      .filter(a => a.articulo_id === articulo_id && a.imei && a !== currentRow)
      .map(a => a.imei);
    return imeis.value.filter(i =>
      i.articulo_nombre === articulo.nombre &&
      i.status === 'Disponible' &&
      !imeisSeleccionados.includes(i.imei)
    );
  }

  function mostrarColumnaIMEI(articulo_id) {
    return imeisDisponiblesPorArticulo(articulo_id).length > 0;
  }

  function addArticulo() {
    venta.articulos.push({ articulo_id: null, cantidad: 1, precio_unitario: 0, imei: null });
  }
  function removeArticulo(index) {
    venta.articulos.splice(index, 1);
  }

  function validateCantidad(row) {
    if (mostrarColumnaIMEI(row.articulo_id)) {
      row.cantidad = 1;
    } else {
      const stock = getStockDisponible(row.articulo_id, row);
      if (row.cantidad > stock) {
        row.cantidad = stock;
      }
      if (row.cantidad < 1) {
        row.cantidad = 1;
      }
    }
  }

  function onArticuloChange(articulo_id, row) {
    const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
    if (articulo) {
      row.precio_unitario = Number(articulo.precioVenta) || 0;
      row.cantidad = mostrarColumnaIMEI(articulo_id) ? 1 : 1;
      row.imei = null;
    }
  }

  async function cargarClientes() {
    clientes.value = await getClientes();
  }
  async function cargarArticulos() {
    const res = await fetch('https://64.227.15.111/articulos/todos');
    articulosDisponibles.value = await res.json();
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
      if (art.cantidad > getStockDisponible(art.articulo_id, art)) {
        toast.add({ severity: 'error', summary: 'Stock insuficiente', detail: `No hay suficiente stock para el artículo seleccionado.`, life: 4000 });
        return;
      }
      if (mostrarColumnaIMEI(art.articulo_id)) {
        if (!art.imei) {
          toast.add({ severity: 'error', summary: 'IMEI requerido', detail: 'Selecciona un IMEI para este artículo.', life: 4000 });
          return;
        }
        const todosImeis = venta.articulos.filter(a => a.imei).map(a => a.imei);
        if (new Set(todosImeis).size !== todosImeis.length) {
          toast.add({ severity: 'error', summary: 'IMEI duplicado', detail: 'No puedes vender el mismo IMEI dos veces.', life: 4000 });
          return;
        }
      }
    }
    try {
      const articulosParaEnviar = venta.articulos.map(art => {
        // Si el artículo tiene un IMEI seleccionado, inclúyelo siempre
        if (art.imei) {
          return {
            articulo_id: art.articulo_id,
            cantidad: 1,
            precio_unitario: art.precio_unitario,
            imei: art.imei
          };
        } else {
          return {
            articulo_id: art.articulo_id,
            cantidad: art.cantidad,
            precio_unitario: art.precio_unitario
          };
        }
      });
      console.log('Payload articulos:', articulosParaEnviar);

      await addVenta({
        cliente_id: venta.cliente_id,
        fecha: venta.fecha,
        observaciones: venta.observaciones,
        total: totalVenta.value,
        articulos: articulosParaEnviar
      });
      showDialog.value = true;
      toast.add({ severity: 'success', summary: 'Venta registrada', life: 3000 });
      venta.cliente_id = null;
      venta.observaciones = '';
      venta.articulos = [];
      await cargarIMEIs();
      await cargarArticulos();
      await cargarVentas();
    } catch (e) {
      toast.add({ severity: 'error', summary: 'Error al guardar', detail: e.message, life: 4000 });
    }
  }

  async function cargarDetalleVenta(event) {
    const id = event.data?.id || ventaSeleccionada.value?.id;
    if (!id) return;
    detalleVenta.value = await getDetalleVenta(id);
  }

  // Watch para loggear cuando se asigna un IMEI a un artículo
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
    cargarDetalleVenta
  };
}