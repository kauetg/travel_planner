// Busca + mini-mapa de localização pro form de trip (add e edit).
// Usa delegação de evento pra funcionar tanto no form incluído direto (home)
// quanto no injetado via fetch (editTripModal em trip_detail.html).
(function () {
  let map = null;
  let marker = null;

  function setPin(lat, lon) {
    document.getElementById('trip-lat').value = lat;
    document.getElementById('trip-lng').value = lon;
    if (marker) marker.setLatLng([lat, lon]);
    else marker = L.marker([lat, lon]).addTo(map);
  }

  function initTripLocationMap() {
    const container = document.getElementById('trip-loc-map');
    if (!container) return;

    if (map) map.remove();
    marker = null;

    map = L.map('trip-loc-map').setView([20, 10], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap'
    }).addTo(map);
    map.on('click', e => setPin(e.latlng.lat.toFixed(6), e.latlng.lng.toFixed(6)));

    const lat = parseFloat(document.getElementById('trip-lat').value);
    const lon = parseFloat(document.getElementById('trip-lng').value);
    if (lat && lon) {
      marker = L.marker([lat, lon]).addTo(map);
      map.setView([lat, lon], 8);
    }

    setTimeout(() => map.invalidateSize(), 200);
  }

  async function searchTripLocation() {
    const input = document.getElementById('trip-loc-search');
    const query = input.value.trim();
    if (!query) return;

    const resp = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&addressdetails=1&limit=1`);
    const data = await resp.json();
    if (!data.length) {
      alert('Location not found. Try being more specific (e.g. add the country name).');
      return;
    }

    const result = data[0];
    const lat = parseFloat(result.lat);
    const lon = parseFloat(result.lon);

    document.getElementById('trip-country-name').value = result.address?.country || '';
    document.getElementById('trip-country-code').value = (result.address?.country_code || '').toUpperCase();

    if (!map) initTripLocationMap();
    map.setView([lat, lon], 8);
    setPin(lat.toFixed(6), lon.toFixed(6));
  }

  document.addEventListener('click', function (e) {
    if (e.target.closest('#trip-loc-search-btn')) {
      e.preventDefault();
      searchTripLocation();
    }
  });

  // Modal "Add New Trip" na home: form já está no DOM, o bootstrap dispara esse evento.
  document.addEventListener('shown.bs.modal', function (e) {
    if (e.target.id === 'addTripModal') initTripLocationMap();
  });

  // Modal "Edit Trip" na página da viagem: chamado manualmente logo após o fetch
  // injetar o HTML (script tags injetados via innerHTML não executam sozinhos).
  window.initTripLocationMap = initTripLocationMap;
})();
