const calendarTitle = document.getElementById("calendar_title");
//let yearDisplayEl = document.getElementById("currentYear"); // <strong id="currentYear">2025</strong>
const initialYear = parseInt(yearDisplayEl?.textContent.trim()) || new Date().getFullYear();

// Garante que 'trips' esteja disponível globalmente (deve estar no HTML antes deste script)
if (typeof trips === 'undefined') {
  console.warn("⚠️ Variável 'trips' não está definida!");
}

function renderCompactCalendar(year) {
  calendarTitle.innerHTML = "Calendar";
  const container = document.getElementById("calendar");
  const monthNames = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
  ];

  container.innerHTML = "";
  container.style.display = "grid";
  container.style.gap = "0.5rem";
//  container.style.gridTemplateColumns = "repeat(auto-fill, minmax(160px, 1fr))";

  for (let month = 0; month < 12; month++) {
    const monthBox = document.createElement("div");
    monthBox.className = "border rounded p-2 shadow-sm text-center bg-white";
    monthBox.style.fontSize = "0.75rem";

    const title = document.createElement("div");
    title.className = "fw-bold mb-2 text-danger";
    title.innerText = monthNames[month];
    monthBox.appendChild(title);

    const daysContainer = document.createElement("div");
    daysContainer.style.display = "grid";
    daysContainer.style.gridTemplateColumns = "repeat(7, 1fr)";
    daysContainer.style.gap = "2px";

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    for (let i = 0; i < firstDay; i++) {
      daysContainer.appendChild(document.createElement("div")); // espaços em branco antes do 1º dia
    }

    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;

      const day = document.createElement("div");
      day.innerText = d;
      day.className = "bg-light small rounded day";
      day.style.padding = "2px 0";
      day.setAttribute("data-date", dateStr);
      day.style.userSelect = "none";

      // Marca os dias das trips
      if (Array.isArray(trips)) {
        trips.forEach(trip => {
          if (trip.dates && trip.dates.includes(dateStr)) {
            day.classList.add("trip-day");
            day.title = trip.name;
          }
        });
      }

      daysContainer.appendChild(day);
    }

    monthBox.appendChild(daysContainer);
    container.appendChild(monthBox);
  }

  // Ajusta altura do mapa ao final
  syncMapHeight();
}

function syncMapHeight() {
  const calendar = document.getElementById("calendar");
  const map = document.getElementById("map");
  if (calendar && map) {
    map.style.height = `${calendar.offsetHeight}px`;
  }
}

// Filtro alternativo (caso esteja usando select dropdown)
const yearFilterEl = document.getElementById("yearFilter");
if (yearFilterEl) {
  yearFilterEl.addEventListener("change", function () {
    const selectedYear = this.value;

    if (selectedYear === "All Trips") {
      calendarTitle.innerHTML = "All Trips";
      document.getElementById("calendar").innerHTML = "<p class='text-muted'>Showing all trips.</p>";
    } else {
      renderCompactCalendar(parseInt(selectedYear));
    }
  });
}

// Chamada inicial
renderCompactCalendar(initialYear);

function showAllTrips() {
  const calendar = document.getElementById("calendar");
  const calendarTitle = document.getElementById("calendar_title");

  calendarTitle.innerHTML = "All Trips";
  calendar.innerHTML = "";

  // Estilização para rolagem vertical
  calendar.style.display = "block";
  calendar.style.maxHeight = "600px"; // ou o valor que quiser
  calendar.style.overflowY = "auto";
  calendar.style.paddingRight = "1rem";

  const tripsByYear = {};
  trips.forEach(trip => {
    const year = trip.year || "Unknown";
    if (!tripsByYear[year]) tripsByYear[year] = [];
    tripsByYear[year].push(trip);
  });

  const sortedYears = Object.keys(tripsByYear).sort((a, b) => b - a);

  sortedYears.forEach(year => {
    // Bloco do ano
    const yearSection = document.createElement("div");
    yearSection.className = "mb-4";

    const yearTitle = document.createElement("h4");
    yearTitle.className = "text-primary fw-bold mb-3 border-bottom pb-1";
    yearTitle.innerText = year;
    yearSection.appendChild(yearTitle);

    // Lista das trips
    tripsByYear[year].forEach(trip => {
      const tripRow = document.createElement("div");
      tripRow.className = "d-flex justify-content-between align-items-center mb-2 px-2 py-2 bg-white rounded shadow-sm";

      const date = new Date(trip.dates[0]);
      const month = date.toLocaleString('default', { month: 'short' });

      tripRow.innerHTML = `
        <div>
          <div class="fw-semibold">${trip.name}</div>
          <small class="text-muted">${month} – ${trip.country_name}</small>
        </div>
                       <div class="flag-frame">
                    <img src="https://flagsapi.com/${ trip.country_code }/flat/64.png"
                         alt="${ trip.country_name } Flag"
                         class="img-fluid">
                </div>
      `;

      yearSection.appendChild(tripRow);
    });

    calendar.appendChild(yearSection);
  });
}
