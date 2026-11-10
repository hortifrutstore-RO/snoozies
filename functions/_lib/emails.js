// Șabloanele emailurilor (confirmare comandă, notificare magazin, expediere).
// HTML pe tabele și stiluri inline, ca să arate la fel în Gmail, Yahoo, Outlook și pe telefon.
import { esc } from './mail.js';

const C = { cream: '#FBF5EC', card: '#FFFFFF', line: '#EADCC8', ink: '#2E2420', text: '#3A2F2A', muted: '#6B5C55', berry: '#9E2A5B', pink: '#FFB6C1', pink2: '#FFE3E8', pine: '#2F5D50' };
const SERIF = "Georgia,'Times New Roman',serif", SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif";
export const lei = n => Number(n).toFixed(2).replace('.', ',') + ' lei';
const first = n => esc(String(n || '').trim().split(/\s+/)[0] || '');
const abs = (base, u) => (u && !/^https?:/.test(u) ? base + u : u || '');
const fmtDate = iso => new Date(iso).toLocaleString('ro-RO', { timeZone: 'Europe/Bucharest', day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });

function layout({ base, shop, preheader, body }) {
  const co = shop.company || {};
  return `<!doctype html><html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>snoozies.ro</title></head>
<body style="margin:0;padding:0;background:${C.cream}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:${C.cream}">${esc(preheader)}&#8199;&#65279;&#847;&#8199;&#65279;&#847;&#8199;&#65279;&#847;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:${C.cream}"><tr><td align="center" style="padding:28px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px">
  <tr><td align="center" style="padding:0 0 22px"><a href="${base}/" style="text-decoration:none"><img src="${base}/img/site/logo-email.png" width="190" height="56" alt="Snoozies" style="display:block;border:0;width:190px;height:auto"></a></td></tr>
  ${body}
  <tr><td align="center" style="padding:26px 20px 0;font:12px/1.6 ${SANS};color:${C.muted}">
    ${esc(co.name || 'HORTIFRUT CONSULTING SRL')} · CUI ${esc(co.cui || '')} · ${esc(co.reg || '')}<br>${esc(co.address || '')}<br>
    <a href="${base}/" style="color:${C.muted}">snoozies.ro</a> · <a href="${base}/termeni-si-conditii/" style="color:${C.muted}">Termeni</a> · <a href="${base}/retur/" style="color:${C.muted}">Retur</a> · <a href="${base}/confidentialitate/" style="color:${C.muted}">Confidențialitate</a>
  </td></tr>
</table></td></tr></table></body></html>`;
}
const card = (inner, pad = '28px 28px') => `<tr><td style="background:${C.card};border-radius:20px;padding:${pad};border:1px solid ${C.line}">${inner}</td></tr><tr><td height="14" style="font-size:0;line-height:0">&nbsp;</td></tr>`;
const h2 = t => `<div style="font:bold 19px/1.3 ${SERIF};color:${C.ink};margin:0 0 14px">${t}</div>`;
const btn = (href, t) => `<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td style="background:${C.berry};border-radius:999px"><a href="${href}" style="display:inline-block;padding:13px 26px;font:bold 15px ${SANS};color:#FFFFFF;text-decoration:none">${t}</a></td></tr></table>`;

