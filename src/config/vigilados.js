// Usuarios cuya presencia se muestra en la barra de conectados (PresenciaBar).
// Para que el dato de "cuándo ingresó" sea incuestionable, a estos usuarios
// NO se les conserva la sesión: cada vez que abren la app tienen que
// ingresar con su contraseña (ver loginStore.restoreSession), lo que deja
// una fila real en usuarios_login_log en el servidor.
export const USUARIOS_VIGILADOS = ['mariah', 'danieli', 'vianney', 'braulior'];

export function esVigilado(username) {
  return USUARIOS_VIGILADOS.includes(String(username || '').trim().toLowerCase());
}
