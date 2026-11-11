#!/usr/bin/env python3
"""Vygeneruje mapu a výškové profily trasy z data/trasa.gpx a vloží je do HTML.

Použití (z kořene repozitáře):  python3 scripts/route_svg.py

Grafika se vkládá mezi značky v HTML:
  <!-- ROUTE:hero-profile -->   … <!-- /ROUTE:hero-profile -->   (index.html)
  <!-- ROUTE:map -->            … <!-- /ROUTE:map -->            (trasa.html)
  <!-- ROUTE:profile -->        … <!-- /ROUTE:profile -->        (trasa.html)

Spusť znovu po každé změně data/trasa.gpx nebo data/challenge.json.
Jen standardní knihovna Pythonu, nic se neinstaluje. Složka scripts/ se na web nenasazuje.
"""
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GPX_NS = "{http://www.topografix.com/GPX/1/1}"


# ---------- data ----------
def haversine(a, b):
    r = 6371000.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = p2 - p1
    dl = math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def load():
    cfg = json.loads((ROOT / "data/challenge.json").read_text(encoding="utf-8"))
    tree = ET.parse(ROOT / "data" / cfg["routeGpx"])
    pts = []
    for p in tree.iter(GPX_NS + "trkpt"):
        ele = p.find(GPX_NS + "ele")
        pts.append((float(p.get("lat")), float(p.get("lon")), float(ele.text) if ele is not None else 0.0))
    dist = [0.0]
    for i in range(1, len(pts)):
        dist.append(dist[-1] + haversine(pts[i - 1], pts[i]))
    return cfg, pts, dist


def nearest_index(pts, lat, lon):
    return min(range(len(pts)), key=lambda i: haversine(pts[i], (lat, lon)))


# ---------- helpers ----------
def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pct(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") + "%"


def douglas_peucker(points, eps):
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        s, e = stack.pop()
        (x1, y1), (x2, y2) = points[s], points[e]
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy) or 1e-9
        best, idx = 0.0, None
        for i in range(s + 1, e):
            x0, y0 = points[i]
            d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / norm
            if d > best:
                best, idx = d, i
        if idx is not None and best > eps:
            keep[idx] = True
            stack += [(s, idx), (idx, e)]
    return [p for p, k in zip(points, keep) if k]


def elevation_series(pts, dist, step_m, window_m):
    """Výšky vzorkované po step_m, vyhlazené klouzavým průměrem přes window_m."""
    total = dist[-1]
    out = []
    j0 = 0
    x = 0.0
    while True:
        lo, hi = x - window_m / 2, x + window_m / 2
        while j0 < len(dist) and dist[j0] < lo:
            j0 += 1
        s = n = 0
        j = j0
        while j < len(dist) and dist[j] <= hi:
            s += pts[j][2]
            n += 1
            j += 1
        if n == 0:
            k = min(range(len(dist)), key=lambda i: abs(dist[i] - x))
            s, n = pts[k][2], 1
        out.append((x, s / n))
        if x >= total:
            break
        x = min(total, x + step_m)
    return out