function itemsTable(items, base, withSku = false) {
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">${items.map(i => `
    <tr><td width="72" valign="top" style="padding:10px 0;border-bottom:1px solid ${C.line}">${i.img ? `<img src="${esc(abs(base, i.img))}" width="60" height="60" alt="" style="display:block;width:60px;height:60px;object-fit:cover;border-radius:12px;background:${C.cream};border:0">` : ''}</td>
      <td valign="top" style="padding:10px 10px 10px 0;border-bottom:1px solid ${C.line};font:14px/1.45 ${SANS};color:${C.text}">
        <div style="font-weight:bold;color:${C.ink}">${esc(i.model || i.name)}</div>${i.opt ? `<div style="color:${C.muted}">${esc(i.opt)}</div>` : ''}
        <div style="color:${C.muted}">${i.qty} × ${lei(i.price)}${withSku ? ` · <span style="font-family:monospace">${esc(i.sku)}</span>` : ''}</div></td>
      <td valign="top" align="right" style="padding:10px 0;border-bottom:1px solid ${C.line};font:bold 14px ${SANS};color:${C.ink};white-space:nowrap">${lei(i.total)}</td></tr>`).join('')}</table>`;
}
function totals(o) {
  const row = (l, v, big) => `<tr><td style="padding:5px 0;font:${big ? 'bold 17px' : '14px'} ${SANS};color:${big ? C.ink : C.text}">${l}</td><td align="right" style="padding:5px 0;font:${big ? 'bold 17px' : '14px'} ${SANS};color:${big ? C.berry : C.text}">${v}</td></tr>`;
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:10px">
    ${row('Produse', lei(o.subtotal))}${row('Transport ' + esc(o.carrier || 'Sameday'), o.shipping ? lei(o.shipping) : '<span style="color:' + C.pine + ';font-weight:bold">Gratuit</span>')}
    <tr><td colspan="2" style="border-top:2px solid ${C.ink};font-size:0;line-height:0;padding-top:6px">&nbsp;</td></tr>${row('Total de plată', lei(o.total), true)}</table>`;
}
const where = o => o.delivery === 'easybox' ? `<b>Easybox</b>: ${esc(o.easybox)}<br>${esc(o.city)}, jud. ${esc(o.county)}` : `${esc(o.address)}<br>${esc(o.city)}, jud. ${esc(o.county)}${o.zip ? ' · ' + esc(o.zip) : ''}`;
const company = o => o.companyName || o.company_name ? `<br><br><b>Factură pe firmă</b><br>${esc(o.companyName || o.company_name)} · CUI ${esc(o.companyCui || o.company_cui)}` : '';

// 1. Clientul: comanda a fost înregistrată
export function confirmation(o, { base, shop }) {
  const wa = shop.whatsapp ? `https://wa.me/${shop.whatsapp}?text=${encodeURIComponent('Bună! Am o întrebare despre comanda ' + o.number)}` : '';
  const step = (n, t, d) => `<tr><td width="38" valign="top" style="padding:0 0 14px"><div style="width:28px;height:28px;border-radius:999px;background:${C.pink2};color:${C.berry};font:bold 14px/28px ${SANS};text-align:center">${n}</div></td>
    <td valign="top" style="padding:3px 0 14px;font:14px/1.5 ${SANS};color:${C.text}"><b style="color:${C.ink}">${t}</b><br>${d}</td></tr>`;
  const body =
    card(`<div style="font:bold 12px ${SANS};letter-spacing:1.5px;text-transform:uppercase;color:${C.berry};margin:0 0 8px">Comandă înregistrată</div>
      <div style="font:bold 28px/1.2 ${SERIF};color:${C.ink};margin:0 0 12px">Mulțumim, ${first(o.name)}!</div>
      <div style="font:15px/1.6 ${SANS};color:${C.text};margin:0 0 18px">Am primit comanda ta și ne apucăm de ea. Papucii pleacă spre tine în 1–2 zile lucrătoare.</div>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td style="background:${C.pink2};border-radius:12px;padding:10px 16px;font:14px ${SANS};color:${C.ink}">Număr comandă: <b style="letter-spacing:.5px">${esc(o.number)}</b></td></tr></table>
      <div style="font:12px ${SANS};color:${C.muted};margin-top:8px">${fmtDate(o.created_at)}</div>`) +
    card(h2('Ce urmează') + `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
      ${step(1, 'Pregătim coletul', 'Verificăm produsele și le împachetăm cu grijă.')}
      ${step(2, 'Îl predăm curierului ' + esc(shop.carrier || 'Sameday'), 'Primești un email cu numărul AWB și linkul de urmărire.')}
      ${step(3, 'Plătești la livrare', `Suma de <b>${lei(o.total)}</b> se achită curierului, la primirea coletului.`)}</table>`) +
    card(h2('Produsele comandate') + itemsTable(o.items, base) + totals({ ...o, carrier: shop.carrier })) +
    card(`<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td valign="top" width="50%" style="padding-right:12px;font:14px/1.6 ${SANS};color:${C.text}"><div style="font:bold 12px ${SANS};letter-spacing:1px;text-transform:uppercase;color:${C.muted};margin-bottom:6px">Livrare</div><b style="color:${C.ink}">${esc(o.name)}</b><br>${where(o)}</td>
      <td valign="top" width="50%" style="font:14px/1.6 ${SANS};color:${C.text}"><div style="font:bold 12px ${SANS};letter-spacing:1px;text-transform:uppercase;color:${C.muted};margin-bottom:6px">Contact și plată</div>${esc(o.phone)}<br>${esc(o.email)}<br>Ramburs, la livrare${company(o)}</td>
    </tr></table>${o.notes ? `<div style="margin-top:14px;padding-top:12px;border-top:1px solid ${C.line};font:14px/1.5 ${SANS};color:${C.text}"><b>Observațiile tale:</b> ${esc(o.notes)}</div>` : ''}
    <div style="margin-top:14px;font:13px/1.5 ${SANS};color:${C.muted}">Ceva nu e corect în adresă sau telefon? Răspunde la acest email și corectăm înainte de expediere.</div>`) +
    card(`${h2('Ai o întrebare?')}<div style="font:14px/1.6 ${SANS};color:${C.text};margin:0 0 16px">Răspunde direct la acest email, sună la <a href="tel:+${esc(shop.whatsapp || '40746242877')}" style="color:${C.berry};font-weight:bold;text-decoration:none">${esc(shop.phone || '0746 242 877')}</a>${wa ? ' sau scrie-ne pe WhatsApp' : ''}. Ai 14 zile să returnezi produsele, dacă nu se potrivesc.</div>
      ${wa ? btn(wa, 'Scrie-ne pe WhatsApp') : ''}`);
  return { subject: `Comanda ${o.number} a fost înregistrată`, html: layout({ base, shop, preheader: `Mulțumim! Total ${lei(o.total)}, plata la livrare. Coletul pleacă în 1–2 zile lucrătoare.`, body }) };
}

