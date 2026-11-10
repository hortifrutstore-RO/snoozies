// Configurația publică pentru harta de easybox (userul de API nu e secret: îl cere chiar harta Sameday).
const PLUGIN_CLIENT_ID = 'b8cb2ee3-41b9-4c3d-aafe-1527b453d65e'; // clientId-ul public al hărții Sameday (din pluginurile lor oficiale)
export const onRequestGet = ({ env }) => new Response(JSON.stringify(env.SAMEDAY_USER
  ? { enabled: true, apiUsername: String(env.SAMEDAY_USER).toLowerCase(), clientId: env.SAMEDAY_LOCKER_CLIENT_ID || PLUGIN_CLIENT_ID }
  : { enabled: false }), { headers: { 'content-type': 'application/json', 'cache-control': 'public, max-age=300' } });
