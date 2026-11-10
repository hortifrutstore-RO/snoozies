# snoozies.ro — site static pe Cloudflare Pages

Același schelet ca magazin-horticol.ro, cu design Snoozies și **mărimi pe produs** (fiecare mărime are codul `SKU-MĂRIME`, stoc propriu în D1, apare în coș, comandă și email). Plata: doar ramburs.

## Structură
- `data/products.json` — produsele (preț, mărimi și stoc pe mărime, colecție, poze, descriere).
- `data/site.json` — texte, banner, transport, date firmă, sinonime pentru căutare, ID-uri Google.
- `templates/` — paginile (Jinja2). `content/` — paginile legale și de informații.
- `public/` — CSS, JS, fonturi, poze (`img/p/` produse, `img/site/` bannere).
- `functions/api/order.js` — primește comenzile, recalculează prețurile pe server, salvează în D1, trimite emailuri.
- `schema.sql` — tabela de comenzi.

## Generare
```
pip install jinja2 bleach
python3 build/build.py        # -> dist/
```

## Panoul de administrare (/admin/)
Comenzi (status, AWB), produse (preț, preț tăiat, stoc, poze, descriere, carusel, produse noi), prima pagină (bandă, banner, avantaje, bandă Barnel, categorii, transport, Google), căutare (căutate des, sinonime).
- Autentificare: parolă + cod din aplicația de autentificare (2FA), max. 5 încercări / 15 min, sesiune 12 h.
- Salvarea scrie în depozitul GitHub (`data/*.json`, `public/img/`), iar Cloudflare Pages reconstruiește site-ul automat în 1–2 minute. Fiecare salvare e un commit, deci orice modificare se poate anula.
- Comenzile stau în baza D1 și se văd imediat.

Configurare acces: deschide `/admin/configurare.html` (generează în browser parola criptată, codul QR pentru 2FA și cheia de sesiune) sau rulează `python3 tools/setup_admin.py` → afișează `ADMIN_PASSWORD_HASH`, `ADMIN_TOTP_SECRET`, `SESSION_SECRET` și salvează codul QR de scanat în aplicația de autentificare.

## Publicare (o singură dată)
0. Depozit privat pe GitHub cu acest folder. În Cloudflare Pages: Connect to Git, build command `pip install jinja2 bleach && python3 build/build.py`, output `dist`.
   Token GitHub „fine-grained”, doar pentru acest depozit, permisiunea Contents: Read and write → secretele `GITHUB_TOKEN`, `GITHUB_REPO` (utilizator/depozit), `GITHUB_BRANCH` (main).
1. Cont Cloudflare → Workers & Pages → Create → Pages → upload sau conectare la Git.
2. `npx wrangler d1 create snoozies-comenzi` → pune `database_id` în `wrangler.toml`.
3. `npx wrangler d1 execute snoozies-comenzi --remote --file schema.sql`
4. `npx wrangler pages deploy dist`
5. Secrete (Settings → Variables): `ADMIN_PASSWORD_HASH`, `ADMIN_TOTP_SECRET`, `SESSION_SECRET`, `GITHUB_TOKEN`, `GITHUB_REPO`, `GITHUB_BRANCH`, `RESEND_API_KEY`, `MAIL_FROM`, `NOTIFY_EMAIL`, `BANK_DETAILS`.
6. Custom domain: snoozies.ro și www. Email Routing: info@ → Gmail.

## Local
```
npx wrangler d1 execute snoozies-comenzi --local --file schema.sql
npx wrangler pages dev dist
```

## Sameday (AWB și easybox)
- Secrete în Cloudflare: `SAMEDAY_USER`, `SAMEDAY_PASS` (userul de API primit de la Sameday). Opțional `SAMEDAY_API=https://sameday-api.demo.zitec.com` pentru serverul lor de test (cu userul de test) și `SAMEDAY_LOCKER_CLIENT_ID` dacă Sameday îți dă un clientId propriu pentru hartă.
- Fără ele, site-ul merge ca înainte: easybox scris de mână, AWB introdus manual.
- Cu ele: la comandă apare harta oficială de easybox; în panou, butonul „Emite AWB Sameday” (serviciul 24H la adresă, Locker NextDay la easybox, PUDO la punctele Sameday), eticheta PDF A6/A4, anularea AWB-ului și verificarea automată a livrării la deschiderea panoului.
- Serviciile și punctul de ridicare se citesc din contul Sameday (păstrate 24 h). Greutatea implicită: `shipping.weightPerItem` × bucăți, modificabilă la emitere.
- Codul e în `functions/_lib/sameday.js`, `functions/api/admin/orders/[id]/awb.js`, `label.js`, `functions/api/admin/sameday/`, `functions/api/easybox.js` — același pe magazin-horticol.ro.
