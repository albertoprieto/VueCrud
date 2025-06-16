import axios from 'axios';

class CotizacionMailService {
  static async enviarCotizacion(cotizacion) {
    const asunto = `Cotización #${cotizacion.folio || cotizacion.id || ''}`;
    const cuerpo = `Estimado cliente, adjuntamos su cotización.\n\nGracias.`;
    return this.enviarCorreo(cotizacion.cliente_email, asunto, cuerpo);
  }

  static async enviarCorreo(destinatario, asunto, cuerpo) {
    try {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/enviar-cotizacion`, {
        destinatario,
        asunto,
        cuerpo
      });
      return res.data;
    } catch (e) {
      throw new Error('No se pudo enviar el correo');
    }
  }
}

export { CotizacionMailService };