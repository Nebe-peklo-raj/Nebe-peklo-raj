(function () {
  'use strict';

  var mapElement = document.getElementById('interactive-map');
  if (!mapElement) return;

  var statusElement = document.getElementById('map-status');
  var fallback = document.querySelector('.route-fallback');
  var apiKey = (window.MAPY_API_KEY || '').trim();

  function setStatus(message) {
    if (statusElement) statusElement.textContent = message || '';
  }

  function showFallback(message) {
    setStatus(message);
    if (fallback) fallback.open = true;
  }

  if (!apiKey) {
    showFallback('Mapa zatím není aktivní: doplň API klíč do assets/mapy-config.js. Níže zůstává statické schéma a výškový profil.');
    return;
  }

  if (!window.L) {
    showFallback('Mapovou knihovnu Leaflet se nepodařilo načíst. Zobrazuji statické schéma a výškový profil.');
    return;
  }

  var map = L.map(mapElement, {
    scrollWheelZoom: false,
    zoomControl: false,
    attributionControl: false
  });
  L.control.zoom({ position: 'topright' }).addTo(map);

  var tileLayer = L.tileLayer(
    'https://api.mapy.com/v1/maptiles/outdoor/256/{z}/{x}/{y}?apikey=' + encodeURIComponent(apiKey),
    { minZoom: 5, maxZoom: 19, crossOrigin: true }
  ).addTo(map);

  var tileErrorShown = false;
  tileLayer.on('tileerror', function () {
    if (tileErrorShown) return;
    tileErrorShown = true;
    showFallback('Mapové podklady se nepodařilo načíst. Zkontroluj omezení API klíče v Mapy.com (HTTP referrer polik9000.github.io, služba Map Tiles).');
  });

  fetch('data/trasa.gpx', { cache: 'no-cache' })
    .then(function (response) {
      if (!response.ok) throw new Error('GPX HTTP ' + response.status);
      return response.text();
    })
    .then(function (xmlText) {
      var xml = new DOMParser().parseFromString(xmlText, 'application/xml');
      if (xml.querySelector('parsererror')) throw new Error('GPX XML parse error');
      var trackPoints = Array.prototype.slice.call(xml.getElementsByTagNameNS('*', 'trkpt'));
      var coordinates = trackPoints.map(function (point) {
        return [Number(point.getAttribute('lat')), Number(point.getAttribute('lon'))];
      }).filter(function (point) {
        return Number.isFinite(point[0]) && Number.isFinite(point[1]);
      });
      if (coordinates.length < 2) throw new Error('GPX neobsahuje trasu');

      var route = L.polyline(coordinates, {
        color: '#fff',
        weight: 8,
        opacity: .92,
        lineCap: 'round',
        lineJoin: 'round'
      }).addTo(map);
      L.polyline(coordinates, {
        color: '#245b83',
        weight: 4,
        opacity: .95,
        lineCap: 'round',
        lineJoin: 'round'
      }).addTo(map);

      var markers = [
        { name: 'Nebe', short: 'N', className: 'nebe', lat: 50.18885, lon: 16.41996, subtitle: 'Kostel v Nebeské Rybné · start' },
        { name: 'Peklo', short: 'P', className: 'peklo', lat: 50.37925, lon: 16.18723, subtitle: 'Bartoňova útulna · kontrolní bod' },
        { name: 'Převýšina', short: 'R', className: 'raj', lat: 50.466023, lon: 15.32059, subtitle: 'Cíl · Ráj' }
      ];

      markers.forEach(function (point) {
        var icon = L.divIcon({
          className: '',
          html: '<span class="route-marker route-marker--' + point.className + '"><span>' + point.short + '</span></span>',
          iconSize: [32, 38],
          iconAnchor: [16, 36]
        });
        L.marker([point.lat, point.lon], { icon: icon, title: point.name, alt: point.name })
          .bindPopup('<strong>' + point.name + '</strong><br>' + point.subtitle)
          .addTo(map);
      });

      map.fitBounds(route.getBounds(), { padding: [28, 28] });
      setStatus('');
      if (fallback) fallback.open = false;
      window.setTimeout(function () { map.invalidateSize(); }, 150);
    })
    .catch(function (error) {
      showFallback('Trasu se nepodařilo načíst (' + error.message + '). Zobrazuji statické schéma a výškový profil.');
    });

  window.addEventListener('resize', function () { map.invalidateSize(); });
})();
