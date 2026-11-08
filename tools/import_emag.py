# Construiește data/products.json din exportul de oferte eMAG (xlsx).
# Un produs pe site = un model; culorile și mărimile devin variante cu codul de pe eMAG.
# Rulare: python3 tools/import_emag.py export-emag.xlsx
import sys, re, json, os
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = {'femei': 'Femei', 'barbati': 'Bărbați', 'copii-si-bebelusi': 'Copii și bebeluși', 'sosete': 'Șosete'}
XMAS, ANIM, MICI, NOR = 'Magia Crăciunului', 'Iubitori de animăluțe', 'Mici plăceri', 'Pufoși ca un nor'

# regex pe codul eMAG -> (cheie model, culoare sau None, mărime)
# model: cheie -> (nume, slug, categorie, colecție, preț site, preț vechi site sau None)
STD = 51.99  # 54,86 lei pe eMAG − 5%
MODELS = {
 'chevron':   ('Papuci de casă Snoozies Chevron', 'papuci-de-casa-femei-snoozies-chevron', 'femei', NOR, None),
 'ren':       ('Papuci de casă Snoozies Ren', 'papuci-de-casa-snoozies-ren', 'femei', XMAS, STD),
 'merry':     ('Papuci de casă Snoozies Crăciun Fericit', 'papuci-de-casa-snoozies-craciun-fericit', 'femei', XMAS, STD),
 'esquad':    ('Papuci de casă Snoozies Echipa Elf', 'papuci-de-casa-snoozies-echipa-elf', 'femei', XMAS, STD),
 'frosty':    ('Papuci de casă Snoozies Feeling Frosty', 'papuci-de-casa-snoozies-feeling-frosty', 'femei', XMAS, STD),
 'snowwine':  ('Papuci de casă Snoozies Snow Wine', 'papuci-de-casa-snoozies-snow-wine', 'femei', XMAS, STD),
 'snowgood':  ('Papuci de casă Snoozies Snow Good', 'papuci-de-casa-femei-snoozies-snow-good', 'femei', XMAS, STD),
 'bemerry':   ('Papuci de casă Snoozies Be Merry', 'papuci-de-casa-femei-snoozies-be-merry', 'femei', XMAS, STD),
 'xelf':      ('Papuci de casă Snoozies Christmas Elf', 'papuci-de-casa-femei-snoozies-christmas-elf', 'femei', XMAS, STD),
 'whitex':    ('Papuci de casă Snoozies White Christmas', 'papuci-de-casa-femei-snoozies-white-christmas', 'femei', XMAS, STD),
 'meowy':     ('Papuci de casă Snoozies Meowy Christmas', 'papuci-de-casa-snoozies-meowy-christmas', 'femei', XMAS, STD),
 'snowmies':  ('Papuci de casă Snoozies Chilling with my Snowmies', 'papuci-de-casa-snoozies-chilling-with-my-snowmies', 'femei', XMAS, STD),
 'chilling':  ('Papuci de casă Snoozies Just Chilling', 'papuci-de-casa-femei-snoozies-just-chilling', 'femei', MICI, STD),
 'choco':     ('Papuci de casă Snoozies Chocolate makes me happy', 'papuci-de-casa-snoozies-ciocolata', 'femei', MICI, STD),
 'winetime':  ('Papuci de casă Snoozies Wine Time', 'papuci-de-casa-snoozies-any-time-is-wine-time', 'femei', MICI, STD),
 'ampm':      ('Papuci de casă Snoozies AM-PM', 'papuci-de-casa-snoozies-am-pm', 'femei', MICI, STD),
 'catitude':  ('Papuci de casă Snoozies Catitude', 'papuci-de-casa-snoozies-catitude', 'femei', ANIM, STD),
 'catlady':   ('Papuci de casă Snoozies Cat Lady', 'papuci-de-casa-snoozies-cat-lady-36-37', 'femei', ANIM, STD),
 'caine':     ('Papuci de casă Snoozies Home is where my dog is', 'papuci-de-casa-snoozies-home-is-where-my-dog-is', 'femei', ANIM, STD),
 'buburuza':  ('Papuci de casă Snoozies Buburuză', 'papuci-de-casa-snoozies-buburuza', 'femei', ANIM, STD),
 'elefant':   ('Papuci de casă Snoozies Elefant', 'papuci-de-casa-snoozies-elefant', 'femei', ANIM, STD),
 'bufnita':   ('Papuci de casă Snoozies Bufniță', 'papuci-de-casa-snoozies-bufnita', 'femei', ANIM, STD),
 'albinuta':  ('Papuci de casă Snoozies Albinuță', 'papuci-de-casa-snoozies-albinuta', 'femei', ANIM, STD),
 'sassy':     ('Papuci de casă Snoozies Sassy Slide', 'papuci-de-casa-snoozies-sassy-slide', 'femei', NOR, None),
 'bling':     ('Papuci de casă Snoozies Bling', 'papuci-de-casa-snoozies-bling', 'femei', NOR, None),
 'crosetati': ('Papuci de casă Snoozies Croșetați', 'papuci-de-casa-snoozies-crosetati', 'femei', NOR, None),
 'buline':    ('Papuci de casă Snoozies Buline', 'papuci-de-casa-snoozies-buline', 'femei', NOR, STD),
 'braduti':   ('Papuci de casă Snoozies Brăduți', 'papuci-de-casa-femei-snoozies-christmas-tree', 'femei', XMAS, STD),
 'fulg':      ('Papuci de casă Snoozies Fulg de nea', 'papuci-de-casa-femei-snoozies-snowflake', 'femei', XMAS, STD),
 'gnome':     ('Papuci de casă Snoozies Christmas Gnomes', 'papuci-de-casa-femei-snoozies-christmas-gnomes', 'femei', XMAS, STD),
 'hohoho':    ('Papuci de casă Snoozies Ho Ho Ho', 'papuci-de-casa-femei-snoozies-ho-ho-ho', 'femei', XMAS, STD),
 'b-fulg':    ('Papuci de casă bărbați Snoozies Fulg de nea', 'papuci-de-casa-barbati-snoozies-snowflake', 'barbati', XMAS, STD),
 'b-gnome':   ('Papuci de casă bărbați Snoozies Christmas Gnomes', 'papuci-de-casa-barbati-snoozies-christmas-gnomes', 'barbati', XMAS, STD),
 'b-hohoho':  ('Papuci de casă bărbați Snoozies Ho Ho Ho', 'papuci-de-casa-barbati-snoozies-ho-ho-ho', 'barbati', XMAS, STD),
 'b-luminite':('Papuci de casă bărbați Snoozies Luminițe', 'papuci-de-casa-barbati-snoozies-luminite', 'barbati', XMAS, STD),
 'b-craciun': ('Papuci de casă bărbați Snoozies Crăciun Fericit', 'papuci-de-casa-barbati-snoozies-craciun-fericit', 'barbati', XMAS, STD),
 'b-urs':     ('Papuci de casă bărbați Snoozies Urs Polar', 'papuci-de-casa-barbati-snoozies-urs-polar', 'barbati', XMAS, STD),
 'b-snowmies':('Papuci de casă bărbați Snoozies Chilling with my Snowmies', 'papuci-de-casa-barbati-snoozies-snowmies', 'barbati', XMAS, STD),
 'b-superdad':('Papuci de casă bărbați Snoozies Super Dad', 'papuci-de-casa-snoozies-super-dad', 'barbati', MICI, STD),
 'b-fish':    ('Papuci de casă bărbați Snoozies Fisherman', 'papuci-de-casa-snoozies-mens-fisherman', 'barbati', MICI, STD),
 'b-pig':     ('Papuci de casă bărbați Snoozies Chicken & Pig', 'papuci-de-casa-snoozies-chicken-and-pig', 'barbati', ANIM, STD),
 'b-elefant': ('Papuci de casă bărbați Snoozies Elefant', 'papuci-de-casa-barbati-snoozies-elefant', 'barbati', ANIM, STD),
 'bb-panda':  ('Botoșei bebeluși Snoozies Panda', 'papuci-de-casa-snoozies-bebelus-model-panda', 'copii-si-bebelusi', ANIM, None),
 'bb-caine':  ('Botoșei bebeluși Snoozies Cățel', 'papuci-de-casa-snoozies-bebelus-model-caine', 'copii-si-bebelusi', ANIM, None),
 'bb-oita':   ('Botoșei bebeluși Snoozies Oiță', 'papuci-de-casa-snoozies-bebelus-model-oita', 'copii-si-bebelusi', ANIM, None),
 'bb-maim':   ('Botoșei bebeluși Snoozies Maimuțică', 'papuci-de-casa-snoozies-bebelus-model-maimuta', 'copii-si-bebelusi', ANIM, None),
 'bb-urs':    ('Botoșei bebeluși Snoozies Ursuleț', 'papuci-de-casa-snoozies-bebelus-model-ursulet', 'copii-si-bebelusi', ANIM, None),
 'bb-pudel':  ('Botoșei bebeluși Snoozies Pudel', 'papuci-de-casa-snoozies-bebelus-model-pudel', 'copii-si-bebelusi', ANIM, None),
 'k-cupcake': ('Papuci de casă copii Snoozies Cupcake', 'papuci-de-casa-snoozies-copii-model-cupcake', 'copii-si-bebelusi', MICI, None),
 'shea':      ('Șosete termice pufoase Snoozies Shea', 'sosete-termice-pufoase-shea', 'sosete', NOR, 47.99),
}
RULES = [  # (regex pe cod, cheie model, grup culoare, grup mărime)
 (r'^Snz-Chevron(Alb|Visiniu|Albastru|Negru)(S|M|L|XL)$', 'chevron'),
 (r'^SnzChristmasTree(S|M|L)$', 'braduti'), (r'^SnzFemeiSnowflake(S|M|L)$', 'fulg'), (r'^SnzGnomeFemei(S|M|L)$', 'gnome'), (r'^SnzFemeiHoHo(S|M|L)$', 'hohoho'),
 (r'^SnzFulgBarb(S|M|L|XL)$', 'b-fulg'), (r'^SnzGnomeBarb(S|M|L|XL)$', 'b-gnome'), (r'^SnzBarbatiHoHo(S|M|L|XL)$', 'b-hohoho'),
 (r'^Snz-07Snow(XL)Barb$', 'b-snowmies'), (r'^Snz-06Elf(XL)$', 'b-elefant'),
 (r'^Snz-Reind(S|M|L)$', 'ren'), (r'^Snz-Merryx(S|M|L)$', 'merry'), (r'^Snz-Esquad(S|M|L)$', 'esquad'),
 (r'^Snz-LuminiteBarb(S|M|L|XL)$', 'b-luminite'), (r'^Snz-CraciunFericitBarb(S|M|L|XL)$', 'b-craciun'), (r'^Snz-UrsPolar(S|M|L|XL)$', 'b-urs'),
 (r'^Snz-Frosty(S|M|L)$', 'frosty'), (r'^Snz-SnowWine(S|M|L)$', 'snowwine'), (r'^Snz-SnowGood(S|M|L)$', 'snowgood'),
 (r'^Snz-BeMerry(S|M|L)$', 'bemerry'), (r'^Snz-WineELF(S|M|L)$', 'xelf'), (r'^Snz-WhiteChristmas(S|M|L)$', 'whitex'),
 (r'^Snz-JustChilling(S|M|L)$', 'chilling'), (r'^SnzSoseteShea(Albastru|Roz|Verde)$', 'shea'),
 (r'^Snz-Sassy(Orange|Roz|Negru|Maro)(S|M|L)$', 'sassy'), (r'^SnzMewowyChristmas(S|M|L)$', 'meowy'),
 (r'^(Gold|Red)Bling(S|M|L)$', 'bling'), (r'^Snz-Crosetati(Roz|Mov|Albastru)(S|M|L)$', 'crosetati'),
 (r'^Snz-Catitude(S|M|L)$', 'catitude'), (r'^Snz-Choco(S|M|L)$', 'choco'), (r'^SnzCat(?:Ldy|lady)(S|M|L)$', 'catlady'),
 (r'^Snz-Bebe[Pp]anda(S|M|L)$', 'bb-panda'), (r'^Snz-BebeCaine(S|M|L)$', 'bb-caine'), (r'^Snz-BebeOita(S|M|L)$', 'bb-oita'),
 (r'^Snz-BebeMaim(S|M|L)$', 'bb-maim'), (r'^Snz-BebeUrsulet(S|M|L)$', 'bb-urs'), (r'^Snz-BebePudel(S|M|L)$', 'bb-pudel'),
 (r'^Snz-CopiiCupcake(S|M|L)$', 'k-cupcake'), (r'^Snz-Wine[Tt]ime(S|M|L)$', 'winetime'), (r'^Snz-Caine(S|M|L)$', 'caine'),
 (r'^Snz-Superdad(S|M|L)$', 'b-superdad'), (r'^Snz-Buburuza(S|M|L)$', 'buburuza'),
 (r'^Snz-07Snowmies(S|M|L)$', 'snowmies'), (r'^Snz-07Snow(S|M|L)barb$', 'b-snowmies'),
 (r'^Snz-06Elf(S|M|L)$', 'elefant'), (r'^Snz-06Elf(S|M|L)men$', 'b-elefant'),
 (r'^Snz-08Lotsa(Blue|Gri|Pink|Mov)(S|M|L)$', 'buline'), (r'^Snz-03Buf(S|M|L)$', 'bufnita'), (r'^Snz-01AMPM(S|M|L)$', 'ampm'),
 (r'^Snz-04Fish(S|M|L)$', 'b-fish'), (r'^Snz-02pig(S|M|L)$', 'b-pig'), (r'^Snz-05Alb(S|M|L)$', 'albinuta'),
]
COLOR = {'Alb': 'Alb', 'Visiniu': 'Vișiniu', 'Albastru': 'Albastru', 'Negru': 'Negru', 'Roz': 'Roz', 'Verde': 'Verde', 'Orange': 'Portocaliu',
         'Maro': 'Maro', 'Gold': 'Auriu', 'Red': 'Roșu', 'Mov': 'Mov', 'Blue': 'Albastru', 'Gri': 'Gri', 'Pink': 'Roz'}
