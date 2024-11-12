<template>
    <div class="informacion">
        <h1>Bienvenido</h1>
        <Divider align="left">
            <span class="section-title">Sobre Nosotros</span>
        </Divider>
        <Card class="card-about-us">
            <template #title>
                <h2>Quiénes Somos</h2>
            </template>
            <template #content>
                <p>.</p>
            </template>
        </Card>

        <Divider align="left">
            <span class="section-title">Nuestros Productos</span>
        </Divider>
        <Card class="card-products">
            <template #title>
                <h2>Ir al catálogo</h2>
            </template>
            <template #subtitle>
                <Button label="Adquirir" icon="pi pi-shopping-cart" @click="goToAdquirir" />
            </template>
            <template #content>
                <p>.</p>
            </template>
        </Card>

        <Divider align="left">
            <span class="section-title">Contacto</span>
        </Divider>
        <Card class="card-contact">
            <template #title>
                <h2>Contáctanos</h2>
            </template>
            <template #content>
                <p>.</p>
            </template>
        </Card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Card from 'primevue/card';
import Divider from 'primevue/divider';
import {useRouter} from 'vue-router'
const router = useRouter();
const someReactiveProperty = ref(null);

const goToAdquirir = () => {
  router.push('/adquirir');
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

.section-title {
    font-size: 1.5rem;
    font-weight: bold;
}

.card-about-us {
    background-color: #f0f8ff;
    margin-bottom: 20px;
}

.card-products {
    background-color: #e6ffe6;
    margin-bottom: 20px;
}

.card-contact {
    background-color: #fff0f5;
    margin-bottom: 20px;
}

.card-about-us h2,
.card-products h2,
.card-contact h2 {
    color: #333;
}

.card-about-us p,
.card-products p,
.card-contact p {
    color: #555;
}
</style>