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
 (r'^Snz-CopiiCupcake(S|M|L)$', 'k-cupcake'), (r'^Snz-WineTime(S|M|L)$', 'winetime'), (r'^Snz-Caine(S|M|L)$', 'caine'),
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

def main(xlsx):
    ws = openpyxl.load_workbook(xlsx)['Oferte']
    rows = [r for r in ws.iter_rows(values_only=True)][5:]
    prods, unmatched, emag_price = {}, [], {}
    for r in rows:
        name, code, price = r[0], r[4], r[7]
        if not code: continue
        for rx, key in RULES:
            m = re.match(rx, str(code))
            if not m: continue
            g = m.groups()
            color = COLOR.get(g[0]) if len(g) == 2 or key == 'shea' else None
            size = g[-1] if key != 'shea' else 'U'
            emag_price.setdefault(key, []).append(price)
            prods.setdefault(key, []).append(dict(size=size, range='' if size == 'U' and key == 'shea' else size_range(name), color=color or '', sku=str(code), stock=None, inStock=True))
            break
        else:
            if 'nz' in str(code) or 'Bling' in str(code): unmatched.append(code)
    old = {p['slug']: p for p in json.load(open(os.path.join(ROOT, 'data/products.json'), encoding='utf-8'))} if os.path.exists(os.path.join(ROOT, 'data/products.json')) else {}
    out = []
    for i, (key, vs) in enumerate(sorted(prods.items(), key=lambda kv: list(MODELS).index(kv[0]))):
        nm, slug, cat, col, price = MODELS[key]
        vs.sort(key=lambda v: (v['color'], ORDER.get(v['size'], 5)))
        colors = []
        for v in vs:
            if v['color'] and v['color'] not in [c['name'] for c in colors]: colors.append(dict(name=v['color'], hex=HEX.get(v['color'], ''), image=''))
        prev = old.get(slug, {})
        out.append(dict(sku='SNZ-' + key.upper(), slug=slug, name=nm, category=cat, categoryName=CAT[cat], sub=col,
            price=price or prev.get('price') or STD, oldPrice=None, inStock=True, stock=None, short=prev.get('short', ''), description=prev.get('description', ''),
            images=prev.get('images', []), weight=0.3, featured=prev.get('featured', False), featuredOrder=prev.get('featuredOrder', 0),
            oldUrl=prev.get('oldUrl') or (slug + '.html'), colors=colors, sizes=vs))
        print(f'{key:12} {len(vs):2} var  eMAG campanie: {sorted(set(emag_price[key]))}  site: {out[-1]["price"]}')
    json.dump(out, open(os.path.join(ROOT, 'data/products.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(out), 'modele,', sum(len(p['sizes']) for p in out), 'variante')
    if unmatched: print('NEPOTRIVITE:', unmatched)

if __name__ == '__main__':
    main(sys.argv[1])
