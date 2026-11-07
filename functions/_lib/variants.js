// Mărimi: fiecare mărime a unui produs are propriul cod (sku-ul produsului + "-" + mărimea), folosit în coș, comenzi și stoc.
export const vsku = (p, s) => `${p.sku}-${s.size}`;
export function variants(p) {
  if (!Array.isArray(p.sizes) || !p.sizes.length) return [{ sku: p.sku, name: p.name, stock: p.stock ?? null, inStock: !!p.inStock, ref: p }];
  return p.sizes.map(s => ({ sku: vsku(p, s), name: `${p.name} – mărimea ${s.size}`, stock: s.stock ?? null, inStock: !!s.inStock, ref: s }));
}
// După o schimbare de stoc pe mărimi, produsul e „în stoc” dacă măcar o mărime e disponibilă.
export function refreshInStock(p) {
  if (Array.isArray(p.sizes) && p.sizes.length) p.inStock = p.sizes.some(s => s.inStock);
}
// Aplică stocul viu (sku -> bucăți) pe un produs; întoarce true dacă s-a schimbat ceva.
export function applyLive(p, live) {
  let changed = false;
  for (const v of variants(p)) if (v.sku in live) {
    const q = live[v.sku], ins = q > 0;
    if (v.ref.stock !== q || v.ref.inStock !== ins) { v.ref.stock = q; v.ref.inStock = ins; changed = true; }
  }
  if (changed) refreshInStock(p);
  return changed;
}
