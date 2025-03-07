import { getGeolocation } from '/static/shared/utils.js';
import { MonicaProject,  loadProjectFromDB, loadProjectToGui, handleDateChange } from '/static/monica/monica_model.js';
import { getCSRFToken, handleAlerts } from '/static/shared/utils.js';
export class UserField {
  constructor(name, id=null, userProjects=[]) {
    this.name = name;
    // this.layer = layer;
    this.id = id;
    this.userProjects = userProjects;
  }
};


const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osmAttrib =
  '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
export const osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib });

const satelliteUrl =
  "http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const satelliteAttrib =
  "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community";
const satellite = L.tileLayer(satelliteUrl, {
  maxZoom: 18,
  attribution: satelliteAttrib,
});

const topoUrl = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png";
const topoAttrib =
  'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)';
const topo = L.tileLayer(topoUrl, { maxZoom: 18, attribution: topoAttrib });

export const projectRegion = new L.geoJSON(project_region, {
    attribution: 'Project Region',
    onEachFeature: function (feature, layer) {
      layer.bindTooltip(feature.properties.name);
  }
});

// basemaps
export const baseMaps = {
    "Open Street Maps": osm,
    Satellit: satellite,
    Topomap: topo,
  };

//  export function enhanceMap (map, osm) {
//   map.addLayer(osm);

//   $(".leaflet-control-zoom").append(
//     '<a class="leaflet-control-home" href="#" role="button" title="Project area" area-label="Project area"><i class="bi bi-bullseye"></i></a>',
//     '<a class="leaflet-control-geolocation" href="#" role="button" title="My location" area-label="User location"><i class="bi bi-geo"></i></a>'
//   );

//   const mapScale = new L.control.scale({
//     position: "bottomright",
//   }).addTo(map);

//   return map;
//   };

  //Map with open street map,opentopo-map and arcgis satellite map
// export const map = enhanceMap(
//   new L.Map("map", {
//     zoomSnap: 0.25,
//     wheelPxPerZoomLevel: 500,
//     inertia: true,
//     tapHold: true,
//   })
// );

export const map = new L.Map("map", {
      zoomSnap: 0.25,
      wheelPxPerZoomLevel: 500,
      inertia: true,
      tapHold: true,
    }).addLayer(osm);

  const mapScale = new L.control.scale({
    position: "bottomright",
  }).addTo(map);
  
// map = enhanceMap(map);


export function openUserFieldNameModal(layer, featureGroup) {
  // Set the modal content (e.g., name input)
  const modal = document.querySelector('#userFieldNameModal');

  const bootstrapModal = new bootstrap.Modal(modal);
  bootstrapModal.show();

  // Add event listeners for the save and dismiss actions
  modal.querySelector('#btnUserFieldSave').onclick = () => handleSaveUserField(layer, bootstrapModal, featureGroup);
  modal.querySelector('#btnUserFieldDismiss').onclick = () => dismissPolygon(layer, bootstrapModal, featureGroup);
  modal.querySelector('#btnUserFieldDismissTop').onclick = () => dismissPolygon(layer, bootstrapModa, featureGroup);
};

export function initializeDrawControl(map, featureGroup) {
  const drawControl = new L.Control.Draw({
    position: "topright",
    edit: {
      featureGroup: featureGroup,
    },
    draw: {
      circlemarker: false,
      polyline: false,
      polygon: {
        shapeOptions: {
          color: "#000000",
        },
        allowIntersection: false,
        showArea: true,
      },
    },
  });
  map.addControl(drawControl);
};

export function initializeMapEventlisteners (map, featureGroup) {
    const chrosshair = document.getElementsByClassName("leaflet-control-home")[0];
    chrosshair.addEventListener("click", () => {
    try {
        var bounds = featureGroup.getBounds();
        map.fitBounds(bounds);
    } catch {
        return;
    }
    });

    const locationPin = document.getElementsByClassName("leaflet-control-geolocation")[0];
    locationPin.addEventListener("click", () => {
      getGeolocation()
        .then((position) => {
          map.setView([position.latitude, position.longitude], 12);
        })
        .catch((error) => {
          console.error(error.message);
          handleAlerts({ success: false, message: error.message });
        });
    });


    map.on("draw:created", function (event) {
      let layer = event.layer;
      // is added to the map only for display
      featureGroup.addLayer(layer);
    
      openUserFieldNameModal(layer, featureGroup);
    });

    featureGroup.on("click", function (event) {
      let leafletId = Object.keys(event.layer._eventParents)[0];
      let userFieldId = getUserFieldIdByLeafletId(leafletId);
      let project = MonicaProject.loadFromLocalStorage();
      selectUserField(userFieldId, project, featureGroup);
      // highlightPolygon(event.layer)
    });
};

  //add map scale


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