# ---------- fragments ----------
def hero_profile(cfg, pts, dist, stops):
    total = dist[-1]
    series = elevation_series(pts, dist, 400, 2500)
    lo, hi = 200.0, 1200.0
    w, h = 1000.0, 300.0

    def xy(d, e):
        return d / total * w, h - (e - lo) / (hi - lo) * h

    line = " ".join(f"{f(x)},{f(y)}" for x, y in (xy(d, e) for d, e in series))
    area = f"M0,{f(h)} L" + line.replace(" ", " L") + f" L{f(w)},{f(h)} Z"
    grid = "".join(
        f'<line x1="0" x2="{f(w)}" y1="{f(y)}" y2="{f(y)}"/>' for y in (h * 0.25, h * 0.5, h * 0.75)
    )

    def elev_at(d):
        return min(series, key=lambda s: abs(s[0] - d))[1]

    # Tečky sedí na křivce; názvy a km jsou v samostatném řádku pod grafem,
    # takže se nikdy nekryjí s tečkou ani s osou (Nebe zarovnané vlevo, Ráj vpravo).
    dots, pins = [], []
    for key, label, d in stops:
        x, y = xy(d, elev_at(d))
        dots.append(
            f'<span class="profile-hero__stop profile-hero__stop--{key}" style="left:{pct(x / w * 100)};top:{pct(y / h * 100)}"></span>'
        )
        pins.append(
            f'<span class="profile-hero__pin profile-hero__pin--{key}" style="left:{pct(x / w * 100)}"><b>{label}</b>{round(d / 1000)} km</span>'
        )
    return f"""<figure class="profile-hero">
  <figcaption class="profile-hero__head"><span>Výškový profil aktuální trasy</span><span>0 — {round(total / 1000)} km</span></figcaption>
  <div class="profile-hero__plot">
    <svg viewBox="0 0 {f(w)} {f(h)}" preserveAspectRatio="none" role="img" aria-labelledby="hero-profile-title">
      <title id="hero-profile-title">Výškový profil trasy: start v Nebi, Peklo po cca 52 km, cíl v Ráji po cca {round(total / 1000)} km. Nadmořská výška 250 až 1110 m.</title>
      <g class="profile-hero__grid">{grid}</g>
      <path class="profile-hero__area" d="{area}"/>
      <polyline class="profile-hero__line" points="{line}"/>
    </svg>
    {''.join(dots)}
  </div>
  <div class="profile-hero__axis" aria-hidden="true">{''.join(pins)}</div>
  <div class="profile-hero__regions" aria-hidden="true"><span>Orlické hory</span><span>Český ráj</span></div>
</figure>"""


def route_map(cfg, pts, stops_idx):
    lat0 = sum(p[0] for p in pts) / len(pts)
    k = math.cos(math.radians(lat0))
    raw = [(p[1] * k, -p[0]) for p in pts]
    minx, maxx = min(p[0] for p in raw), max(p[0] for p in raw)
    miny, maxy = min(p[1] for p in raw), max(p[1] for p in raw)
    w = 1000.0
    pad = 50.0
    scale = (w - 2 * pad) / (maxx - minx)
    h = (maxy - miny) * scale + 2 * pad
    h = max(h, 420.0)
    offy = (h - (maxy - miny) * scale) / 2

    def proj(lat, lon):
        return pad + (lon * k - minx) * scale, offy + (-lat - miny) * scale

    xy = [proj(p[0], p[1]) for p in pts]
    simp = douglas_peucker(xy, 0.8)
    d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in simp)

    # graticule: every 0.25° lon, 0.1° lat
    def frange(a, b, s):
        v = math.ceil(a / s) * s
        while v <= b:
            yield round(v, 4)
            v += s

    lon_min = (minx - pad / scale) / k
    lon_max = (maxx + pad / scale) / k
    lat_max = -(miny - offy / scale)
    lat_min = -(maxy + (h - offy - (maxy - miny) * scale) / scale)
    grid = []
    for lon in frange(lon_min, lon_max, 0.25):
        x, _ = proj(lat0, lon)
        grid.append(f'<line x1="{f(x)}" x2="{f(x)}" y1="0" y2="{f(h)}"/>')
    for lat in frange(lat_min, lat_max, 0.1):
        _, y = proj(lat, 0)
        grid.append(f'<line x1="0" x2="{f(w)}" y1="{f(y)}" y2="{f(y)}"/>')

    circles, labels = [], []
    for key, label, i in stops_idx:
        x, y = xy[i]
        circles.append(f'<circle class="route-map__dot route-map__dot--{key}" cx="{f(x)}" cy="{f(y)}" r="9"/>')
        labels.append(
            f'<span class="route-map__label route-map__label--{key}" style="left:{pct(x / w * 100)};top:{pct(y / h * 100)}">{label}</span>'
        )
    return f"""<figure class="route-map" style="aspect-ratio:{f(w)}/{f(h)}">
  <figcaption class="route-map__caption">Přehledové schéma trasy</figcaption>
  <svg viewBox="0 0 {f(w)} {f(h)}" role="img" aria-labelledby="route-map-title">
    <title id="route-map-title">Schéma trasy z Nebeské Rybné v Orlických horách (vpravo dole) přes Peklo u Nového Města nad Metují do Českého ráje (vlevo nahoře). Sever je nahoře.</title>
    <g class="route-map__grid">{''.join(grid)}</g>
    <path class="route-map__halo" d="{d}"/>
    <path class="route-map__line" d="{d}"/>
    {''.join(circles)}
  </svg>
  {''.join(labels)}
  <span class="route-map__region route-map__region--raj" aria-hidden="true">Český ráj</span>
  <span class="route-map__region route-map__region--nebe" aria-hidden="true">Orlické hory</span>
</figure>"""