HEX = {'Alb': '#F4F1EA', 'Vișiniu': '#7A1F45', 'Albastru': '#4C6FA5', 'Negru': '#1F1B1A', 'Roz': '#F28DB2', 'Verde': '#8FBF9F', 'Portocaliu': '#F2A65A',
       'Maro': '#8A5A3C', 'Auriu': '#C9A646', 'Roșu': '#C8102E', 'Mov': '#A68BD1', 'Gri': '#9A9A9A'}
ORDER = {'S': 0, 'M': 1, 'L': 2, 'XL': 3, 'U': 9}

def size_range(name):
    m = re.search(r'(\d+)\s*-\s*(\d+)\s*luni', name)
    if m: return f'{m.group(1)}–{m.group(2)} luni'
    m = re.search(r'(\d{1,2}(?:[.,]5)?)\s*-\s*(\d{1,2}(?:[.,]5)?)', name)
    return f'{m.group(1)}–{m.group(2)}' if m else ''

def read_rows(paths):
    """Citește exporturile eMAG: „update-product” (foaia Template) și/sau oferte (foaia Oferte)."""
    rows = []
    for path in paths:
        wb = openpyxl.load_workbook(path)
        if 'Template' in wb.sheetnames:
            R = list(wb['Template'].iter_rows(values_only=True)); H = R[2]
            for r in R[5:]:
                d = dict(zip(H, r))
                if not d.get('part_number'): continue
                imgs = [d.get('main_image_url')] + [d.get(f'other_image_url{i}') for i in range(1, 6)]
                rows.append(dict(code=str(d['part_number']).strip(), name=d.get('name') or '', size=(d.get('Marime [original]: [6506]') or '').replace(' EU', '').strip(),
                    color=d.get('Culoare: [5401]') or '', desc=d.get('description') or '', images=[i for i in imgs if i], family=d.get('family_name') or '', price=None))
        elif 'Oferte' in wb.sheetnames:
            for r in list(wb['Oferte'].iter_rows(values_only=True))[5:]:
                if r[4]: rows.append(dict(code=str(r[4]).strip(), name=r[0] or '', size='', color='', desc='', images=[], family='', price=r[7]))
    return rows

