import { getGeolocation } from '/static/shared/utils.js';
import { MonicaProject, loadProjectFromDB, loadProjectToGui  } from '/static/monica/monica.js';

import { ToolboxProject } from '/static/toolbox/toolbox.js';
import { getCSRFToken, handleAlerts } from '/static/shared/utils.js';
export class UserField {
  constructor(name, id=null, lat=null, lon=null, userProjects=[]) {
    this.name = name;
    // this.layer = layer;
    this.id = id;
    this.lat = lat;
    this.lon = lon;
    this.userProjects = userProjects;
  }
};


const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
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

export function enhanceMap (map) {
  
  $(".leaflet-control-zoom").append(
    '<a class="leaflet-control-home" href="#" role="button" title="Project area" aria-label="Project area"><i class="bi bi-bullseye"></i></a>',
    '<a class="leaflet-control-geolocation" href="#" role="button" title="My location" aria-label="User location"><i class="bi bi-geo"></i></a>'
  );

  const baseMapSwitches = L.control.layers(baseMaps, null, { 
    collapsed: true,
    position: "topleft"
   }).addTo(map);

  const mapScale = new L.control.scale({
    position: "bottomright",
  }).addTo(map);

  window.addEventListener('resize', () => {
    map.invalidateSize();
  });
  return map;
  };

  //Map with open street map,opentopo-map and arcgis satellite map
  // TODO change var back to const!!
export var map = enhanceMap(
  new L.Map("map", {
    zoomSnap: 0.25,
    wheelPxPerZoomLevel: 250,
    maxZoom: 18,
    minZoom: 3,
    inertia: true,
    tapHold: true,
  }).addLayer(osm)
);

export function getCircleMarkerSettings (fillColor) {
  return {
    radius: 5,
    type: 'circle',
    weight: 2,
    fillOpacity: 1,
    color: 'black',
    fillColor: fillColor
  };
};

export function getLegendItem (label, markerSettings) {
  return {
    label: label,
    ...markerSettings
  };
};

export function getLegendSettings (title, legendItems) {
  return {
    position: 'bottomright',
    collapsed: false,
    title: title,
    legends: legendItems
  };
};

export function removeLegendFromMap(map) {      
  const existingLegend = document.querySelector('.leaflet-legend');
      if (existingLegend) {
        map.removeControl(existingLegend);
      }
};

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
      edit: false,
    },
    draw: {
      circlemarker: false,
      polyline: false,
      circle: false,
      marker: false,
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


export function initializeMapEventlisteners (map, featureGroup, projectClass) {
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
      let leafletId = event.layer._leaflet_id;
  
      let userFieldId = getUserFieldIdByLeafletId(leafletId);
      let projectClass = MonicaProject
      if (window.location.pathname.endsWith('/toolbox/')) {
        projectClass = ToolboxProject
      }
      let project = projectClass.loadFromLocalStorage();
      selectUserField(userFieldId, project, featureGroup);
    });
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
};


// export function createBaseLayerSwitchGroup(baseMaps, map) {
//     const baseLayerControlList = document.getElementById("baseLayerList");
//     let html = "";

//     // Generate HTML for base layer switches
//     Object.keys(baseMaps).forEach((basemapName) => {
//         html += `
//             <li class="list-group-item">
//                 <div class="col form-check form-switch">
//                     <input 
//                         type="radio" 
//                         class="form-check-input user-field-switch basemap-switch" 
//                         data-basemap="${basemapName}">
//                     <label>${basemapName}</label>
//                 </div>
//             </li>
//         `;
//     });

//     // Insert the generated HTML
//     baseLayerControlList.innerHTML = html;
//     baseLayerCollapse.appendChild(baseLayerControlList);