// 2. Magazinul: comandă nouă
export function notification(o, { base, shop }) {
  const tel = String(o.phone).replace(/\D/g, '').replace(/^0/, '40');
  const body =
    card(`<div style="font:bold 12px ${SANS};letter-spacing:1.5px;text-transform:uppercase;color:${C.berry};margin:0 0 8px">Comandă nouă · ${esc(o.number)}</div>
      <div style="font:bold 28px/1.2 ${SERIF};color:${C.ink};margin:0 0 6px">${lei(o.total)}</div>
      <div style="font:14px ${SANS};color:${C.muted};margin:0 0 18px">${fmtDate(o.created_at)} · ramburs · ${o.items.reduce((a, i) => a + i.qty, 0)} buc.</div>
      ${btn(base + '/admin/', 'Deschide în panou')}`) +
    card(`<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td valign="top" width="50%" style="padding-right:12px;font:14px/1.6 ${SANS};color:${C.text}"><b style="color:${C.ink}">${esc(o.name)}</b><br><a href="tel:+${tel}" style="color:${C.berry}">${esc(o.phone)}</a> · <a href="https://wa.me/${tel}" style="color:${C.berry}">WhatsApp</a><br><a href="mailto:${esc(o.email)}" style="color:${C.berry}">${esc(o.email)}</a>${company(o)}</td>
      <td valign="top" width="50%" style="font:14px/1.6 ${SANS};color:${C.text}">${where(o)}</td></tr></table>
      ${o.notes ? `<div style="margin-top:12px;padding:10px 14px;background:${C.pink2};border-radius:12px;font:14px/1.5 ${SANS};color:${C.ink}"><b>Observații:</b> ${esc(o.notes)}</div>` : ''}`) +
    card(itemsTable(o.items, base, true) + totals({ ...o, carrier: shop.carrier }));
  return { subject: `Comandă nouă ${o.number} – ${lei(o.total)} – ${o.name}`, html: layout({ base, shop, preheader: `${o.name}, ${o.city} · ${lei(o.total)}`, body }) };
}

// 3. Clientul: coletul a fost expediat
export function shipped(o, code, { base, shop }) {
  const link = (shop.trackingUrl || 'https://sameday.ro/status-colet/?awb={awb}').replace('{awb}', encodeURIComponent(code));
  const body =
    card(`<div style="font:bold 12px ${SANS};letter-spacing:1.5px;text-transform:uppercase;color:${C.berry};margin:0 0 8px">Comanda ${esc(o.number)}</div>
      <div style="font:bold 28px/1.2 ${SERIF};color:${C.ink};margin:0 0 12px">Papucii tăi sunt pe drum, ${first(o.name)}!</div>
      <div style="font:15px/1.6 ${SANS};color:${C.text};margin:0 0 18px">Am predat coletul curierului ${esc(shop.carrier || 'Sameday')}. De obicei ajunge în 1–2 zile lucrătoare.</div>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:18px"><tr><td style="background:${C.pink2};border-radius:12px;padding:10px 16px;font:14px ${SANS};color:${C.ink}">AWB: <b style="letter-spacing:.5px">${esc(code)}</b></td></tr></table>
      ${btn(link, 'Urmărește coletul')}
      ${o.payment === 'cod' ? `<div style="font:14px/1.6 ${SANS};color:${C.text};margin-top:18px">De plătit curierului la livrare: <b>${lei(o.total)}</b></div>` : ''}`) +
    card(h2('În colet') + itemsTable(o.items, base)) +
    card(`<div style="font:14px/1.6 ${SANS};color:${C.text}">Întrebări despre livrare? Răspunde la acest email sau sună la <b>${esc(shop.phone || '0746 242 877')}</b>.</div>`);
  return { subject: `Comanda ${o.number} a fost expediată – AWB ${code}`, html: layout({ base, shop, preheader: `AWB ${code} · urmărește coletul`, body }) };
}