def small_profile(cfg, pts, dist, stops):
    total = dist[-1]
    series = elevation_series(pts, dist, 250, 800)
    lo, hi = 200.0, 1200.0
    w, h = 1000.0, 260.0

    def xy(d, e):
        return d / total * w, h - (e - lo) / (hi - lo) * h

    line = " ".join(f"{f(x)},{f(y)}" for x, y in (xy(d, e) for d, e in series))
    area = f"M0,{f(h)} L" + line.replace(" ", " L") + f" L{f(w)},{f(h)} Z"
    grid = "".join(
        f'<line x1="0" x2="{f(w)}" y1="{f(xy(0, e)[1])}" y2="{f(xy(0, e)[1])}"/>' for e in (400, 600, 800, 1000)
    )
    ylabels = "".join(
        f'<span style="top:{pct(xy(0, e)[1] / h * 100)}">{e}</span>' for e in (400, 600, 800, 1000)
    )
    km_marks = [k for k in range(0, int(total / 1000) + 1, 40) if k * 1000 < total - 15000]
    xlabels = "".join(f'<span style="left:{pct(k * 1000 / total * 100)}">{k}</span>' for k in km_marks)
    markers = "".join(
        f'<span class="profile__stop profile__stop--{key}" style="left:{pct(d / total * 100)}"><span>{label}</span></span>'
        for key, label, d in stops
    )
    return f"""<figure class="profile">
  <div class="profile__plot">
    <svg viewBox="0 0 {f(w)} {f(h)}" preserveAspectRatio="none" role="img" aria-labelledby="profile-title">
      <title id="profile-title">Výškový profil trasy: nadmořská výška 250 až 1110 m, Peklo po cca 52 km, cíl po cca {round(total / 1000)} km.</title>
      <g class="profile__grid">{grid}</g>
      <path class="profile__area" d="{area}"/>
      <polyline class="profile__line" points="{line}"/>
    </svg>
    {markers}
    <div class="profile__y" aria-hidden="true">{ylabels}</div>
  </div>
  <div class="profile__x" aria-hidden="true">{xlabels}<span class="profile__unit">{round(total / 1000)} km</span></div>
  <figcaption class="note">Nadmořská výška (m) podle vzdálenosti (km), vyhlazeno. Schematický přehled podle aktuálního GPX.</figcaption>
</figure>"""


def inject(path, name, fragment):
    text = path.read_text(encoding="utf-8")
    pat = re.compile(rf"(<!-- ROUTE:{name} -->)(.*?)(<!-- /ROUTE:{name} -->)", re.S)
    if not pat.search(text):
        sys.exit(f"Značka ROUTE:{name} v {path.name} nenalezena")
    text = pat.sub(lambda m: m.group(1) + "\n" + fragment + "\n" + m.group(3), text)
    path.write_text(text, encoding="utf-8")
    print(f"{path.name}: {name} OK")


def main():
    cfg, pts, dist = load()
    ip = nearest_index(pts, cfg["peklo"]["lat"], cfg["peklo"]["lon"])
    stops_d = [("nebe", "Nebe", 0.0), ("peklo", "Peklo", dist[ip]), ("raj", "Ráj", dist[-1])]
    stops_i = [("nebe", "Nebe", 0), ("peklo", "Peklo", ip), ("raj", "Ráj", len(pts) - 1)]
    print(f"Délka {dist[-1] / 1000:.1f} km, Peklo na {dist[ip] / 1000:.1f} km, {len(pts)} bodů")
    inject(ROOT / "index.html", "hero-profile", hero_profile(cfg, pts, dist, stops_d))
    inject(ROOT / "trasa.html", "map", route_map(cfg, pts, stops_i))
    inject(ROOT / "trasa.html", "profile", small_profile(cfg, pts, dist, stops_d))


if __name__ == "__main__":
    main()