//     // Set initial basemap
//     const initialBasemapSwitch = baseLayerControlList.querySelector(".basemap-switch");
//     if (initialBasemapSwitch) {
//         initialBasemapSwitch.checked = true;
//         changeBasemap(initialBasemapSwitch, baseMaps, map);
//     }
// };

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
            var url = '/drought/load_nuts_polygon/' + key + '/' + polygon + '/';
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

  // remove highlight class from all layers
  featureGroup.eachLayer(function (layer) {
    if (layer.getElement) {
      const el = layer.getElement();
      if (el) el.classList.remove("highlight");
    }
  });

  // remove highlight from all sidebar headers
  const listElements = document.querySelectorAll(".user-field-header");
  listElements.forEach(header => header.classList.remove("highlight"));

  // toggle highlight on selected layer + header
  const header = $(`#accordion-${leafletId}`);
  const layer = featureGroup.getLayer(leafletId);
  

  if (header.hasClass("highlight")) {
    header.removeClass("highlight");
    if (layer?.getElement) {
      const el = layer.getElement();
      if (el) {
        el.classList.remove("highlight");
        layer.editing.disable();
      }
    }
  } else {
    header.addClass("highlight");
    if (layer?.getElement) {
      const el = layer.getElement();
      if (el) {
        el.classList.add("highlight");
      }
    }
  }
};


export function selectUserField(userFieldId, project, featureGroup) {
    console.log("selectUserField featureGroup", project);

    const leafletId = getLeafletIdByUserFieldId(userFieldId);
    const userField = getUserFields()[leafletId];
    highlightLayer(leafletId, featureGroup);

    const needsConfirmation = (
        project && project.id &&
        (
            (project.userField && project.userField !== userFieldId) ||
            (!project.userField || project.userField === '')
        )
    );
    console.log('needsConfirmation', needsConfirmation, userFieldId, userField);

    if (needsConfirmation) {
        const isChangingExisting = !!project.userField;

        showUserFieldModal({
            title: "User Field Selection",
            text: isChangingExisting
                ? "You are changing a Monica Project's user field."
                : "You are changing a Monica Project without UserField to a SWN Project with UserField. The location of the project will be changed to the UserField location.",
            onConfirm: () => {
                applyUserFieldChange(project, userFieldId, userField, featureGroup);
            }
        });
    } else  {
        applyUserFieldChange(project, userFieldId, userField, featureGroup);
    }
};


function showUserFieldModal({ title, text, onConfirm }) {
    const modal = document.getElementById('interactionModal');
    const modalInstance = new bootstrap.Modal(modal);

    document.getElementById('interactionModalTitle').innerHTML = title;
    document.getElementById('interactionModalText').innerHTML = text;

    $('#interactionModalOK')
        .off('click')
        .on('click', () => {
            modalInstance.hide();
            onConfirm();
        });

    modalInstance.show();
}

function applyUserFieldChange(project, userFieldId, userField, featureGroup) {
    console.log('applyUserFieldChange', userFieldId, userField);
    project['userField'] = userFieldId;
    project['latitude'] = userField.lat;
    project['longitude'] = userField.lon;
    project.saveToLocalStorage();
    highlightLayer(getLeafletIdByUserFieldId(userFieldId), featureGroup);
}



function revertEdit(layer) {
  if (layer._originalLatLngs) {
    const original = L.LatLngUtil.cloneLatLngs(layer._originalLatLngs);

    // Step 1: Reset shape and visuals
    layer.setLatLngs(original);
    layer.redraw();

    // Step 2: Disable editing
    if (layer.editing && layer.editing._enabled) {
      layer.editing.disable();
    }

    // Step 3: Clean up vertices handlers safely
    if (layer.editing && Array.isArray(layer.editing._verticesHandlers)) {
      layer.editing._verticesHandlers.forEach(handler => {
        if (handler._markerGroup && handler._markerGroup.clearLayers) {
          handler._markerGroup.clearLayers();
        }
      });
      layer.editing._verticesHandlers = [];
    }

    // Step 4: Reset the editing plugin completely
    layer.editing = new L.Edit.Poly(layer);

    // Step 5: Clean up the original backup
    delete layer._originalLatLngs;

    console.log("Edits truly reverted (safe).");
  }
}

