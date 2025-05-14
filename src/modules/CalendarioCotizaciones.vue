<template>
  <div class="calendario-cotizaciones">
    <h2>Calendario de Cotizaciones</h2>
    <FullCalendar :events="events" :options="calendarOptions" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useQuotationStore } from '@/stores/quotationStore';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';

const quotationStore = useQuotationStore();
const events = computed(() =>
  quotationStore.getQuotations()
    .filter((q) => q.status === 'Agendado' && q.calendarDate)
    .map((q) => ({
      title: `${q.cliente} - ${q.technician}`,
      start: new Date(q.calendarDate).toISOString().split('T')[0],
      backgroundColor: '#28a745',
      borderColor: '#28a745'
    }))
);

const calendarOptions = ref({
  plugins: [dayGridPlugin],
  initialView: 'dayGridMonth',
  locale: 'es'
});
</script>

<style scoped>
.calendario-cotizaciones {
  max-width: 900px;
  margin: 0 auto;
}
</style>