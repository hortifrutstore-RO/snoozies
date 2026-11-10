// Emailul de expediere (o singură dată pe AWB, sau la retrimitere).
import { sendMail, mailReady } from './mail.js';
import { shipped } from './emails.js';
import SHOP from '../api/_shop.json';
export async function sendShipped(env, o, code, base) {
  if (!mailReady(env) || !code) return false;
  const m = shipped({ ...o, items: JSON.parse(o.items_json || '[]') }, code, { base, shop: SHOP });
  const r = await sendMail(env, { to: o.email, replyTo: SHOP.email, subject: m.subject, html: m.html });
  if (r.ok) await env.DB.prepare('UPDATE orders SET awb_notified_at = ?1 WHERE id = ?2').bind(new Date().toISOString(), o.id).run();
  return r.ok;
}
