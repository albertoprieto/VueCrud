import { defineStore } from 'pinia';

export const useReportesStore = defineStore('reportes', {
  state: () => ({
    reportes: JSON.parse(localStorage.getItem('reportes')) || []
  }),
  actions: {
    addReporte(reporte) {
      const newId = this.reportes.length ? Math.max(...this.reportes.map(r => r.id)) + 1 : 1;
      const newReporte = { ...reporte, id: newId, fecha: new Date().toISOString().split('T')[0] };
      this.reportes.push(newReporte);
      localStorage.setItem('reportes', JSON.stringify(this.reportes));
    },
    getReportes() {
      return this.reportes;
    }
  }
});