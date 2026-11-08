// Variante: fiecare combinație culoare + mărime a unui produs are propriul cod (de obicei codul de pe eMAG),
// folosit în coș, comenzi și stoc. Fără cod explicit: sku-ul produsului + "-" + mărimea.
export const vsku = (p, s) => s.sku || `${p.sku}-${s.color ? s.color + '-' : ''}${s.size}`;
export const vlabel = (p, s) => `${p.name} – ${[s.color, s.size && s.size !== 'U' ? 'mărimea ' + s.size + (s.range ? ' (' + s.range + ')' : '') : ''].filter(Boolean).join(', ')}`;
export function variants(p) {
  if (!Array.isArray(p.sizes) || !p.sizes.length) return [{ sku: p.sku, name: p.name, stock: p.stock ?? null, inStock: !!p.inStock, ref: p }];
  return p.sizes.map(s => ({ sku: vsku(p, s), name: vlabel(p, s), stock: s.stock ?? null, inStock: !!s.inStock, ref: s }));
}
// După o schimbare de stoc, produsul e „în stoc” dacă măcar o variantă e disponibilă.
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
