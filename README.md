# Nebe Peklo Ráj

FKT výzva z Nebeské Rybné přes Peklo do Českého ráje (aktuálně cca 155 km). Spuštění květen 2027.

Statický web (čisté HTML/CSS, bez buildu), hostovaný přes GitHub Pages. Později poběží na ASP.NET a soubory se přesunou do `wwwroot`.

## Stránky

| Soubor | Obsah |
|---|---|
| `index.html` | úvod s výškovým profilem, tři zastávky, varianty, jak to funguje, pro koho, waitlist (Tally) |
| `trasa.html` | body trasy se souřadnicemi, mapa a výškový profil, etapy, koridor, bezpečnost |
| `pravidla.html` | pravidla v1.2: shrnutí v 8 bodech, čas, styly, pauzy, GPX, historie změn |
| `zebricek.html` | připravujeme: záložky variant, zatím neaktivní filtry, prázdná tabulka |
| `kontakt.html` | kdo za tím stojí, kontakt, info pro média |
| `ochrana-udaju.html` | zásady ochrany osobních údajů k waitlistu |
| `faq.html` | časté otázky v 6 tématech |
| `404.html` | stránka nenalezena (odkazy s absolutní cestou `/Nebe-peklo-raj/` kvůli GitHub Pages) |

Hlavička a patička jsou v každé stránce zkopírované. Při změně menu je potřeba upravit všechny stránky.

`assets/site.js` (bez závislostí) ovládá mobilní menu, zvýraznění postranního obsahu a záložky Žebříčku. Bez JavaScriptu web funguje dál: menu je rovnou vidět a záložky jsou pod sebou.

Mapa a výškové profily (`index.html`, `trasa.html`) generuje z `data/trasa.gpx` a `data/challenge.json` skript `scripts/route_svg.py` (jen standardní Python). Po změně trasy spusť v kořeni repa:

```
python3 scripts/route_svg.py
```

Skript přepíše obsah mezi značkami `<!-- ROUTE:… -->` a `<!-- /ROUTE:… -->`. Složka `scripts/` se na web nenasazuje.

## GPX parser

Kontrola nahraných pokusů je C# knihovna (.NET 8), oddělená od webu:

| Složka | Obsah |
|---|---|
| `src/NebePekloRaj.GpxValidation` | načtení GPX, kontroly pravidel, výpočet časů |
| `tests/NebePekloRaj.GpxValidation.Tests` | unit testy, i na předběžné trase |
| `data/trasa.gpx` | oficiální trasa (zatím předběžná) |
| `data/challenge.json` | souřadnice startu, Pekla a cíle, zóny, všechny limity, datum spuštění a verze pravidel |

Posun cíle nebo nová trasa = upravit `data/challenge.json` nebo nahradit `data/trasa.gpx`, kód se nemění. Zadání kontrol je v dokumentu [GPX parser – zadání](https://claude.ai/artifact/HLPhBwi1GfbCPqk4sHFbwi).

Použití:

```csharp
var (config, route) = ChallengeConfig.LoadWithRoute("data/challenge.json");
var validator = new AttemptValidator(config, route);
var result = validator.Validate(
    [File.OpenRead("hodinky.gpx"), File.OpenRead("telefon.gpx")],
    RouteVariant.Full,
    new ValidationOptions(KnownAttempts: existing, IsRecordCandidate: wouldBeFirst));
// result.Verdict: Accepted / ManualReview / Rejected
// result.Elapsed, result.Stages, result.Findings, result.Fingerprint
// result.AttemptDateUtc, result.RulesVersion
// result.Stage1Fallback: Etapa 1 z nedokončeného pokusu o celou trasu
```

Testy: `dotnet test` v kořeni repa.

## Jak vložit Tally formulář

1. Založ si účet na [tally.so](https://tally.so) (zdarma).
2. **Create form** → přidej pole **Email** (nastav jako povinné). Volitelně jméno.
3. Na konec přidej pole **Checkbox** se souhlasem, např. „Souhlasím se zasíláním informací o spuštění výzvy.“ a nastav ho jako povinné.
4. **Publish** → **Share** → **Embed** → zvol **Standard** a zapni *Transparent background* a *Dynamic height*.
5. Zkopíruj kód (`<iframe …>` a `<script …>`).
6. V `index.html` najdi komentář `TALLY` a obsah bloku `<div class="form-embed">…</div>` (iframe) a skript pod ním nahraď zkopírovaným kódem.

Odpovědi pak najdeš v Tally v záložce **Submissions** a jdou exportovat do CSV.

## Jak to zveřejnit přes GitHub Pages

Web se nasazuje přes GitHub Actions (`.github/workflows/pages.yml`): Repo → **Settings** → **Pages** → *Source: GitHub Actions*. Běží na vlastní doméně **https://nebepekloraj.eu** (soubor `CNAME`).

Nastavení domény:
1. U registrátora v DNS pro `nebepekloraj.eu` přidej 4× záznam **A**: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` (volitelně i **AAAA** `2606:50c0:8000::153`, `…8001::153`, `…8002::153`, `…8003::153`) a záznam **CNAME** `www` → `nebe-peklo-raj.github.io`.
2. Settings → **Pages** → *Custom domain*: `nebepekloraj.eu` → **Save**, po ověření DNS zaškrtni **Enforce HTTPS**.
3. V Mapy.com omez API klíč na HTTP referrer `nebepekloraj.eu` a `www.nebepekloraj.eu`.

## Design

Design V2 („turistický atlas“): bílé a teple šedé plochy, tenké linky, hranaté tvary, bez stínů a gradientů. Jen světlý režim. Rozhodnutí a rozdíly oproti PDF návrhu jsou v [docs/redesign-v2.md](docs/redesign-v2.md).

- Barvy, písma, velikosti a rozestupy jsou proměnné v `:root` na začátku `assets/styles.css`. Komponenty používají jen je.
- Modrá `#194FA2` / `#0F3470` je barva značky. Červená `#B92A2A` (Peklo) a zelená `#2F7A12` (Ráj) se používají jen na značky zastávek a body na mapě.
- Písmo: Barlow Condensed 700 na nadpisy a velká čísla, Barlow 500–700 na text, menu a popisky. Fonty jsou lokálně v `assets/fonts/`.
- Logo: Prstenec v hlavičce, inverzní Pečeť v patičce (pozadí patičky má stejnou modrou jako pozadí souboru). Soubory v `assets/logo/` se neupravují.
- Hlavní komponenty: `page-header`, `stats`, `stops`, `waypoints`, `tiles`, `rows`, `numbered`, `cta-band`, `toc`, `accordion`, `table`, `notice`, `tabs`.


## Aktuální trasa (5. 11. 2026)

Aktuální GPX má 3 895 bodů a délku přibližně 154,6 km. Kontrolní bod Peklo leží přibližně na 51,9 km; etapy tedy mají cca 52 km a 103 km. Součet kladných změn nadmořské výšky v GPX je přibližně +3 866 m (surový součet, zašuměný). Web uvádí cca +3 200 m (součet etap změřených v Mapy.com; celek v Mapy.com ukázal 2 961 m); etapy +1 370 m a +1 820 m změřil Tobias v Mapy.com (10. 11. 2026). Cílový bod v `data/challenge.json` je nyní nastaven na poslední bod GPX (50.466023 N, 15.320590 E), cílový bod je pojmenovaný Přivíšina.
