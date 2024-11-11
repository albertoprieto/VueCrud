<template>
    <div class="envios">
        <h1>Monitoreo de Envíos</h1>
        <DataTable :value="pedidos" responsiveLayout="scroll">
            <Column field="id" header="ID Pedido"></Column>
            <Column field="producto" header="Producto"></Column>
            <Column field="estado" header="Estado" :body="estadoTemplate"></Column>
            <Column field="fechaEnvio" header="Fecha de Envío"></Column>
            <Column field="fechaEntrega" header="Fecha de Entrega"></Column>
        </DataTable>
    </div>
</template>

<script setup>
import { ref, onMounted, h } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';

const pedidos = ref([
    { id: 1, producto: 'Laptop', estado: 'En camino', fechaEnvio: '2023-10-01', fechaEntrega: '2023-10-05' },
    { id: 2, producto: 'Smartphone', estado: 'Preparando envío', fechaEnvio: '2023-10-02', fechaEntrega: '2023-10-06' },
    { id: 3, producto: 'Auriculares', estado: 'Entregado', fechaEnvio: '2023-09-28', fechaEntrega: '2023-10-02' }
]);

const estadoTemplate = (rowData) => {
    let severity = '';
    switch (rowData.estado) {
        case 'En camino':
            severity = 'info';
            break;
        case 'Preparando envío':
            severity = 'warning';
            break;
        case 'Entregado':
            severity = 'success';
            break;
        default:
            severity = 'secondary';
    }
    return h(Tag, { value: rowData.estado, severity: severity });
};

onMounted(() => {
    console.log('Componente Envios montado');
});
</script>

<style scoped>
.envios {
    text-align: center;
    margin: 20px;
}

h1 {
    margin-bottom: 20px;
}

.p-datatable {
    margin-top: 20px;
}
</style>