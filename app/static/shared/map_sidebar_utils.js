import { MonicaProject,  loadProjectFromDB, loadProjectToGui, handleDateChange } from '/static/monica/monica_model.js';

export class UserField {
  constructor(name, id=null, userProjects=[]) {
    this.name = name;
    // this.layer = layer;
    this.id = id;
    this.userProjects = userProjects;
  }
};

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
};


export function getUserFields() {
  let userFields = localStorage.getItem("userFields");
  return userFields ? JSON.parse(userFields) : {};
};

export function getLeafletIdByUserFieldId(id) {
  let userFields = getUserFields();
  const entry = Object.values(userFields).find(field => field.id == id);
  return entry ? entry.leafletId : null;
};

export function getUserFieldIdByLeafletId(leafletId) {
  let userFields = getUserFields();
  const entry = Object.values(userFields).find(field => field.leafletId == leafletId);
  console.log("getUserFieldIdByLeafletId", leafletId, entry, userFields);
  return entry ? entry.id : null;
};
export function highlightLayer(leafletId, featureGroup) {
  console.log("HIGHLIGHT", leafletId);
  // remove highlight from all layers
  console.log('HighlightLayer, featureGroup' , featureGroup)
  featureGroup.eachLayer(function (layer) {
    const key = Object.keys(layer._layers)[0];
    const value = layer._layers[key];
    value._path.classList.remove("highlight");
  });
  // deselect layer/ header: remove highlight class from  header
  if ($(`#accordionHeader-${leafletId}`).hasClass("highlight")) {
    $(`#accordionHeader-${leafletId}`).removeClass("highlight");

    
    let key = Object.keys(featureGroup._layers[leafletId]._layers)[0]
    console.log("Key: ", key, "leafletId: ", leafletId)
     featureGroup._layers[leafletId]._layers[key]._path.classList.remove('highlight');
  } else { // select layer/ header: 

      const accordionUserFieldHeaders = document.querySelectorAll('#accordionUserFields .accordion-header');
      accordionUserFieldHeaders.forEach(header => {
        header.classList.remove('highlight')
      });

    $(`#accordionHeader-${leafletId}`).addClass("highlight")
    // add highlight class to leaflet layer
    let key = Object.keys(featureGroup._layers[leafletId]._layers)[0]
    featureGroup._layers[leafletId]._layers[key]._path.classList.add('highlight');
  };
};

export function selectUserField(userFieldId, project, featureGroup) {
  console.log("selectUserField featureGroup", featureGroup);
  // const project = MonicaProject.loadFromLocalStorage();
  if (project.userField && project.userField != userFieldId && project.id) {
    console.log('If action')
    let modal = document.getElementById('interactionModal');
    let modalInstance = new bootstrap.Modal(modal);
    document.getElementById('interactionModalTitle').innerHTML = "User Field Selection";
    document.getElementById('interactionModalText').innerHTML = "you are changing a Monica Project without UserField to a SWN Project with UserField. The location of the project will be changed to the UserField location.";
    $('#interactionModalOK').off('click').on('click', function () {
      project.userField = userFieldId;
      project.saveToLocalStorage();
      highlightLayer(getLeafletIdByUserFieldId(userFieldId), featureGroup);
    }
    );
    modalInstance.show(); 
  } else {
    console.log('Else action')
    project.userField = userFieldId;
    project.saveToLocalStorage();
    highlightLayer(getLeafletIdByUserFieldId(userFieldId), featureGroup);
  };
};

export function initializeSidebarEventHandler({ sidebar, map, baseMaps, overlayLayers, getUserFields, getFeatureGroup, getProject }) {
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
            toggleUserField(switchInput, getFeatureGroup());
        }
    });

    sidebar.addEventListener("dblclick", (event) => {
        
        if (event.target.classList.contains("user-field-btn")) {
          const listElement = event.target.closest(".accordion-item");
          
          map.fitBounds(listElement.layer.getBounds());
        }
    });

    sidebar.addEventListener("click", (event) => {
      const clickedElement = event.target;
      let featureGroup = getFeatureGroup()
      if (clickedElement.classList.contains("user-field-header") || clickedElement.classList.contains("user-field-btn")) {
        const leafletId = clickedElement.getAttribute("leaflet-id");
        console.log("user-field-header clicked", leafletId);

        selectUserField(getUserFieldIdByLeafletId(leafletId), getProject(), featureGroup);
        
      } else if (clickedElement.classList.contains("user-field-action")) {
        const leafletId = clickedElement.getAttribute("leaflet-id");
        console.log("user-field-action clicked", leafletId);
        let userFields = getUserFields();
        const userField = userFields[leafletId];

        if (clickedElement.classList.contains("delete")) {
          let confirmDelete = confirm(`Are you sure to delete ` + userField.name + "?");
          if (confirmDelete) {
            
            let layer = featureGroup.getLayer(userField.leafletId);
            delete userFields[userField.leafletId];
            featureGroup.removeLayer(layer); // removes shape from map

            const listElement = document.getElementById("accordion-"+leafletId);
            listElement.remove(); // removes HTML element from sidebar
            // removes field from db
            console.log("delete UserField ", userField)
            fetch(`/drought/delete-user-field/${userField.id}/`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
              }}).then(response => response.json())
              .then(data => {
                handleAlerts(data.message);
                console.log("Delete Success");
              })
              .catch(error => {
                console.log(error);
              });
          }
        } else if (clickedElement.classList.contains("field-menu")) {
          fetch(`field-projects-menu/${userField.id}/`)
          .then(response => response.json())
          .then(data => {
            console.log("data", data);
          // TODO the hardcoded # fieldMenuModal is triggered from button
          const modalElement = document.getElementById('fieldMenuModal');
          modalElement.querySelector('.modal-title').textContent = `Projekte in ${userField.name}`;

            const table = modalElement.querySelector('.project-table');
            table.innerHTML = '';
            const headerRow = document.createElement('tr');
            headerRow.innerHTML = `
              <th>Name</th>
              <th>Last Modified</th>
              <th>Actions</th>
            `;
            table.appendChild(headerRow);
            data.projects.forEach(project => {
              const tableRow = document.createElement('tr');
              // tableRow.classList.add('list-group-item');
              tableRow.innerHTML = `
              <td>${project.name}</td>
              <td>${project.last_modified}</td>
              <td>
                <button type="button" class="btn btn-primary btn-sm open-project" data-project-id="${project.id}">
                  Load
                </button>
              </td>
              `;
              table.appendChild(tableRow);
            });
            const fieldMenuModal = new bootstrap.Modal(modalElement);
            fieldMenuModal.show();

            modalElement.addEventListener('click', (event) => {
              if(event.target.classList.contains('open-project')) {
                const projectId = event.target.getAttribute('data-project-id');
                loadProjectFromDB(projectId)
                .then(project => {
                  loadProjectToGui(project);
                  selectUserField(project.userField, getProject(), featureGroup);
                  
                });
                // console.log('project after loadProjectFromDb', project)
                fieldMenuModal.hide();
              }
            });
          });
        } else if (clickedElement.classList.contains("field-edit")) {
            $('#userFieldSelect').val(userField.id);
            $('#monicaProjectModal').modal('show');
        } else { return;}
        }
      });
};