export function createNUTSSelectors({getFeatureGroup}) {
  // Create a LayerGroup to hold the displayed polygons
  // const stateCountyDistrictLayer = L.layerGroup().addTo(map);
  const stateCountyDistrictLayer = new L.FeatureGroup().addTo(map);
  stateCountyDistrictLayer.on("click", function (event) {
    console.log("stateCountyDistrictLayer click event: ", event);
  
    // Get the clicked layer
    let clickedLayer = event.layer;
    
    // Confirm action with the user
    if (confirm("Save this region as a user field?")) {
      openUserFieldNameModal(clickedLayer, getFeatureGroup()) 
    }
  });
  
  
  stateCountyDistrictLayer.on("click", function (event) {
    console.log("stateCountyDistrictLayer click event: ", event);
  });
  
  // Handle dropdown menu change event
  // Multiple Select from https://www.cssscript.com/select-box-virtual-scroll/
  VirtualSelect.init({ 
    ele: '#stateSelect',
    placeholder: 'Bundesland',
    required: false,
    disableSelectAll: true,
  });
  VirtualSelect.init({ 
    ele: '#districtSelect',
    placeholder: 'Regierungsbezirk',
    required: false,
    disableSelectAll: true,
  });
  VirtualSelect.init({ 
    ele: '#countySelect',
    placeholder: 'Landkreis',
    required: false,
    disableSelectAll: true,
  });
  
  var administrativeAreaDiv = document.querySelectorAll('div.administrative-area');
  var selectedAdminAreas = {
    states: [],
    counties: [],
    districts: [],
  };
  
  
  administrativeAreaDiv.forEach(function (areaDropdown) {
    areaDropdown.addEventListener('change', function (event) {
      stateCountyDistrictLayer.clearLayers();
      var name = areaDropdown.getAttribute("name");
      var selectedOptions = areaDropdown.value;
      selectedAdminAreas[name] = selectedOptions;
  
      for (let key in selectedAdminAreas) {
        if (selectedAdminAreas[key].length > 0) {
          selectedAdminAreas[key].forEach(function (polygon) {
            var url = loadNutsUrl + key + '/' + polygon + '/';
          console.log("URL", url)
          var color = '';
          if (key == 'states') {
              color = 'purple';
          } else if (key == 'counties') {
              color = 'blue';
          } else if (key == 'districts') {
              color = 'green';
          }
          var geojsonLayer = new L.GeoJSON.AJAX(url, {
              style: {
                  color: color 
              },
              onEachFeature: function (feature, layer) {
                  layer.bindTooltip(`${feature.properties.nuts_name}`);
                  layer.setStyle({
                    fill: false, 
                  });
              }
          });
          console.log("geojsonLayer", geojsonLayer)
          geojsonLayer.addTo(stateCountyDistrictLayer);
          });
        }
      }
    }); 
  });
  
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
  if (!project) {
    project = MonicaProject.loadFromLocalStorage();
  }

  console.log("selectUserField featureGroup", featureGroup);
  // const project = MonicaProject.loadFromLocalStorage();
  if (project && project.userField && project.userField != userFieldId && project.id) {
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
    console.log('Else if action')
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
                "X-CSRFToken": getCSRFToken(),
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
      csrfmiddlewaretoken: getCSRFToken(),
      geom: JSON.stringify(geomJson.geometry),
      name: name,
    };
    fetch('save-user-field/', {
      method: "POST",
      credentials: "same-origin",
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
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
export function handleSaveUserField(layer, bootstrapModal, featureGroup) {

  
  const fieldNameInput = document.getElementById("fieldNameInput");
  const fieldName = fieldNameInput.value;
  let userFields = {};
          try {
            userFields = JSON.parse(localStorage.getItem('userFields'));
          } catch { ; }

  if (fieldName !== "") {
    if (Object.values(userFields).some((uf) => uf.name === fieldName)) {
      handleAlerts({'success': false, 'message': `Please change the name since "${fieldName}" already exists.`});
    } else {
      var geomJson = layer.toGeoJSON();

      // userField.name = fieldName;
      saveUserField(fieldName, geomJson)
      .then((data) => {
        console.log("Data: ", data);
        var layerGeoJson = L.geoJSON(data.geom_json);
        const userField = new UserField(
          data.name,
          data.id,  
        );
        
        featureGroup.addLayer(layerGeoJson);
        // temporary layer is removed from the map
        featureGroup.removeLayer(layer);
        userField.leafletId  = featureGroup.getLayerId(layerGeoJson);
        
        userFields[userField.leafletId] = userField;
        localStorage.setItem('userFields', JSON.stringify(userFields));

        addLayerToSidebar(userField, layerGeoJson);
        selectUserField(userField.id, null, featureGroup);
        const fieldSelector = document.getElementById("userFieldSelect");
        updateFieldSelectorOption(userField, fieldSelector);
      })
      // .catch((error) => {
      //   console.log("Error: ", error);
      // });
      // reset name input field
      fieldNameInput.value = '';
    }
  } else {
    alert("This field cannot be empty. Please enter a name!");
  }
  bootstrapModal.hide();
};


export function dismissPolygon(layer, modalInstance, featureGroup) {
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
        <button class=" btn user-field-btn" type="button" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" id="accordionButton-${userField.leafletId}" > 
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
      
    `;
    // adding the UserField to the HTML-list element
    accordion.layer = layer;
  
    userFieldsAccordion.appendChild(accordion);
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
        
        addLayerToSidebar(userField, layer);
    });
    localStorage.setItem('userFields', JSON.stringify(userFields))
  })
  .catch(error => {
    console.log(error);
  });
};







