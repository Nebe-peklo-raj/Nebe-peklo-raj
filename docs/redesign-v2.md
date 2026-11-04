# Redesign webu podle návrhu V2 (listopad 2026)

Web je převedený do vizuálu z PDF „nebe_peklo_raj_web_v2“. Obsah zůstal zachovaný, mění se rozložení a vzhled.

## Odsouhlasená rozhodnutí

| Téma | Rozhodnutí |
|---|---|
| Úvod | Horní část podle V2. Sekce Jak to funguje, Otevřeno pro všechny a Pro koho to je zůstaly, místo karet mají tenké linky. Ukázka FAQ je nahrazená odkazem. Formulář Tally a text pod ním se nezměnily. |
| Tmavý režim | Zrušený, web je jen světlý. |
| Mapa a profily | Ze skutečného GPX (`scripts/route_svg.py`), bez vymyšlených vrstevnic. |
| Koridor | „±150 m“ / „150 m na každou stranu“ (PDF psalo „150 m šířka“, což neodpovídá pravidlům). |
| Žebříček | Záložky variant fungují, filtry Styl a Kategorie jsou vypnuté až do spuštění. |
| Pravidla | Současných 8 bodů beze změny, úplné znění je vidět pořád. Otázky z Pravidel jsou nahrazené odkazem na FAQ (všechny tam jsou). |
| FAQ | Všech 34 otázek v 6 tématech zůstalo na stránce. Postranní seznam vede na kotvy. |
| Menu | Tlačítko s `aria-expanded` a `aria-controls`, Esc zavře a vrátí fokus, klik na odkaz zavře. Bez JS jsou odkazy vidět rovnou. Hlavička není připevněná. |
| GPX | Místo tlačítka „Stáhnout GPX“ je neaktivní popisek „GPX ke stažení · jaro 2027“ s odkazem na waitlist. |
| Kontakt | Čtyři dlaždice otevírají e-mail s předvyplněným předmětem. |
| Patička | Logová modrá `#194FA2` s inverzní Pečetí. |
| Tlačítka | Hranatá, jedna linka, text verzálkami. |

## Texty: rozdíly mezi PDF a webem

Krátké texty z PDF jsou převzaté tam, kde nemění význam: perex v hero („z Orlických hor“), eyebrow nad nadpisy, perexy Pravidel, FAQ a Kontaktu, titulek na 404.

Ponechaný byl text webu, kde by PDF změnilo význam nebo vynechalo důležitou informaci:

- Žebříček: „zápis bude **placený**“ a „3D tištěná medaile ve tvaru puzzle“ (PDF: „zápis bude možný“, „pamětní medaile“).
- Koridor: „150 m na každou stranu“ (PDF: „150 m šířka koridoru“).
- Pravidla: 8 bodů shrnutí (PDF mělo 5 přeformulovaných bodů a vynechávalo „Jen po svých“ a „Na vlastní riziko“).
- FAQ: otázky a odpovědi z webu (PDF mělo jiné formulace a jen 5 témat). Otázka z PDF „Kdy se platí zápis do žebříčku?“ nebyla přidaná, odpověď zatím neexistuje.
- Kontakt: z PDF je převzatý úvodní text. V části „Kdo za tím stojí“ zůstala formulace webu („Vymyslel trasu, napsal pravidla“), z PDF přibylo „ani anonymní tým“.

Popisky stránek PDF v pravém dolním rohu („01 / ÚVOD“ atd.) patří k PDF, na web se nepřebírají.

## Omezení

- **Waitlist** běží přes externí službu Tally. Když se Tally nenačte, zobrazí se odkaz na formulář v novém okně.
- **Žebříček** zatím nemá data ani backend. Záložky jen přepínají prázdné tabulky, filtry jsou vypnuté. Nahrávání GPX přijde s ASP.NET verzí.
- **GPX** se zatím nestahuje. Předběžné `data/trasa.gpx` slouží jen ke generování grafiky a testům a na web se nenasazuje.
- **404.html** používá absolutní cesty `/Nebe-peklo-raj/…`, protože ji GitHub Pages servíruje na libovolné adrese. Při přesunu na vlastní doménu nebo ASP.NET je potřeba cesty upravit.
- Hlavička a patička jsou v každé stránce zkopírované (web nemá build).

## Testy

- Screenshoty všech 8 stránek v šířkách 360, 390, 430, 768, 1366 a 1920 px (Playwright, Chromium): žádný horizontální přetok, žádné chyby JS v konzoli.
- Odkazy: 281 interních odkazů a kotev, všechny existují, žádné duplicitní `id`.
- Klávesnice: menu (Enter, Esc, fokus), záložky (šipky), skip link. Bez JS: menu viditelné, všechny tři panely žebříčku viditelné.
- Kontrast: text i ovládací prvky splňují WCAG AA (tlumený text 6,0:1 na šedé, fokus 12:1 na bílé).
- `html-validate`: bez chyb kromě stylu zápisu doctype a starších atributů ve vloženém kódu Tally.
