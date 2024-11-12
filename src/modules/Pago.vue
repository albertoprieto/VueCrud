<template>
  <div class="pago" v-if="payment">
    <Card>
      <h1>Realizar Pago</h1>
      <img :src="payment.image" alt="Image" class="item-image"/>
      <p>Descripción: {{ payment.description }}</p>
      <p>Monto: {{ payment.amount }}</p>
      <Button label="Pagar con MercadoPago" @click="pagar" />
    </Card>
  </div>
  <div v-else>
    <p>Cargando...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Button from 'primevue/button';
import Card from 'primevue/card';
import { usePaymentsStore } from '@/stores/paymentsStore';

const route = useRoute();
const paymentsStore = usePaymentsStore();
const payment = ref(null);

onMounted(() => {
  const id = parseInt(route.params.id, 10);
  payment.value = paymentsStore.getPaymentById(id);
});

const pagar = () => {
  const mercadoPagoUrl = 'https://mpago.la/2iNHic4';
  window.location.href = mercadoPagoUrl;
};
</script>

<style scoped>
.pago {
  text-align: center;
  margin-top: 20px;
}
.item-image {
  width: 100%;
  height: auto;
}
</style>