<template>
  <div class="servicio-detalle">
    <h1>{{ servicio.nombre }}</h1>
    <p>{{ servicio.descripcion }}</p>
    <h2>Dispositivos</h2>
    <div v-if="dispositivos.length === 1">
      <h3>{{ dispositivos[0].imei }}</h3>
      <video
        :id="'video-player-' + dispositivos[0].imei"
        class="video-player"
        controls
        preload="auto"
        width="600"
        height="300"
      ></video>
    </div>
    <div v-else>
      <div v-for="dispositivo in dispositivos" :key="dispositivo.imei" class="video-container">
        <h3>{{ dispositivo.imei }}</h3>
        <video
          :id="'video-player-' + dispositivo.imei"
          class="video-player"
          controls
          preload="auto"
          width="600"
          height="300"
        ></video>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import flvjs from 'flv.js';

import DataAPI from '@/services/DataAPI';

const route = useRoute();
const servicio = ref({});
const dispositivos = ref([]);

const servicios = [
  // { id: 1, nombre: 'Video', descripcion: 'Servicio de monitoreo de video.' },
  { id: 2, nombre: 'Otro', descripcion: 'Otro servicio.' },
];

const initializeVideoPlayers = async () => {
  await nextTick();
  dispositivos.value.forEach((dispositivo) => {
    const videoElement = document.getElementById(`video-player-${dispositivo.imei}`);
    if (flvjs.isSupported()) {
      const flvPlayer = flvjs.createPlayer({
        type: 'flv',
        url: dispositivo.url
      });
      flvPlayer.attachMediaElement(videoElement);
      flvPlayer.load();
      flvPlayer.play();
    }
  });
};

onMounted(async () => {
  const id = parseInt(route.params.id);
  servicio.value = servicios.find(s => s.id === id) || {};
  if (servicio.value.nombre === 'Video') {
    const urls = await DataAPI.main();
    dispositivos.value = urls.map((url) => ({
      imei: url.imei,
      url: url.url
    }));
    initializeVideoPlayers();
  }
});
</script>

<style scoped>
.servicio-detalle {
  text-align: center;
  margin: 20px;
}

.servicio-detalle h1 {
  color: #333;
}

.servicio-detalle p {
  color: #555;
}

.video-container {
  margin-bottom: 20px;
}

.video-player {
  width: 100%;
  max-width: 600px;
  height: auto;
}
</style>