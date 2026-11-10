// POST /api/order — salvează comanda în D1 (binding DB) și trimite emailuri (opțional, prin Resend).
// Prețurile și transportul se recalculează aici, din catalogul de pe server, nu din browser.
import CATALOG from './_catalog.json';
import SHOP from './_shop.json';
import { sendMail } from '../_lib/mail.js';
import { confirmation, notification } from '../_lib/emails.js';
import { reserve, restore, syncCatalogStock } from '../_lib/stock.js';

const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { 'content-type': 'application/json; charset=utf-8' } });
const str = (v, max = 200) => (typeof v === 'string' ? v.trim().slice(0, max) : '');

export async function onRequestPost({ request, env, waitUntil }) {
  let b;
  try { b = await request.json(); } catch { return json({ ok: false, error: 'Cerere invalidă.' }, 400); }
  if (b.website) return json({ ok: true, number: 'OK', total: 0 }); // capcană pentru roboți

  const o = {
    name: str(b.name, 120), phone: str(b.phone, 30), email: str(b.email, 160), county: str(b.county, 40), city: str(b.city, 80),
    zip: str(b.zip, 10), address: str(b.address, 250), delivery: b.delivery === 'easybox' ? 'easybox' : 'address', easybox: str(b.easybox, 200),
    payment: 'cod', // deocamdată doar ramburs
    company: !!b.company, companyName: str(b.companyName, 160), companyCui: str(b.companyCui, 20),
    notes: str(b.notes, 1000), newsletter: !!b.newsletter
  };
  const errs = [];
  if (o.name.length < 3) errs.push('nume');
  if (!/^[0-9 +().-]{9,}$/.test(o.phone)) errs.push('telefon');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(o.email)) errs.push('email');
  if (!o.county || !o.city) errs.push('localitate');
  if (o.delivery === 'address' && o.address.length < 5) errs.push('adresă');
  if (o.delivery === 'easybox' && o.easybox.length < 3) errs.push('easybox');
  if (o.company && (!o.companyName || !o.companyCui)) errs.push('date firmă');
  if (b.terms !== true) errs.push('acceptarea termenilor');
  if (errs.length) return json({ ok: false, error: 'Verifică: ' + errs.join(', ') + '.' }, 400);

  const items = [];
  for (const it of Array.isArray(b.items) ? b.items.slice(0, 50) : []) {
    const p = CATALOG[it && it.sku]; const q = Math.max(1, Math.min(99, parseInt(it && it.qty, 10) || 0));
    if (!p || !p.inStock || !q) continue;
    items.push({ sku: it.sku, name: p.name, model: p.model, opt: p.opt, img: p.img, url: p.url, price: p.price, qty: q, total: Math.round(p.price * q * 100) / 100 });
  }
  if (!items.length) return json({ ok: false, error: 'Coșul este gol sau produsele nu mai sunt disponibile.' }, 400);
  const subtotal = Math.round(items.reduce((a, x) => a + x.total, 0) * 100) / 100;
  const shipping = subtotal >= SHOP.freeOver ? 0 : SHOP.cost;
  const total = Math.round((subtotal + shipping) * 100) / 100;

  const d = new Date();
  const number = 'SN' + d.toISOString().slice(2, 10).replace(/-/g, '') + '-' + Math.random().toString(36).slice(2, 6).toUpperCase();

  if (!env.DB) return json({ ok: false, error: 'Baza de date nu este configurată.' }, 500);
  const rs = await reserve(env, items);
  if (!rs.ok) return json({ ok: false, error: 'Stoc insuficient: ' + rs.short.map(x => `${x.name} (${x.left ? 'mai sunt ' + x.left + ' buc.' : 'epuizat'})`).join('; ') + '.', stock: rs.short }, 409);
  try {
  await env.DB.prepare(`INSERT INTO orders (number, created_at, status, name, phone, email, county, city, zip, address, delivery, easybox, payment,
      company_name, company_cui, notes, newsletter, items_json, subtotal, shipping, total)
      VALUES (?1, ?2, 'noua', ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13, ?14, ?15, ?16, ?17, ?18, ?19, ?20)`)
    .bind(number, d.toISOString(), o.name, o.phone, o.email, o.county, o.city, o.zip, o.address, o.delivery, o.easybox, o.payment,
      o.company ? o.companyName : null, o.company ? o.companyCui : null, o.notes, o.newsletter ? 1 : 0, JSON.stringify(items), subtotal, shipping, total)
    .run();
  } catch (e) { await restore(env, items); throw e; }
  if (rs.zeroed.length) waitUntil(syncCatalogStock(env, rs.zeroed));

  const ord = { ...o, number, created_at: d.toISOString(), items, subtotal, shipping, total };
  const ctx = { base: new URL(request.url).origin, shop: SHOP };
  const c = confirmation(ord, ctx), n = notification(ord, ctx);
  // Emailurile pleacă după răspuns, ca să nu încetinească pagina de comandă.
  waitUntil(Promise.all([
    sendMail(env, { to: o.email, replyTo: SHOP.email, subject: c.subject, html: c.html }),
    sendMail(env, { to: env.NOTIFY_EMAIL || SHOP.email, replyTo: o.email, subject: n.subject, html: n.html })
  ]));
  return json({ ok: true, number, total });
}

export const onRequest = () => json({ ok: false, error: 'Metodă nepermisă.' }, 405);
