import { openAddActivityModal, openViewActivityModal, openAddInfoModal , openEditTripModal,} from './modals_utils.js';

document.addEventListener("DOMContentLoaded", () => {
  const tripData = JSON.parse(document.getElementById("trip-context").textContent);

  // Ativa botão "+ Add Activity"
  document.getElementById("activityModal").addEventListener("show.bs.modal", (event) => {
    const button = event.relatedTarget;
    openAddActivityModal({
      category: button.dataset.category,
      label: button.dataset.label,
      icon: button.dataset.icon,
      tripId: tripData._id,
    });
  });

  // Ativa clique nos cards
  document.querySelectorAll(".activity-item").forEach((el) => {
    el.addEventListener("click", () => {
      openViewActivityModal({
        activityId: el.dataset.activityId,
        icon: el.dataset.icon,
        label: el.dataset.label,
        tripId: tripData._id,
        mode: "view",
      });
    });
  });

  // Botão "➕ Add Custom Info"
  const addInfoBtn = document.querySelector('[data-bs-target="#addInfoModal"]');
  if (addInfoBtn) {
    addInfoBtn.addEventListener('click', () => {
      openAddInfoModal(tripData._id);
    });
  }

  // Formulário de custom info
  const customInfoForm = document.getElementById('customInfoForm');
  if (customInfoForm) {
    customInfoForm.addEventListener('submit', function (e) {
      e.preventDefault();

      const title = document.getElementById('info-title').value.trim();
      const url = document.getElementById('info-url').value.trim();
      const notes = document.getElementById('info-notes').value.trim();

      if (!title) return alert("Please add a title.");

      const data = {
        title,
        url,
        notes,
        trip_id: window.currentTripId,
      };

      fetch(`/trip/${data.trip_id}/add_link`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
        .then(res => {
          if (res.ok) {
            location.reload();
          } else {
            alert("Failed to save info.");
          }
        });
    });
  }
});

// Tornar acessível globalmente se necessário
window.openViewActivityModal = openViewActivityModal;
