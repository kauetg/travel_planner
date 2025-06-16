document.addEventListener("DOMContentLoaded", function () {
  const map = L.map('map').setView([0, 0], 2); // Visão inicial global

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  const allTrips = Array.isArray(trips) ? trips : [];
  let markers = [];

  function updateMap(year) {
    // Limpa marcadores antigos
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    const filteredTrips = year === "All Trips"
      ? allTrips
      : allTrips.filter(trip => trip.year == year);

    const bounds = [];

    filteredTrips.forEach(trip => {
      if (trip.lat && trip.lng) {
        const customIcon = L.icon({
          iconUrl: '/static/img/pin.png',
          iconSize: [32, 50],
          iconAnchor: [16, 32],
          popupAnchor: [0, -32],
        });
        const marker = L.marker([trip.lat, trip.lng], { icon: customIcon })
          .bindPopup(`<strong>${trip.name}</strong><br>${trip.country_name}`);
        marker.addTo(map);
        markers.push(marker);
        bounds.push([trip.lat, trip.lng]);
      }
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [30, 30] });
    }
  }

  // Inicialização com o ano atual
  const currentYearEl = document.getElementById("currentYear");
  console.log(currentYearEl.textContent)
  const initialYear = currentYearEl ? currentYearEl.textContent.trim() : "All Trips";
  updateMap(initialYear);

  // Expor função globalmente para ser chamada de outro script
  window.renderMap = updateMap;
});