// TODO: move this to three_split.js
$('#toggleBottomFullscreen').on('click', function () {
    const isFullscreen = $(this).find('i').hasClass('bi-fullscreen-exit');

    if (isFullscreen) {
      // Exit fullscreen - restore layout
      $('.panel-top').css('height', '60%');
      $('.panel-left').css('visibility', 'visible');
      $('#main-navbar').show();
      $('.leaflet-control-container').show(); 
      $('#toggleBottomFullscreen').html('<i class="bi bi-arrows-fullscreen"></i>');
      map.invalidateSize();

    } else {
      // Enter fullscreen mode - shrink top, hide left
      $('.panel-top').css('height', '20%'); // or even '5%' if you want it smaller
      $('.panel-left').css('visibility', 'hidden');
            // hide the sidebar
      $('#main-navbar').hide(); // hide the navbar
      $('.leaflet-control-container').hide(); // hide Leaflet controls
      map.invalidateSize()
      const highlightedElement = $('#userFieldsAccordion').find('li.highlight')
      if (highlightedElement.length > 0) {
        console.log(highlightedElement)
        
        map.fitBounds(highlightedElement[0].layer.getBounds());
      }
        $('#toggleBottomFullscreen').html('<i class="bi bi-fullscreen-exit"></i>');
      }
    });


