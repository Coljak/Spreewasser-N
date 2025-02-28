export function changeBasemap(basemap, baseMaps, map) {
    if (!basemap?.getAttribute) return;

    const selectedBasemap = basemap.getAttribute("data-basemap");
    map.eachLayer((layer) => {
        if (layer instanceof L.TileLayer && layer.options.name !== selectedBasemap) {
            map.removeLayer(layer);
        }
    });
    map.addLayer(baseMaps[selectedBasemap]);
}


export function createBaseLayerSwitchGroup(baseMaps, map) {
    let initialBasemapChecked = false; 
    const baseLayerControlList = document.getElementById("baseLayerList");
    let html = "";

    // Generate HTML for base layer switches
    Object.keys(baseMaps).forEach((basemapName) => {
        html += `
            <li class="list-group-item">
                <div class="col form-check form-switch">
                    <input 
                        type="radio" 
                        class="form-check-input user-field-switch basemap-switch" 
                        data-basemap="${basemapName}">
                    <label>${basemapName}</label>
                </div>
            </li>
        `;
    });

    // Insert the generated HTML
    baseLayerControlList.innerHTML = html;
    baseLayerCollapse.appendChild(baseLayerControlList);

    // Set initial basemap
    const initialBasemapSwitch = baseLayerControlList.querySelector(".basemap-switch");
    if (initialBasemapSwitch) {
        initialBasemapSwitch.checked = true;
        changeBasemap(initialBasemapSwitch, baseMaps, map);
    }
};

// export function initializeSidebarEventHandler(leafletSidebarContent, map, overlayLayers, userFields) {
//     leafletSidebarContent.addEventListener("change", (event) => {
//         const switchInput = event.target;

//         if (switchInput.classList.contains("basemap-switch")) {
//             changeBasemap(switchInput);
//         } else if (switchInput.classList.contains("layer-switch")) {
//             const layerId = switchInput.getAttribute("data-layer");
//             if (switchInput.checked) {
//                 map.addLayer(overlayLayers[layerId]);
//             } else {
//                 map.removeLayer(overlayLayers[layerId]);
//             }
//         } else if (switchInput.classList.contains("layer-opacity")) {
//             const overlayId = switchInput.getAttribute("data-layer");
//             const opacityValue = switchInput.value;
//             overlayLayers[overlayId].setOpacity(opacityValue);
//         } else if (switchInput.classList.contains("overlay-switch")) {
//             const overlayId = switchInput.getAttribute("data-layer");
//             const overlay = overlayLayers[overlayId];
//             const opacitySlider = document.getElementById(`${overlayId}Opacity`);

//             if (switchInput.checked) {
//                 overlay.addTo(map);
//                 if (opacitySlider) {
//                     opacitySlider.disabled = false;
//                 }
//                 overlay.bringToBack();
//             } else {
//                 overlay.remove();
//                 if (opacitySlider) {
//                     opacitySlider.disabled = true;
//                 }
//             }
//         } else if (switchInput.classList.contains("user-field-switch")) {
//             const leafletId = switchInput.getAttribute("leaflet-id");
//             const userField = userFields[leafletId];
//             if (switchInput.checked) {
//                 map.addLayer(userField.layer);
//             } else {
//                 map.removeLayer(map._layers[leafletId]);
//             }
//         }
//     });
// }


export function initializeSidebarEventHandler({ sidebar, map, overlayLayers, getUserFields }) {
    sidebar.addEventListener("change", (event) => {
        const switchInput = event.target;

        if (switchInput.classList.contains("basemap-switch")) {
            changeBasemap(switchInput, map);
        } else if (switchInput.classList.contains("layer-switch")) {
            const layerId = switchInput.getAttribute("data-layer");
            switchInput.checked ? map.addLayer(overlayLayers[layerId]) : map.removeLayer(overlayLayers[layerId]);
        } else if (switchInput.classList.contains("layer-opacity")) {
            const overlayId = switchInput.getAttribute("data-layer");
            overlayLayers[overlayId].setOpacity(switchInput.value);
        } else if (switchInput.classList.contains("overlay-switch")) {
            handleOverlaySwitch(switchInput, overlayLayers, map);
        } else if (switchInput.classList.contains("user-field-switch")) {
            toggleUserField(switchInput, getUserFields(), map);
        }
    });
}

function toggleUserField(switchInput, userFields, map) {
    const leafletId = switchInput.getAttribute("leaflet-id");
    const userField = userFields[leafletId];

    if (!userField) return; // Handle cases where userFields has changed and the key no longer exists

    switchInput.checked ? map.addLayer(userField.layer) : map.removeLayer(map._layers[leafletId]);
}
