<template>
  <div class="servicios">
    <h1>Servicios</h1>
    <div class="card-container">
      <Card v-for="servicio in servicios" :key="servicio.id" class="servicio-card" @click="navigateToService(servicio.id)">
        <template #title>
          <h2>{{ servicio.nombre }}</h2>
        </template>
        <template #content>
          <p>{{ servicio.descripcion }}</p>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';

const servicios = ref([
  { id: 1, nombre: 'Servicio', descripcion: 'Servicio.' },
  // { id: 2, nombre: 'Otro', descripcion: 'Otro.' },
]);

const router = useRouter();

const navigateToService = (id) => {
  router.push(`/servicio/${id}`);
};

onMounted(() => {
  console.log('Componente Servicios montado');
});
</script>

<style scoped>
.servicios {
  text-align: center;
  margin: 20px;
}

.card-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.servicio-card {
  width: 300px;
  cursor: pointer;
}

.servicio-card h2 {
  color: #333;
}

.servicio-card p {
  color: #555;
}
</style>