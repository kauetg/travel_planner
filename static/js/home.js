 function scrollTrips(direction) {
      const container = document.getElementById("trip-scroll-container");
      const scrollAmount = 300;
      container.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }

const currentRealYear = new Date().getFullYear();
let currentYear = currentRealYear;

const yearDisplayEl = document.getElementById("currentYear");
const calendarTitleEl = document.getElementById("calendar_title");

function updateYear(delta) {
  currentYear += delta;
  console.log()
  if (currentYear > currentRealYear) {
    yearDisplayEl.textContent = "All Trips";
    calendarTitleEl.textContent = "All Trips";
    renderMap("All Trips")
    showAllTrips()

  } else {
    yearDisplayEl.textContent = currentYear;
    calendarTitleEl.innerHTML = `Annual Calendar <strong>${currentYear}</strong>`;
    renderCompactCalendar(currentYear);
    renderMap(currentYear);
  }
}

// Inicializa ao carregar
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("prevYear").addEventListener("click", () => updateYear(-1));
  document.getElementById("nextYear").addEventListener("click", () => updateYear(1));
  updateYear(0);
});
