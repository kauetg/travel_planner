    export function enableMapboxAutocomplete({ inputId, latId, lonId, imageId, accessToken }) {
      const input = document.getElementById(inputId);
      if (!input) return;

      const suggestionsId = `${inputId}-suggestions`;
      let suggestionsBox = document.getElementById(suggestionsId);

      if (!suggestionsBox) {
        suggestionsBox = document.createElement("div");
        suggestionsBox.id = suggestionsId;
        suggestionsBox.className = "list-group position-absolute w-100";
        suggestionsBox.style.zIndex = 1000;
        input.parentNode.appendChild(suggestionsBox);
      }

      input.addEventListener("input", function () {
        const query = input.value.trim();
        if (query.length < 3) {
          suggestionsBox.innerHTML = '';
          return;
        }

        fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${accessToken}`)
          .then(res => res.json())
          .then(data => {
            suggestionsBox.innerHTML = '';
            data.features.forEach(feature => {
              const item = document.createElement("a");
              item.href = "#";
              item.className = "list-group-item list-group-item-action";
              item.textContent = feature.place_name;
              item.addEventListener("click", (e) => {
                e.preventDefault();
                input.value = feature.place_name;
                const latEl = document.getElementById(latId);
const lonEl = document.getElementById(lonId);
const imgEl = document.getElementById(imageId);

if (latEl) latEl.value = feature.geometry.coordinates[1];
if (lonEl) lonEl.value = feature.geometry.coordinates[0];
if (imgEl) {
  imgEl.value = `https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/pin-l+ff0000(${feature.geometry.coordinates[0]},${feature.geometry.coordinates[1]})/${feature.geometry.coordinates[0]},${feature.geometry.coordinates[1]},14/600x300?access_token=${accessToken}`;
}
                suggestionsBox.innerHTML = '';
              });
              suggestionsBox.appendChild(item);
            });
          });
      });
    }
