// Baselayers
export function changeBasemap(basemapSwitch, baseMaps, map) {
    console.log("changeBasemap", basemapSwitch);
    if (!basemapSwitch?.getAttribute) return;

    const selectedBasemap = basemapSwitch.getAttribute("data-basemap");
    map.eachLayer((layer) => {
        if (layer instanceof L.TileLayer && layer.options.name !== selectedBasemap) {
            map.removeLayer(layer);
        }
    });
    map.addLayer(baseMaps[selectedBasemap]);
    document.querySelectorAll(".basemap-switch").forEach((switchInput) => {
        if (switchInput !== basemapSwitch) {
            switchInput.checked = false;
        }
    });
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

// Overlays
function handleOverlaySwitch(switchInput, overlayLayers, map) {
    const overlayId = switchInput.getAttribute("data-layer");
    const overlay = overlayLayers[overlayId];
    const opacitySlider = document.getElementById(`${overlayId}Opacity`);

    if (switchInput.checked) {
    overlay.addTo(map);
    if (opacitySlider) {
        opacitySlider.disabled = false;
    };
    overlay.bringToBack(); 
    } else {
    overlay.remove();
    if (opacitySlider) {
        opacitySlider.disabled = true;
    };
    };
}

export function initializeSidebarEventHandler({ sidebar, map, baseMaps, overlayLayers, getUserFields, featureGroup }) {
    sidebar.addEventListener("change", (event) => {
        const switchInput = event.target;

        if (switchInput.classList.contains("basemap-switch")) {
            changeBasemap(switchInput, baseMaps, map);
        } else if (switchInput.classList.contains("layer-switch")) {
            const layerId = switchInput.getAttribute("data-layer");
            switchInput.checked ? map.addLayer(overlayLayers[layerId]) : map.removeLayer(overlayLayers[layerId]);
        } else if (switchInput.classList.contains("layer-opacity")) {
            const overlayId = switchInput.getAttribute("data-layer");
            overlayLayers[overlayId].setOpacity(switchInput.value);
        } else if (switchInput.classList.contains("overlay-switch")) {
            handleOverlaySwitch(switchInput, overlayLayers, map);
        } else if (switchInput.classList.contains("user-field-switch")) {
            toggleUserField(switchInput, featureGroup);
        }
    });

    sidebar.addEventListener("dblclick", (event) => {
        
        if (event.target.classList.contains("user-field-btn")) {
          const listElement = event.target.closest(".accordion-item");
          
          map.fitBounds(listElement.layer.getBounds());
        }
    });

    // sidebar.addEventListener("click", (event) => {
    //     console.log('CLICK')
    //     if (event.target.classList.contains("user-field-header") || event.target.classList.contains("user-field-btn")) {
    //             const leafletId = event.target.getAttribute("leaflet-id");
    //             console.log("user-field-header clicked", leafletId);
            
    //             selectUserField(getUserFieldIdByLeafletId(leafletId));
                
    //           }
    //   });

    
}


function toggleUserField(switchInput,  map) {
    const leafletId = switchInput.getAttribute("leaflet-id");
    const accordion = switchInput.closest(".accordion-item");
    switchInput.checked ? map.addLayer(accordion.layer) : map.removeLayer(accordion.layer);

};



export const addLayerToSidebar = (userField, layer) => {
    var menuType = '';
  
    // new Accordion UserField style
    const accordion = document.createElement("div");
    accordion.setAttribute("class", "accordion-item");
    accordion.setAttribute("id", `accordion-${userField.leafletId}`);
    accordion.setAttribute("leaflet-id", userField.leafletId);
    accordion.setAttribute("user-field-id", userField.id);
   
  
    let projectListHTML = "";
    // Check if there are related projects
    if (userField.userProjects && userField.userProjects.length > 0) {
      projectListHTML = userField.userProjects
        .map(
          (project) => `
            <li class="list-group-item">
              <button type="button" class="btn btn-primary btn-sm open-project" data-project-id="${project.id}" data-user-field-id="${userField.id}">
                ${project.name}
              </button>
            </li>
          `
        )
        .join("");
    } 
      // Create project button
      projectListHTML += `
        <li class="list-group-item">
          <button type="button" class="btn btn-success btn-sm create-project" data-user-field-id="${userField.id}">
            Create Project
          </button>
        </li>
      `;
  
    // Generate the full HTML for the accordion
    accordion.innerHTML = `
      <div 
        class="accordion-header nested user-field-header d-flex align-items-center justify-content-between" 
        id="accordionHeader-${userField.leafletId}" 
        leaflet-id="${userField.leafletId}"
      >
        <span class="form-check form-switch h6">  
          <input type="checkbox" class="form-check-input user-field-switch" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" id="fieldSwitch-${userField.leafletId}" checked>
        </span>
        <button class="accordion-button nested btn collapsed user-field-btn" type="button" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" id="accordionButton-${userField.leafletId}" data-bs-toggle="collapse" data-bs-target="#accordionField-${userField.leafletId}" aria-expanded="false" aria-controls="accordionField-${userField.leafletId}"> 
          ${userField.name}
        </button>
        <span class="column col-4 field-btns-col">
          <form id="deleteAndCalcForm-${userField.leafletId}">
            <button type="button" class="btn btn-outline-secondary btn-sm field-name user-field-action field-edit" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}">
              <span><i class="bi bi-pencil-square user-field-action field-edit" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm user-field-action field-menu" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}">
              <span><i class="bi bi-list user-field-action field-menu" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm user-field-action delete" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}">
              <span><i class="bi bi-trash user-field-action delete" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
          </form>
        </span>  
      </div>
      <div id="accordionField-${userField.leafletId}" class="accordion-collapse collapse">
        <div class="accordion-body">
          <ul class="list-group" id="projectList-${userField.leafletId}">
            ${projectListHTML}
          </ul>
        </div>
      </div>
    `;
  
    // adding the UserField to the HTML-list element
    accordion.layer = layer;
  
    userFieldsAccordion.appendChild(accordion);
  };

  export function openUserFieldNameModal(layer) {
    // Set the modal content (e.g., name input)
    const modal = document.querySelector('#userFieldNameModal');
  
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
  
    // Add event listeners for the save and dismiss actions
    modal.querySelector('#btnUserFieldSave').onclick = () => handleSaveUserField(layer, bootstrapModal);
    modal.querySelector('#btnUserFieldDismiss').onclick = () => dismissPolygon(layer, bootstrapModal);
    modal.querySelector('#btnUserFieldDismissTop').onclick = () => dismissPolygon(layer, bootstrapModal);
  }