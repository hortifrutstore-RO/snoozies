"""Generează site-ul static în dist/ din data/*.json, templates/ și content/.
Rulare: python3 build/build.py"""
import json, os, shutil, datetime, re, html
from jinja2 import Environment, FileSystemLoader, select_autoescape
import bleach

def split_desc(h):
    h = re.sub(r'<strong>[^<]*ideali pentru:\s*</strong>', '', h or '')
    h = re.sub(r'<br\s*/?>', '\n', h)
    paras = [re.sub(r'\s+', ' ', x).strip() for x in re.split(r'</?p>|\n', h)]
    paras = [x for x in paras if re.sub(r'<[^>]+>|&nbsp;', '', x).strip()]
    lead, checks, more = [], [], []
    for x in paras:
        plain = re.sub(r'<[^>]+>', '', x).strip()
        if plain.startswith('✔') or plain.startswith('✓'):
            body = plain.lstrip('✔✓ ').strip()
            m = re.match(r'(.{3,60}?)\s+[–—-]\s+(.+)', body)
            checks.append(dict(t=m.group(1).rstrip(':'), d=m.group(2)) if m else dict(t='', d=body))
        elif re.fullmatch(r'<strong>[^<]{0,80}</strong>', x) and not lead: continue  # titluri de tip „Papuci de casa pufosi Snoozies”
        elif len(lead) < 1 and len(plain) > 40: lead.append(x)
        else: more.append(x)
    if len(checks) < 2:  # fără listă în descriere: avantajele menționate în text
        low = re.sub(r'<[^>]+>', ' ', h or '').lower()
        found = [('Interior pufos și călduros', 'blăniță moale care ține picioarele calde', ('blan', 'plus', 'pufos')),
                 ('Talpă antiderapantă', 'inserții din silicon, pentru siguranță pe orice podea', ('antiderapant', 'silicon')),
                 ('Exterior textil fin', 'plăcut la atingere și rezistent', ('textil',)),
                 ('Se spală la mașină', 'își păstrează forma și moliciunea', ('spala', 'spală'))]
        checks += [dict(t=a, d=b) for a, b, keys in found if any(k in low for k in keys) and not any(a.split()[0].lower() in (c['t'] or '').lower() for c in checks)]
    return lead, checks, more

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
site = json.load(open(os.path.join(ROOT, 'data/site.json'), encoding='utf-8'))
products = json.load(open(os.path.join(ROOT, 'data/products.json'), encoding='utf-8'))
V = datetime.datetime.now().strftime('%Y%m%d%H%M')

def lei(n):
    s = f"{n:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return s + ' lei'

env = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates')), autoescape=select_autoescape(['html']))
env.filters['lei'] = lei
JUDETE = ["Alba","Arad","Argeș","Bacău","Bihor","Bistrița-Năsăud","Botoșani","Brașov","Brăila","București","Buzău","Caraș-Severin","Călărași","Cluj","Constanța","Covasna","Dâmbovița","Dolj","Galați","Giurgiu","Gorj","Harghita","Hunedoara","Ialomița","Iași","Ilfov","Maramureș","Mehedinți","Mureș","Neamț","Olt","Prahova","Satu Mare","Sălaj","Sibiu","Suceava","Teleorman","Timiș","Tulcea","Vaslui","Vâlcea","Vrancea"]
sg = (site.get('sizeGuide') or '').strip()
if sg and '<' not in sg: sg = ''.join(f'<p>{html.escape(l)}</p>' for l in sg.splitlines() if l.strip())
site['sizeGuide'] = bleach.clean(sg, tags=['p','br','ul','ol','li','strong','table','tbody','tr','td','th'], attributes={}, strip=True)
def img_size(path):
    # dimensiunile unei poze PNG/JPEG fără biblioteci externe
    try:
        b = open(path, 'rb').read()
        if b[:8] == b'\x89PNG\r\n\x1a\n': return int.from_bytes(b[16:20], 'big'), int.from_bytes(b[20:24], 'big')
        i = 2
        while i < len(b):
            if b[i] != 0xFF: i += 1; continue
            m = b[i + 1]
            if m in (0xC0, 0xC1, 0xC2): return int.from_bytes(b[i + 7:i + 9], 'big'), int.from_bytes(b[i + 5:i + 7], 'big')
            i += 2 + int.from_bytes(b[i + 2:i + 4], 'big')
    except Exception: pass
    return None
for r in site.get('reviewShots', []):
    wh = img_size(os.path.join(ROOT, 'public', r['image'].lstrip('/')))
    if wh: r['w'], r['h'] = round(wh[0] * .88), round(wh[1] * .88)
COLS = ['Magia Crăciunului', 'Iubitori de animăluțe', 'Mici plăceri', 'Pufoși ca un nor']
base = dict(site=site, v=V, year=datetime.date.today().year)

