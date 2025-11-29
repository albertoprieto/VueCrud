import { defineStore } from 'pinia'

export const useServiciosReporteStore = defineStore('serviciosReporte', {
  state: () => ({
    servicios: []
  }),
  actions: {
    agregarServicio(servicio) {
      this.servicios.push(servicio)
    },
    eliminarServicio(index) {
      this.servicios.splice(index, 1)
    },
    limpiarServicios() {
      this.servicios = []
    },
    actualizarServicio(index, servicio) {
      this.servicios[index] = servicio
    }
  }
})
