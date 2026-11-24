// POST: cererea clientului de anulare a comenzii sau de retragere din contract (art. 11¹ din OUG 34/2014).
// Salvează cererea în D1, o notează pe comandă (dacă numărul și emailul se potrivesc) și trimite confirmarea
// de primire pe email (suport durabil), cu conținutul cererii, data și ora.
import { json } from '../_lib/auth.js';
import { sendMail } from '../_lib/mail.js';
import { normEmail, validEmail } from '../_lib/customer.js';
import { withdrawalReceipt, withdrawalNotice } from '../_lib/emails.js';
import SHOP from './_shop.json';

const str = (v, n) => String(v ?? '').replace(/[<>]/g, '').trim().slice(0, n);

export async function onRequestPost({ request, env }) {
  let b = {}; try { b = await request.json(); } catch {}
  if (b.website) return json({ ok: true, ref: 'OK', at: new Date().toISOString() }); // capcană pentru roboți
  const w = {
    kind: b.kind === 'anulare' ? 'anulare' : 'retragere',
    number: str(b.number, 40).toUpperCase(), name: str(b.name, 120), email: normEmail(b.email), phone: str(b.phone, 30),
    items: str(b.items, 1500), iban: str(b.iban, 60).replace(/\s+/g, ' '), message: str(b.message, 1500)
  };
  if (!w.name) return json({ ok: false, error: 'Completează numele.' }, 400);
  if (!validEmail(w.email)) return json({ ok: false, error: 'Adresa de email nu pare corectă.' }, 400);
  if (!w.number) return json({ ok: false, error: 'Completează numărul comenzii (îl găsești în emailul de confirmare).' }, 400);

  await env.DB.prepare(`CREATE TABLE IF NOT EXISTS withdrawals (id INTEGER PRIMARY KEY AUTOINCREMENT, ref TEXT UNIQUE NOT NULL, created_at TEXT NOT NULL,
    kind TEXT NOT NULL, order_number TEXT, order_id INTEGER, name TEXT, email TEXT, phone TEXT, items TEXT, iban TEXT, message TEXT, ip TEXT)`).run();
  const ip = request.headers.get('cf-connecting-ip') || '';
  const since = new Date(Date.now() - 60 * 60e3).toISOString();
  const r = await env.DB.prepare('SELECT COUNT(*) AS n FROM withdrawals WHERE ip = ?1 AND created_at > ?2').bind(ip, since).first();
  if ((r?.n || 0) >= 5) return json({ ok: false, error: `Ai trimis deja mai multe cereri. Dacă e nevoie, scrie-ne la ${SHOP.email} sau sună la ${SHOP.phone}.` }, 429);

  const order = await env.DB.prepare('SELECT * FROM orders WHERE number = ?1 AND email = ?2 COLLATE NOCASE').bind(w.number, w.email).first();
  const now = new Date(), at = now.toISOString();
  const ref = 'R' + at.slice(2, 10).replace(/-/g, '') + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();
  await env.DB.prepare(`INSERT INTO withdrawals (ref, created_at, kind, order_number, order_id, name, email, phone, items, iban, message, ip)
    VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12)`)
    .bind(ref, at, w.kind, w.number, order ? order.id : null, w.name, w.email, w.phone, w.items, w.iban, w.message, ip).run();

  if (order) {
    const when = now.toLocaleString('ro-RO', { timeZone: 'Europe/Bucharest', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    const line = `${when}: clientul a cerut ${w.kind === 'anulare' ? 'ANULAREA comenzii' : 'RETRAGEREA din contract'} prin site (cererea ${ref}).`;
    await env.DB.prepare('UPDATE orders SET admin_note = CASE WHEN COALESCE(admin_note, \'\') = \'\' THEN ?1 ELSE admin_note || char(10) || ?1 END WHERE id = ?2').bind(line, order.id).run();
  }

  const origin = new URL(request.url).origin;
  const ctx = { base: origin, shop: SHOP };
  const data = { ...w, ref, at, matched: !!order, shipped: !!(order && (order.awb || order.status === 'expediata' || order.status === 'livrata')) };
  const c = withdrawalReceipt(data, ctx), n = withdrawalNotice(data, ctx);
  const [mc] = await Promise.all([
    sendMail(env, { to: w.email, replyTo: SHOP.email, subject: c.subject, html: c.html }),
    sendMail(env, { to: env.NOTIFY_EMAIL || SHOP.email, replyTo: w.email, subject: n.subject, html: n.html })
  ]);
  return json({ ok: true, ref, at, emailed: !!mc.ok, matched: !!order, shipped: data.shipped });
}
