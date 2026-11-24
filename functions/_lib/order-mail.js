// Emailurile de comandă (client + magazin), pornind de la rândul din tabela `orders`.
import SHOP from '../api/_shop.json';
import { sendMail } from './mail.js';
import { confirmation, notification } from './emails.js';

export async function sendOrderMails(env, origin, row) {
  const o = { ...row, items: Array.isArray(row.items) ? row.items : JSON.parse(row.items_json || '[]') };
  const ctx = { base: origin, shop: SHOP };
  const c = confirmation(o, ctx), n = notification(o, ctx);
  await Promise.all([
    sendMail(env, { to: o.email, replyTo: SHOP.email, subject: c.subject, html: c.html }),
    sendMail(env, { to: env.NOTIFY_EMAIL || SHOP.email, replyTo: o.email, subject: n.subject, html: n.html })
  ]);
}