// TODO rename to MapEventhandler
export function initializeSidebarEventHandler({projectClass, sidebar, map, baseMaps, overlayLayers, getUserFields, getFeatureGroup, getProject }) {
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
          console.log('switchInput: ', switchInput);
            toggleUserField(switchInput, getFeatureGroup());
        }
    });

    let clickTimeout;

    sidebar.addEventListener("dblclick", (event) => {
      clearTimeout(clickTimeout); // prevent single click logic
      
        const listElement = event.target.closest("li");
        map.fitBounds(listElement.layer.getBounds());
        console.log("DOUBLE CLICK");
      
    });

    sidebar.addEventListener("click", (event) => {
      console.log("sidebar click event", event.target.classList);
      const clickedElement = event.target;
      let featureGroup = getFeatureGroup()
  
      
      if (clickedElement.classList.contains("user-field-action")) {
        const leafletId = clickedElement.getAttribute("leaflet-id");
        console.log("user-field-action clicked", leafletId);
        let userFields = getUserFields();
        const userField = userFields[leafletId];

        if (clickedElement.classList.contains("delete")) {
          let confirmDelete = confirm(`Are you sure to delete ` + userField.name + "?");
          if (confirmDelete) {
            
            let layer = featureGroup.getLayer(leafletId);
            delete userFields[leafletId];
            featureGroup.removeLayer(layer); // removes shape from map

            const listElement = document.getElementById("accordion-"+leafletId);
            listElement.remove(); // removes HTML element from sidebar
            // removes field from dbprojectClass
            console.log("delete UserField ", userField)
            fetch(`delete-user-field/${userField.id}/`, {
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
          console.log('field-menu clicked');
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
        } else if (clickedElement.classList.contains("field-project-add")) {
          $('#userFieldSelect').val(userField.id);
          if (window.location.pathname.endsWith('/drought/') || window.location.pathname.endsWith('/monica/')) {
            localStorage.setItem('userFieldId', clickedElement.getAttribute('user-field-id'));

            
            $('#monicaProjectModal').modal('show');
          } else if (window.location.pathname.endsWith('/toolbox/')){
            $('#toolboxProjectModal').modal('show');
          }
        } else if (clickedElement.classList.contains('field-edit')) {
          console.log('field-edit clicked');
          let layer = featureGroup.getLayer(leafletId);
        
          if (layer && layer.editing && !layer.editing._enabled) {
            console.log('Edit enabling')
            // Save original latlngs for cancel
            layer._originalLatLngs = L.LatLngUtil.cloneLatLngs(layer.getLatLngs());
            layer.editing.enable();
        
            // Use plain HTML string for popup content
            const popupHtml = `
              <strong>Editing field</strong><br>
              <button class="btn btn-sm btn-success" id="btnUpdateUserField">Speichern</button>
              <button class="btn btn-sm btn-danger" id="btnCancelEditUserField">Abbrechen</button>
            `;
        
            // Bind and open the popup
            
        
            // Listen for popupopen ON THE MAP
            function onPopupOpen(e){
              console.log("On Popup opened");
              if (e.popup._source !== layer) return;
        
              const popupEl = e.popup.getElement();
              const saveBtn = popupEl.querySelector('#btnUpdateUserField');
              const cancelBtn = popupEl.querySelector('#btnCancelEditUserField');
              let editConfirmed = false;
        
              // Save button
              L.DomEvent.on(saveBtn, 'click', () => {
                console.log('Save clicked');
                editConfirmed = true;
                saveUserField(userField.name, userField.id, layer);
                layer.editing.disable();
                layer.closePopup();
                layer.unbindPopup(); // Prevent popup from reopening later
              });
        
              // Cancel button
              L.DomEvent.on(cancelBtn, 'click', () => {
                console.log('Cancel clicked');
                editConfirmed = false;
                revertEdit(layer);
                layer.editing.disable();
                layer.closePopup();
                layer.unbindPopup(); // Also prevent reappearing
              });
        
              // Popup close fallback — only revert if NOT confirmed
              function onPopupClose(e){
                console.log('On Popup close', layer)
                if (e.popup._source === layer && !editConfirmed) {
                  console.log('Popup closed without save – reverting');
                  revertEdit(layer);
                  layer.editing.disable();
                  layer.unbindPopup(); // Cleanup
                  console.log('Popup closed:', layer);
                }
                map.off('popupclose', onPopupClose);
              };
        
              map.on('popupclose', onPopupClose);
              map.off('popupopen', onPopupOpen); // Prevent multiple bindings
            };
        
            map.on('popupopen', onPopupOpen);
            layer.bindPopup(popupHtml).openPopup();
          } else {
            console.log('Edit disabling');
            layer.editing.disable();
            layer.closePopup();
            layer.unbindPopup(); // Prevent popup from reopening later
          }

        }
         else { return;}
        } else if (clickedElement.closest("li") && clickedElement.closest("li").hasAttribute("leaflet-id")) {
          const listEl = clickedElement.closest("li");
        clearTimeout(clickTimeout);
        clickTimeout = setTimeout(() => {
          // clickTimeout = null;
          const leafletId = listEl.getAttribute("leaflet-id");
          console.log("user-field-header clicked", leafletId);
          selectUserField(getUserFieldIdByLeafletId(leafletId), getProject(), featureGroup);
        }, 250); }
      });
};


function toggleUserField(switchInput,  map) {
    const leafletId = switchInput.getAttribute("leaflet-id");
    const listElement = switchInput.closest("li");
    switchInput.checked ? map.addLayer(listElement.layer) : map.removeLayer(listElement.layer)
};

// Save a newly created userField in DB
function saveUserField(name, id, layer) {
  let geomJson = layer.toGeoJSON();
  return new Promise((resolve, reject) => {
    const requestData = {
      geom: JSON.stringify(geomJson.geometry),
      name: name,
      id: id,
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

export function updateUserField(userField, layer) {
  let geomJson = layer.toGeoJSON();
  return new Promise((resolve, reject) => {
    const requestData = {
      geom: JSON.stringify(geomJson.geometry),
      userField: userField,
    };
    fetch(`update-user-field/${userField.id}/`, {
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

  let userFieldsName;
  if (window.location.pathname.endsWith('/drought/')) {
    userFieldsName = 'droughtUserFields';
  } else if (window.location.pathname.endsWith('toolbox/')) {
    userFieldsName = 'toolboxUserFields'
  } else {
    userFieldsName = '';
  }

  const fieldNameInput = document.getElementById("fieldNameInput");
  const fieldName = fieldNameInput.value;
  let userFields = {};
          try {
            userFields = JSON.parse(localStorage.getItem('userFields'));
          } catch { ; }

  if (fieldName !== "") {
    if (Object.values(userFields).some((uf) => uf.name === fieldName)) {
      handleAlerts({'success': false, 'message': `Please change the name since "${fieldName}" already exists.`});
      setTimeout(() => {
        bootstrapModal.show();
      }
      , 2000);
    } else {
      

      // userField.name = fieldName;
      saveUserField(fieldName, null, layer)
      .then((data) => {
        console.log("Data: ", data);
        var layerGeoJson = L.geoJSON(data.geom_json,
          {
            onEachFeature: function (f, l) {
              l.bindTooltip(fieldName);
              featureGroup.addLayer(l);
            },
          }
        );
        const userField = new UserField(
          data.name,
          data.id,  
          data.lat,
          data.lon,
        );
        layer.remove(); // removes the drawn shape from map
        const newLayer = Object.values(layerGeoJson._layers)[0];
        // featureGroup.addLayer(newLayer);
        userField.leafletId  = featureGroup.getLayerId(newLayer);
        
        userFields[userField.leafletId] = userField;
        localStorage.setItem('userFields', JSON.stringify(userFields));

        addLayerToSidebar(userField, newLayer);
      })

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

const tooltip = {
  de: {
    edit: "Feld bearbeiten",
    createProject: "Projekt erstellen",
    loadProject: "Projekt laden",
    delete: "Project löschen",
  }
}


export const addLayerToSidebar = (userField, layer) => {
    // new Accordion UserField style
    const accordion = document.createElement("li");
    accordion.setAttribute("class", "list-group-item user-field-header");
    accordion.setAttribute("id", `accordion-${userField.leafletId}`);
    accordion.setAttribute("leaflet-id", userField.leafletId);
    accordion.setAttribute("user-field-id", userField.id);
  
    accordion.innerHTML = `
      <div 
        class="d-flex justify-content-between align-items-center" 
        id="accordionHeader-${userField.leafletId}" 
        user-field-id="${userField.id}"
        leaflet-id="${userField.leafletId}"
      >
        <div class="form-check form-switch h6">  
          <input type="checkbox" class="form-check-input user-field-switch" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" id="fieldSwitch-${userField.leafletId}" checked>
          <label>${userField.name}</label>
        </div>

        <div class="d-flex gap-1">
          <form id="deleteAndCalcForm-${userField.leafletId}" class="d-flex gap-1">
            <button type="button" class="btn btn-outline-secondary btn-sm field-name user-field-action field-edit" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${tooltip.de.edit}">
              <span><i class="bi bi-pencil-square user-field-action field-edit" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm field-name user-field-action field-project-add" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${tooltip.de.createProject}">
              <span><i class="bi bi-plus user-field-action field-project-add" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm user-field-action field-menu" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${tooltip.de.loadProject}">
              <span><i class="bi bi-list user-field-action field-menu" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm user-field-action delete" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${tooltip.de.delete}">
              <span><i class="bi bi-trash user-field-action delete" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
          </form>
        </div>  
      </div>
    `;

    

    accordion.layer = layer;
    const userFieldsAccordion = document.getElementById("userFieldList");
    // console.log("userFieldsAccordion", userFieldsAccordion);
    userFieldsAccordion.appendChild(accordion);
  };

  // Load all user fields from DB
export async function getUserFieldsFromDb (featureGroup) {
  let userFields = {};
  fetch('get-user-fields/', {
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
      // var layer = L.geoJSON(el.geom_json);
      let layerGeoJson = L.geoJson(el.geom_json, {
        className: 'user-field',
        onEachFeature: function (feature, layer) {
          layer.bindTooltip(el.name);
          featureGroup.addLayer(layer);
        },
      });

      // console.log("getData, element: ", el);
      const userField = new UserField(
        el.name,
        el.id,  
        el.centroid_lat || null,
        el.centroid_lon || null,
        el.user_projects || [] // Ensure user_projects is an array
      );

      // Add the layer to the droughtFeatureGroup layer group
      // featureGroup.addLayer(layer);
      const newLayer = Object.values(layerGeoJson._layers)[0];
      // featureGroup.addLayer(newLayer);
      userField.leafletId  = featureGroup.getLayerId(newLayer);
      userFields[userField.leafletId ] = userField;
      // console.log("getData, userFields: ", userFields);
      addLayerToSidebar(userField, newLayer);

    });
    localStorage.setItem('userFields', JSON.stringify(userFields))
  })
  .catch(error => {
    console.log(error);
  });
};