for p in products:
    p['description'] = bleach.clean(p.get('description') or '', tags=['p','br','ul','ol','li','strong','h3','h4','table','tbody','tr','td','th'], attributes={}, strip=True)
    p['off'] = round((1 - p['price'] / p['oldPrice']) * 100) if p.get('oldPrice') else 0
    if not p.get('images'): p['images'] = ['fara-poza.jpg']  # până se încarcă pozele
    p['desc_lead'], p['desc_checks'], p['desc_more'] = split_desc(p.get('description'))
    p['sizes'] = p.get('sizes') or []
    p['colors'] = p.get('colors') or []
    for z in p['sizes']:
        z.setdefault('color', '')
        z['sku'] = z.get('sku') or f"{p['sku']}-{z['color'] + '-' if z['color'] else ''}{z['size']}"
    # culorile care au măcar o variantă; poza culorii trece prima în galerie la alegere
    p['colorNames'] = [c['name'] for c in p['colors']]
    # culoarea fiecărei poze: de la poza culorii până la poza următoarei culori
    starts = sorted((p['images'].index(c['image']), c['name']) for c in p['colors'] if c.get('image') in p['images'])
    p['imgColor'] = []
    for i, _ in enumerate(p['images']):
        cur = ''
        for st, nm in starts:
            if i >= st: cur = nm
        p['imgColor'].append(cur)
    if p['sizes']: p['inStock'] = any(z.get('inStock', True) for z in p['sizes'])

def vsku(p, z): return z.get('sku') or f"{p['sku']}-{z['color'] + '-' if z.get('color') else ''}{z['size']}"
def vlabel(p, z):
    bits = [z.get('color') or '', ('mărimea ' + z['size'] + (f" ({z['range']})" if z.get('range') else '')) if z['size'] != 'U' else '']
    return p['name'] + ' – ' + ', '.join(b for b in bits if b)
def variants(p):
    if not p['sizes']: return [dict(sku=p['sku'], name=p['name'], size=None, inStock=p['inStock'])]
    return [dict(sku=vsku(p, z), name=vlabel(p, z), size=z['size'], color=z.get('color') or '', inStock=z.get('inStock', True)) for z in p['sizes']]

def write(path, htmltext):
    out = os.path.join(DIST, path.strip('/'), 'index.html') if not path.endswith('.html') else os.path.join(DIST, path.strip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(htmltext)

def render(tpl, path, **kw):
    write(path, env.get_template(tpl).render(**base, path=path, **kw))

if os.path.exists(DIST): shutil.rmtree(DIST)
shutil.copytree(os.path.join(ROOT, 'public'), DIST)

# Prima pagină
featured = sorted([p for p in products if p.get('featured') and p['inStock']], key=lambda p: p.get('featuredOrder') or 0)[:8] or [p for p in products if p['inStock']][:8]
cats = []
for c in site['categories']:
    items = [p for p in products if p['category'] == c['slug']]
    img = c.get('image') or ('/img/p/' + items[0]['images'][0] if items else '')
    if items: cats.append(dict(slug=c['slug'], name=c['name'], count=len(items), img=img, contain=False))
render('home.html', '/', featured=featured, cats=cats)

# Categorii
for c in site['categories']:
    items = [p for p in products if p['category'] == c['slug']]
    items.sort(key=lambda p: (not p['inStock'], -p['off'], p['name']))
    subs = {}
    for p in items:
        if p.get('sub'): subs[p['sub']] = subs.get(p['sub'], 0) + 1
    prices = [p['price'] for p in items] or [0]
    render('category.html', f"/categorie/{c['slug']}/", cat=c, products=items, active_cat=c['slug'],
           subs=[dict(name=k, n=v) for k, v in sorted(subs.items(), key=lambda x: (COLS.index(x[0]) if x[0] in COLS else 99, -x[1]))],
           pmin=int(min(prices)), pmax=int(max(prices)) + 1)

# Produse
for p in products:
    rel = [r for r in products if r['category'] == p['category'] and r['sku'] != p['sku'] and r['inStock']]
    rel.sort(key=lambda r: (r.get('sub') != p.get('sub'), abs(r['price'] - p['price'])))
    if len(rel) < 4: rel += [r for r in products if r['category'] != p['category'] and r['inStock']][:4 - len(rel)]
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p['name'], "sku": p['sku'],
          "image": [site['url'] + '/img/p/' + i for i in p['images']],
          "description": re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', p['description'])))[:500],
          "brand": {"@type": "Brand", "name": "Snoozies"},
          "offers": {"@type": "Offer", "price": f"{p['price']:.2f}", "priceCurrency": "RON",
                     "availability": "https://schema.org/InStock" if p['inStock'] else "https://schema.org/OutOfStock",
                     "url": f"{site['url']}/produs/{p['slug']}/"}}
    render('product.html', f"/produs/{p['slug']}/", p=p, related=rel[:4], active_cat=p['category'],
           ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'))

render('search.html', '/cautare/')
render('cart.html', '/cos/', judete=JUDETE)

# Pagini de text
for fn in sorted(os.listdir(os.path.join(ROOT, 'content'))):
    raw = open(os.path.join(ROOT, 'content', fn), encoding='utf-8').read()
    title, body = raw.split('\n', 1)
    body = env.from_string(body).render(**base)
    slug = fn[:-5]
    render('page.html', f'/{slug}/', page=dict(title=title.strip(), body=body, noindex=slug == 'comanda-plasata'))
open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8').write(env.get_template('page.html').render(**base, path='/404', page=dict(
    title='Pagina nu există', noindex=True,
    body='<p>Pagina căutată nu mai există sau a fost mutată. Caută produsul în bara de sus sau mergi la <a href="/">prima pagină</a>.</p>')))

