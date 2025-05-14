<template>
    <div class="informacion">
        <h1>X</h1>
        <div class="grid-container">
            <Card class="card card-about-us" @click="navigateTo('/registrar')">
                <template #title>
                    <h2>Registrar</h2>
                </template>
            </Card>

            <Card class="card card-products" @click="navigateTo('/consultar')">
                <template #title>
                    <h2>Consultar</h2>
                </template>
            </Card>

            <Card class="card card-contact" @click="navigateTo('/reporte')">
                <template #title>
                    <h2>Reporte</h2>
                </template>
            </Card>
            <Card class="card card-contact" @click="navigateTo('/cotizacion')">
                <template #title>
                    <h2>Cotización</h2>
                </template>
            </Card>
            <Card class="card card-contact" @click="navigateTo('/consultar-cotizaciones')">
                <template #title>
                    <h2>Consultar Cotizaciones</h2>
                </template>
            </Card>
            <Card class="card card-contact" @click="navigateTo('/calendario-cotizaciones')">
                <template #title>
                    <h2>Calendario Cotizaciones</h2>
                </template>
            </Card>

        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import { useRouter } from 'vue-router';

const router = useRouter();

const navigateTo = (route) => {
  router.push(route);
};

onMounted(() => {
  console.log('Componente Información montado');
});
</script>

<style scoped>
.informacion {
    text-align: center;
    margin: 20px;
}

.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.card {
    background-color: #3f3f3f; /* Gris muy oscuro */
    color: #e4c8c8; /* Texto blanco para contraste */
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
    padding: 20px;
    border-radius: 8px; /* Bordes redondeados */
}

.card:hover {
    transform: translateY(-10px);
    box-shadow: 0 10px 20px rgba(8, 74, 255, 0.2);
}

.card h2 {
    color: #e4c8c8; /* Asegura que los títulos sean visibles */
}

.card p {
    color: #e4c8c8; /* Texto secundario en gris claro */
}
</style>