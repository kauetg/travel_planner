// utils para modais do app Trip Planner
import { enableMapboxAutocomplete } from "./map_box.js";
const mapboxToken = window.mapboxToken;

export function openAddActivityModal({ category, label, icon, tripId }) {
  const modal = new bootstrap.Modal(document.getElementById("activityModal"));
  const modalTitle = document.getElementById("activityModalLabel");
  const modalBody = document.getElementById("modal-body-content");

  modalTitle.innerHTML = `<i class="${icon} me-2"></i> ${label}`;
  modalBody.innerHTML = '<div class="text-center py-3"><div class="spinner-border" role="status"></div></div>';

  const url = `/trip/${tripId}/add_${category}`;
  fetch(url)
    .then((res) => res.text())
    .then((html) => {
      modalBody.innerHTML = html;

      // ✅ Ativa Mapbox autocomplete
      enableMapboxAutocomplete({
        inputId: "departure",
        latId: "departure_lat",
        lonId: "departure_lon",
        imageId: "departure_map_image",
        accessToken: mapboxToken,
      });

      enableMapboxAutocomplete({
        inputId: "arrival",
        latId: "arrival_lat",
        lonId: "arrival_lon",
        imageId: "arrival_map_image",
        accessToken: mapboxToken,
      });
    })
    .catch(() => {
      modalBody.innerHTML = "<p class='text-danger'>Failed to load form. Try again.</p>";
    });

  modal.show();
}


export function openViewActivityModal({ activityId, icon, label, tripId, mode = "view" }) {
  const modalEl = document.getElementById("viewActivityModal");
  const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
  const modalTitle = document.getElementById("viewActivityModalLabel");
  const content = document.getElementById("view-activity-content");

  modalTitle.innerHTML = `<i class="${icon} me-2"></i> ${label}`;
  content.innerHTML = '<div class="text-center py-3"><div class="spinner-border" role="status"></div></div>';

  const url = mode === "edit"
    ? `/trip/${tripId}/activity/${activityId}?mode=edit`
    : `/trip/${tripId}/activity/${activityId}`;

  fetch(url)
    .then(res => res.text())
    .then(html => {
      content.innerHTML = html;

      const isAlreadyOpen = modalEl.classList.contains("show");
      if (!isAlreadyOpen) {
        modal.show();
      }

      // Só ativa o Mapbox se for no modo edição
      if (mode === "edit") {
        enableMapboxAutocomplete({
          inputId: "departure_edit",
          latId: "departure_lat_edit",
          lonId: "departure_lon_edit",
          imageId: "departure_map_image_edit",
          accessToken: mapboxToken,
        });

        enableMapboxAutocomplete({
          inputId: "arrival_edit",
          latId: "arrival_lat_edit",
          lonId: "arrival_lon_edit",
          imageId: "arrival_map_image_edit",
          accessToken: mapboxToken,
        });
      }

      // Reanexa botão "Edit" no modo visualização
      if (mode === "view") {
        const editBtn = document.getElementById("edit-btn");
        if (editBtn) {
          editBtn.addEventListener("click", () => {
            openViewActivityModal({ activityId, icon, label, tripId, mode: "edit" });
          });
        }
      }
    })
    .catch(() => {
      content.innerHTML = '<div class="text-danger">Error loading activity.</div>';
    });
}
window.openViewActivityModal = openViewActivityModal;

export function openAddInfoModal(tripId) {
  fetch(`/trip/${tripId}/add_info_modal`)
    .then(res => res.text())
    .then(html => {
      document.getElementById('add-info-modal-container').innerHTML = html;

      const modalEl = document.getElementById('addInfoModal');
      const modal = new bootstrap.Modal(modalEl);
      modal.show();

      // agora o form existe
      document.getElementById('customInfoForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const title = document.getElementById('info-title').value.trim();
        const url = document.getElementById('info-url').value.trim();
        const notes = document.getElementById('info-notes').value.trim();

        if (!title) return alert("Please add a title.");

        const data = {
          title,
          url,
          notes,
          trip_id: tripId
        };

        fetch(`/trip/${tripId}/add_link`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        }).then(res => {
          if (res.ok) {
            location.reload();
          } else {
            alert("Failed to save info.");
          }
        });
      });
    });
}

// Torna a função global
window.openAddInfoModal = openAddInfoModal;


export function openEditTripModal(tripId) {
  const modalEl = document.getElementById("editTripModal");
  const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
  const content = document.getElementById("edit-trip-content");

  content.innerHTML = '<div class="text-center py-3"><div class="spinner-border" role="status"></div></div>';

  fetch(`/trip/${tripId}/edit`)
    .then(res => res.text())
    .then(html => {
      content.innerHTML = html;
      modal.show();
    })
    .catch(() => {
      content.innerHTML = '<div class="text-danger">Failed to load trip form.</div>';
    });
}

window.openEditTripModal = openEditTripModal;