# Index pentru căutare și coș (public, doar date de afișare)
os.makedirs(os.path.join(DIST, 'data'), exist_ok=True)
idx = [dict(sku=p['sku'], slug=p['slug'], name=p['name'], cat=p['categoryName'], catSlug=p['category'], sub=p.get('sub'),
            price=p['price'], old=p.get('oldPrice'), off=p['off'], inStock=p['inStock'], img=p['images'][0], featured=p.get('featured', False),
            sizes=[dict(s=z['size'], c=z.get('color', ''), r=z.get('range', ''), sku=v['sku'], n=v['name'], i=v['inStock']) for z, v in zip(p['sizes'], variants(p))] if p['sizes'] else None)
       for p in products]
json.dump(idx, open(os.path.join(DIST, 'data/search.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# Catalog pentru funcția de comenzi (prețurile reale, verificate pe server)
os.makedirs(os.path.join(ROOT, 'functions/api'), exist_ok=True)
def vimg(p, v):
    c = v.get('color')
    if c and p.get('imgColor') and c in p['imgColor']: return '/img/p/' + p['images'][p['imgColor'].index(c)]
    return '/img/p/' + p['images'][0] if p['images'] else ''
def vopt(p, v): return v['name'][len(p['name']):].lstrip(' –') if v['name'].startswith(p['name']) else ''
json.dump({v['sku']: dict(name=v['name'], model=p['name'], opt=vopt(p, v), img=vimg(p, v), url='/produs/' + p['slug'] + '/', price=p['price'], inStock=v['inStock']) for p in products for v in variants(p)},
          open(os.path.join(ROOT, 'functions/api/_catalog.json'), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(dict(freeOver=site['shipping']['freeOver'], cost=site['shipping']['cost'], easyboxCost=site['shipping'].get('easyboxCost', site['shipping']['cost']), email=site['contact']['email'], name=site['name'], carrier=site['shipping']['carrier'], phone=site['contact'].get('phone',''), whatsapp=site['contact'].get('whatsapp',''), company=site['company'], trackingUrl=site['shipping'].get('trackingUrl') or 'https://sameday.ro/status-colet/?awb={awb}'),
          open(os.path.join(ROOT, 'functions/api/_shop.json'), 'w', encoding='utf-8'), ensure_ascii=False)

# Redirecționări 301 de la adresele Magento
red = ['# Generat automat - adresele vechi Magento (snoozies.ro)']
for p in products:
    red.append(f"/{p['slug']}.html /produs/{p['slug']}/ 301")
    if p.get('oldUrl') and p['oldUrl'] != p['slug'] + '.html': red.append(f"/{p['oldUrl'].lstrip('/')} /produs/{p['slug']}/ 301")
for extra in json.load(open(os.path.join(ROOT, 'data/redirects_extra.json'), encoding='utf-8')) if os.path.exists(os.path.join(ROOT, 'data/redirects_extra.json')) else []:
    red.append(f"{extra[0]} {extra[1]} 301")
red += ['/checkout/* /cos/ 301', '/customer/* / 301', '/catalogsearch/* /cautare/ 301', '/index.php/* / 301']
open(os.path.join(DIST, '_redirects'), 'w').write('\n'.join(red) + '\n')

open(os.path.join(DIST, '_headers'), 'w').write("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://*.sameday.ro; connect-src 'self' https://*.google-analytics.com https://*.googletagmanager.com https://*.google.com https://*.sameday.ro; img-src 'self' data: blob: https://*.google-analytics.com https://*.googletagmanager.com https://*.google.com https://*.doubleclick.net https://*.sameday.ro; style-src 'self' 'unsafe-inline' https://*.sameday.ro; font-src 'self' https://*.sameday.ro; frame-src https://*.doubleclick.net https://*.google.com https://*.sameday.ro; base-uri 'self'; form-action 'self'
/admin/*
  Cache-Control: no-store
  X-Robots-Tag: noindex, nofollow
/api/*
  Cache-Control: no-store
/fonts/*
  Cache-Control: public, max-age=31536000, immutable
/img/*
  Cache-Control: public, max-age=2592000
""")

urls = ['/'] + [f"/categorie/{c['slug']}/" for c in site['categories']] + [f"/produs/{p['slug']}/" for p in products] + \
       ['/livrare-si-plata/', '/retur/', '/termeni-si-conditii/', '/confidentialitate/', '/cookie-uri/', '/contact/']
open(os.path.join(DIST, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'<url><loc>{site["url"]}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
open(os.path.join(DIST, 'robots.txt'), 'w').write(f"User-agent: *\nDisallow: /cos/\nDisallow: /cautare/\nDisallow: /comanda-plasata/\nDisallow: /api/\nDisallow: /admin/\nSitemap: {site['url']}/sitemap.xml\n")
print('OK', len(products), 'produse ->', DIST)