def main(paths):
    prods, unmatched, info = {}, [], {}
    seen = set()
    for row in read_rows(paths):
        code = row['code']
        for rx, key in RULES:
            m = re.match(rx, code)
            if not m: continue
            g = m.groups()
            color = COLOR.get(g[0]) if len(g) == 2 or key == 'shea' else None
            size = g[-1] if key != 'shea' else 'U'
            rng = row['size'] if row['size'] and key != 'shea' else size_range(row['name'])
            rng = rng.replace('-', '–').replace(' luni', ' luni')
            if re.match(r'^\d+–\d+$', rng) and key.startswith('bb-'): rng += ' luni'
            inf = info.setdefault(key, dict(desc='', images={}, family=''))
            if row['desc'] and not inf['desc']: inf['desc'] = row['desc']
            if row['family'] and not inf['family']: inf['family'] = row['family']
            if row['images']: inf['images'].setdefault(color or '', row['images'])
            if code in seen: break
            seen.add(code)
            prods.setdefault(key, []).append(dict(size=size, range='' if key == 'shea' else rng, color=color or '', sku=code, stock=None, inStock=True))
            break
        else:
            if 'nz' in code or 'Bling' in code: unmatched.append(code)
    old = {p['slug']: p for p in json.load(open(os.path.join(ROOT, 'data/products.json'), encoding='utf-8'))} if os.path.exists(os.path.join(ROOT, 'data/products.json')) else {}
    out, imgmap = [], {}
    for key, vs in sorted(prods.items(), key=lambda kv: list(MODELS).index(kv[0])):
        nm, slug, cat, col, price = MODELS[key]
        vs.sort(key=lambda v: (v['color'], ORDER.get(v['size'], 5)))
        colors = []
        for v in vs:
            if v['color'] and v['color'] not in [c['name'] for c in colors]: colors.append(dict(name=v['color'], hex=HEX.get(v['color'], ''), image=''))
        fam = info[key]['family'].lower()
        if 'christmas fun' in fam or 'jingle' in fam: col = XMAS
        elif 'animal lovers' in fam: col = ANIM
        elif 'enjoy life' in fam: col = MICI
        prev = old.get(slug, {})
        desc = clean_desc(info[key]['desc']) or prev.get('description', '')
        out.append(dict(sku='SNZ-' + key.upper(), slug=slug, name=nm, category=cat, categoryName=CAT[cat], sub=col,
            price=price or prev.get('price') or STD, oldPrice=None, inStock=True, stock=None, short=prev.get('short', ''), description=desc,
            images=prev.get('images', []), weight=0.3, featured=prev.get('featured', False), featuredOrder=prev.get('featuredOrder', 0),
            oldUrl=prev.get('oldUrl') or (slug + '.html'), colors=colors, sizes=vs))
        imgmap[slug] = info[key]['images']
        print(f"{key:12} {len(vs):3} var  culori: {','.join(c['name'] for c in colors) or '-':30} familie eMAG: {info[key]['family'][:40]}")
    json.dump(out, open(os.path.join(ROOT, 'data/products.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(imgmap, open(os.path.join(ROOT, 'tools/emag_images.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(out), 'modele,', sum(len(p['sizes']) for p in out), 'variante')
    if unmatched: print('NEPOTRIVITE:', unmatched)

def clean_desc(h):
    if not h: return ''
    h = re.sub(r'<(/?)(?:b)>', r'<\1strong>', str(h))
    h = re.sub(r'<(?!/?(?:p|br|ul|ol|li|strong|h3|h4)\b)[^>]+>', '', h)
    h = re.sub(r'<(p|li|ul|ol|strong|h3|h4)\s[^>]*>', r'<\1>', h)
    return h.strip()

if __name__ == '__main__':
    main(sys.argv[1:])