function toggleUserField(switchInput,  map) {
    const leafletId = switchInput.getAttribute("leaflet-id");
    const accordion = switchInput.closest(".accordion-item");
    switchInput.checked ? map.addLayer(accordion.layer) : map.removeLayer(accordion.layer);

};

// Save a newly created userField in DB
function saveUserField(name, geomJson) {
  return new Promise((resolve, reject) => {
    const requestData = {
      csrfmiddlewaretoken: csrfToken,
      geom: JSON.stringify(geomJson.geometry),
      name: name,
    };
    fetch('save-user-field/', {
      method: "POST",
      credentials: "same-origin",
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
      handleAlerts({'success': true, 'message': 'UserField saved successfully'});
      resolve(data); 
    })
    .catch(error => {
      handleAlerts({'success': false, 'message': 'Error saving UserField: ', error});
      reject(error); 
    });
  });
};

function updateFieldSelectorOption(userField, fieldSelector) {
  
  const option = document.createElement("option");
  option.value = userField.id;
  option.text = userField.name;
  fieldSelector.add(option);
};

// Modal Userfield Name Input
function handleSaveUserField(layer, bootstrapModal) {
  const fieldNameInput = document.getElementById("fieldNameInput");
  const fieldName = fieldNameInput.value;
  let userFields = {};
          try {
            userFields = JSON.parse(localStorage.getItem('userFields'));
          } catch { ; }

  if (fieldName !== "") {
    if (Object.values(userFields).some((proj) => proj.name === fieldName)) {
      alert(`Please change the name since "${fieldName}" already exists.`);
    } else {
      var geomJson = layer.toGeoJSON();

      // userField.name = fieldName;
      saveUserField(fieldName, geomJson)
      .then((data) => {
        console.log("Data: ", data);
        var layerGeoJson = L.geoJSON(data.geom_json);
        const userField = new UserField(
          data.name,
          // layerGeoJson,
          data.id,  
        );
        
        featureGroup.addLayer(layerGeoJson);
        // temporary layer is removed from the map
        featureGroup.removeLayer(layer);
        userField.leafletId  = featureGroup.getLayerId(layerGeoJson);
        
        userFields[userField.leafletId] = userField;
        localStorage.setItem('userFields', JSON.stringify(userFields));

        addLayerToSidebar(userField, layerGeoJson);
        selectUserField(userField.id);
        const fieldSelector = document.getElementById("userFieldSelect");
        updateFieldSelectorOption(userField, fieldSelector);
      })
      .catch((error) => {
        console.log("Error: ", error);
      });
      // reset name input field
      fieldNameInput.value = '';
    }
  } else {
    alert("This field cannot be empty. Please enter a name!");
  }
  bootstrapModal.hide();
};


function dismissPolygon(layer, modalInstance) {
  modalInstance.hide();
  // temporary layer is removed from the map
  featureGroup.removeLayer(layer);
};



export const addLayerToSidebar = (userField, layer) => {
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
  };



  // Load all user fields from DB
export async function getData (loadDataUrl, featureGroup) {
  let userFields = {};
  fetch(loadDataUrl, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
  })
  .then(response => response.json())
  .then(data => {
    // clear all userFields from map and sidebar
    $("#display-data").empty();
    const userFieldsDb = data.user_fields;
    
    userFieldsDb.forEach((el) => {
      var layer = L.geoJSON(el.geom_json);
      layer.bindTooltip(el.name);
      // console.log("getData, element: ", el);
      const userField = new UserField(
        el.name,
        // layer,
        el.id,
        el.user_projects    
      );
      // Add the layer to the droughtFeutureGroup layer group
        featureGroup.addLayer(layer);
        userField.leafletId  = featureGroup.getLayerId(layer);
        userFields[userField.leafletId ] = userField;
        // localStorage.setItem('userFields', JSON.stringify(userFields));
        console.log("getData, userFields: ", userFields);
        addLayerToSidebar(userField, layer);
    });
    localStorage.setItem('userFields', JSON.stringify(userFields))
  })
  .catch(error => {
    console.log(error);
  });
};






