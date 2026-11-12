// Creează tabelele în baza D1 la prima cerere (o dată pe instanță), ca să nu fie nevoie de rulat schema manual.
const SCHEMA = [
 "CREATE TABLE IF NOT EXISTS orders ( id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT UNIQUE NOT NULL, created_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'noua', name TEXT NOT NULL, phone TEXT NOT NULL, email TEXT NOT NULL, county TEXT, city TEXT, zip TEXT, address TEXT, delivery TEXT NOT NULL, easybox TEXT, payment TEXT NOT NULL, company_name TEXT, company_cui TEXT, notes TEXT, newsletter INTEGER DEFAULT 0, items_json TEXT NOT NULL, subtotal REAL NOT NULL, shipping REAL NOT NULL, total REAL NOT NULL, awb TEXT, admin_note TEXT, awb_notified_at TEXT )",
 "CREATE INDEX IF NOT EXISTS orders_created ON orders(created_at)",
 "CREATE TABLE IF NOT EXISTS login_attempts (ip TEXT NOT NULL, ts TEXT NOT NULL)",
 "CREATE INDEX IF NOT EXISTS login_attempts_ip ON login_attempts(ip, ts)",
 "CREATE TABLE IF NOT EXISTS stock (sku TEXT PRIMARY KEY, qty INTEGER NOT NULL)",
 "CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL, exp TEXT)",
 "CREATE TABLE IF NOT EXISTS login_tokens (hash TEXT PRIMARY KEY, email TEXT NOT NULL, ip TEXT, created_at TEXT NOT NULL, expires_at TEXT NOT NULL, used_at TEXT)",
 "CREATE INDEX IF NOT EXISTS login_tokens_created ON login_tokens(created_at)",
 "CREATE INDEX IF NOT EXISTS orders_email ON orders(email COLLATE NOCASE)"
];
// Coloane adăugate ulterior (pe o bază existentă ALTER dă eroare dacă există deja: o ignorăm).
const COLUMNS = ['locker_json TEXT', 'awb_status TEXT', 'awb_checked_at TEXT'];
let ready = null;
export async function onRequest(ctx) {
  if (ctx.env.DB && /^\/api\//.test(new URL(ctx.request.url).pathname)) {
    if (!ready) ready = ctx.env.DB.batch(SCHEMA.map(s => ctx.env.DB.prepare(s)))
      .then(() => Promise.all(COLUMNS.map(c => ctx.env.DB.prepare('ALTER TABLE orders ADD COLUMN ' + c).run().catch(() => null))))
      .catch(e => { ready = null; throw e; });
    await ready;
  }
  return ctx.next();
}
