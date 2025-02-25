

import { MonicaProject,  loadProjectFromDB, loadProjectToGui } from '/static/monica/monica_model.js';
import { getGeolocation } from '/static/shared/utils.js';
import { handleAlerts } from '/static/swn/js/base.js';



getGeolocation()
    .then((position) => {
        console.log("Position:", position);
        $('#id_latitude').val(position.latitude);
        $('#id_longitude').val(position.longitude);
    })
    .catch((error) => {
        console.error(error.message);
        handleAlerts({ success: false, message: error.message });
    });


document.addEventListener("DOMContentLoaded", () => {
  $('#coordinateFormCard').hide();
  
  let csrfToken = document.cookie
    .split("; ")
    .find(row => row.startsWith("csrftoken="))
    .split("=")[1];

  // Update the CSRF token value if it changes
  function updateCsrfToken() {
    console.log("updateCsrfToken");
    csrfToken = document.cookie
      .split("; ")
      .find(row => row.startsWith("csrftoken="))
      .split("=")[1];
    return csrfToken;
  };

  // TODO userfield highlight
  $('#userFieldSelect').on('change', function () {
    const project = MonicaProject.loadFromLocalStorage();
    // get centroid of the userfield
    console.log('userFieldSelect change event');
    var userFieldId = $(this).val();
    let leafletId = getLeafletIdByUserFieldId(userFieldId);
    highlightLayer(leafletId);
    project.userField = userFieldId;
    project.saveToLocalStorage();
    // TODO using the userFields's centroid
    // if (userFieldId != null) {
    //     fetch('/drought/get_lat_lon/' + userFieldId + '/')
    //   .then((response) => response.json())
    //   .then((data) => {
    //     console.log('data', data);
    //     $('#id_latitude').val(data.lat);
    //     $('#id_longitude').val(data.lon);
    //   });
    // }
  });

    $('#todaysDatePicker').on('changeDate', function () {
        console.log()
        const project = MonicaProject.loadFromLocalStorage();
        console.log("EvenLister todaysDatePicker changeDate", project)
        project.todaysDate = $(this).datepicker('getUTCDate');
        project.saveToLocalStorage();
        
    });

// -----------User Field Name Modal -----------------

// -------------MAP --------------------------------------


const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osmAttrib =
  '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib });

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

// Bounds for DEM image overlay
const demBounds = [
  [47.136744752, 15.57241882],
  [55.058996788, 5.564783468],
];
const droughtBounds = [
  [46.89, 15.33],
  [55.31, 5.41],
];
const demOverlay = L.imageOverlay(demUrl, demBounds, { opacity: 0.5 });
const droughtOverlay = L.imageOverlay(droughtUrl, droughtBounds, { opacity: 0.5 });
const projectRegion = new L.geoJSON(project_region, {
    attribution: 'Project Region',
    onEachFeature: function (feature, layer) {
      layer.bindTooltip(feature.properties.name);
  }
});

// basemaps
const baseMaps = {
  "Open Street Maps": osm,
  Satellit: satellite,
  Topomap: topo,
};




//Map with open street map,opentopo-map and arcgis satellite map
// opens at Müncheberg by default
const map = new L.Map("map", {
  layers: [osm],
  center: new L.LatLng(52.338145830363914, 13.85877631507592),
  zoom: 8,
  zoomSnap: 0.25,
  wheelPxPerZoomLevel: 500,
});


//add map scale
const mapScale = new L.control.scale({
  position: "bottomright",
}).addTo(map);


// handles clicks on a userField layer in the map
var featureGroup = new L.FeatureGroup()
map.addLayer(featureGroup);


featureGroup.bringToFront();

featureGroup.on("click", function (event) {
  let leafletId = Object.keys(event.layer._eventParents)[0];
  highlightLayer(leafletId);
  console.log("droughtFeutureGroup click event: highlight ", leafletId, event.layer);
  // highlightPolygon(event.layer)
});

// highlight layer and li element on click in the sidebar

function highlightLayer(id) {
  console.log("HIGHLIGHT", id);
  // remove highlight from all layers
  featureGroup.eachLayer(function (layer) {
    const key = Object.keys(layer._layers)[0];
    const value = layer._layers[key];
    value._path.classList.remove("highlight");
  });
  // deselect layer/ header: remove highlight class from  header
  if ($(`#accordionHeader-${id}`).hasClass("highlight")) {
    $(`#accordionHeader-${id}`).removeClass("highlight");

    
    let key = Object.keys(featureGroup._layers[id]._layers)[0]
    console.log("Key: ", key, "id: ", id)
     featureGroup._layers[id]._layers[key]._path.classList.remove('highlight');
  } else { // select layer/ header: 

      const accordionUserFieldHeaders = document.querySelectorAll('#accordionUserFields .accordion-header');
      accordionUserFieldHeaders.forEach(header => {
        header.classList.remove('highlight')
      });

    $(`#accordionHeader-${id}`).addClass("highlight")
    // add highlight class to leaflet layer
    let key = Object.keys(featureGroup._layers[id]._layers)[0]
    featureGroup._layers[id]._layers[key]._path.classList.add('highlight');
  };
};


      
function getLeafletIdByUserFieldId(id) {
  const entry = Object.values(userFields).find(field => field.id == id);
  console.log("getLeafletIdByUserFieldId", id, entry, userFields);
  return entry ? entry.leafletId : null;
}
  
// Draw functionality
var drawControl = new L.Control.Draw({
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

// zoom to user's layers via chrosshair
// added back-to-home bullseyer button to zoom controls
$(".leaflet-control-zoom").append(
  '<a class="leaflet-control-home" href="#" role="button" title="Project area" area-label="Project area"><i class="bi bi-bullseye"></i></a>'
);
const chrosshair = document.getElementsByClassName("leaflet-control-home")[0];

chrosshair.addEventListener("click", () => {
  try {
    var bounds = featureGroup.getBounds();
    map.fitBounds(bounds);
  } catch {
    return;
  }
});



//-------------------- Baselayers ------------------------------
const leafletSidebarContent = document.querySelector(".sidebar-content");

const baseLayerCollapse = document.getElementById("baseLayerCollapse")

const overlayLayers = {
  "droughtOverlay": droughtOverlay,
  "demOverlay": demOverlay,
  "projectRegion": projectRegion,

};


// ------------------- Sidebar eventlisteners -------------------

// -------------------Sidebar new----------------


var accordionUserFields = document.getElementById("accordionUserFields")
var userFieldsAccordion = document.getElementById("userFieldsAccordion");

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
});

// -------------------Sidebar new end----------------
leafletSidebarContent.addEventListener("click", (event) => {
  const clickedElement = event.target;
  if (clickedElement.classList.contains("user-field-header") || clickedElement.classList.contains("user-field-btn")) {
    const leafletId = clickedElement.getAttribute("leaflet-id");
    console.log("user-field-header clicked", leafletId);
   
    highlightLayer(leafletId);
  } else if (clickedElement.classList.contains("user-field-action")) {
    const leafletId = clickedElement.getAttribute("leaflet-id");
    console.log("user-field-action clicked", leafletId);
    const userField = userFields[leafletId];

    if (clickedElement.classList.contains("delete")) {
      let confirmDelete = confirm(`Are you sure to delete ` + userField.name + "?");
      if (confirmDelete) {
        delete userFields[userField.leafletId];
        userField.layer.remove(); // removes shape from map
        const listElement = document.getElementById("accordion-"+leafletId);
        listElement.remove(); // removes HTML element from sidebar
        // removes field from db
        console.log("delete UserField ", userField)
        fetch(deleteUrl + userField.id, {
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
        data.projects.forEach(project => {
          const tableRow = document.createElement('tr');
          // tableRow.classList.add('list-group-item');
          tableRow.innerHTML = `
          <td>${project.name}</td>
          <td>${project.creation_date}</td>
          <td>${project.last_modified}</td>
          <td>
            <button type="button" class="btn btn-primary btn-sm open-project" data-project-id="${project.id}" data-user-field-id="${userField.id}">
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
            const userFieldId = event.target.getAttribute('data-user-field-id');
            console.log("open-project clicked", projectId, userFieldId);
            const project = loadProjectFromDB(projectId);
            loadProjectToGui(project);
            fieldMenuModal.hide();
            // TODO open project
          }
        });
      });
    } else if (clickedElement.classList.contains("field-edit")) {
        // TODO the hardcoded modal is triggered from button
        console.log("field-edit clicked", leafletId, userField.id);
        // select the userField in the modal
        $('#userFieldSelect').val(userField.id);
        $('#monicaProjectModal').modal('show');
    } else { console.log("else in eventlistener") }
    }
  });

//event bubbling for the switches and menus in the sidebar
leafletSidebarContent.addEventListener("change", (event) => {
  const switchInput = event.target;

  if (switchInput.classList.contains("basemap-switch")) {
    changeBasemap(switchInput);
  } else if (switchInput.classList.contains("layer-switch")) {
    const layerId = switchInput.getAttribute("data-layer");
    if (switchInput.checked) {
      // Add the layer
      map.addLayer(overlayLayers[layerId]);
    } else {
      // Remove the layer
      map.removeLayer(overlayLayers[layerId]);
    }
    } else if (switchInput.classList.contains("layer-opacity")) {
      const overlayId = switchInput.getAttribute("data-layer");
      overlayLayers[overlayId].setOpacity(switchInput.value);
      const opacityValue = switchInput.value;
      overlayLayers[overlayId].setOpacity(opacityValue);
    } else if (switchInput.classList.contains("overlay-switch")) {
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
    } else if (switchInput.classList.contains("user-field-switch")) {
      const leafletId = switchInput.getAttribute("leaflet-id");
      const userField = userFields[leafletId];
      if (switchInput.checked) {
        map.addLayer(userField.layer);
      } else {
        map.removeLayer(map._layers[leafletId]);
      };
    };
});


// Create a function to handle the basemap change
function changeBasemap(basemap) {
  if (!basemap || !basemap.getAttribute) {
    return;
  } else {
    // Update the map's basemap
    const selectedBasemap = basemap.getAttribute("data-basemap");
    map.eachLayer((layer) => {
      if (layer instanceof L.TileLayer && layer.options.name !== selectedBasemap) {
        map.removeLayer(layer);
      }
    });
    map.addLayer(baseMaps[selectedBasemap]);
  };
};

// Create a function to handle the creation of the Baselayer Switches in the sidebar
let switchGroupId = 1; 

function createBaseLayerSwitchGroup() {
  let initialBasemapChecked = false; 
  const baseLayerControlList = document.getElementById("baseLayerList");
  // Loop through the baseMaps and create the control switches
  for (const [basemapName, basemapLayer] of Object.entries(baseMaps)) {
    const li = document.createElement("li");
    li.classList.add("list-group-item")
    const switchDiv = document.createElement("div");
    switchDiv.classList.add("col", "form-check", "form-switch")
    const switchInput = document.createElement("input");
    switchInput.type = "radio";
    switchInput.name = `switchGroup${switchGroupId}`; // Assign the same name to all switch inputs in a group
    switchInput.classList.add("form-check-input", "user-field-switch");
    const switchLabel = document.createElement("label");
    switchDiv.appendChild(switchInput);
    switchDiv.appendChild(switchLabel);
    li.appendChild(switchDiv);
    switchLabel.textContent = basemapName;
    switchInput.classList.add("basemap-switch");
    switchInput.setAttribute("data-basemap", basemapName);
    baseLayerControlList.appendChild(li);
  }
  baseLayerCollapse.appendChild(baseLayerControlList);
  switchGroupId++;

  if (!initialBasemapChecked) {
    const initialBasemapSwitches = baseLayerControlList.querySelector(".basemap-switch");
    initialBasemapSwitches.checked = true;
    changeBasemap(initialBasemapSwitches);
    initialBasemapChecked = true;
  }
};
createBaseLayerSwitchGroup();



//-------------------- Baselayers end ------------------------------

//-------------------- Overlays start ------------------------------
// const overlayLayerCollapses = document.querySelectorAll(".overlay-layer-collapse");


//---------------MAP END-------------------------------
var userFields = {};



// User Field Name Modal


const loadUrl = "/drought/load-user-field/";
const saveUrl = "/drought/save-user-field/";
const deleteUrl = "/drought/delete-user-field/";


class UserField {
  constructor(name, layer, id=null, userProjects=[]) {
    this.name = name;
    this.layer = layer;
    this.id = id;
    this.userProjects = userProjects;
  }
  hideLayer() {
    map.removeLayer(this.layer);
  }
  showLayer() {
    map.addLayer(this.layer);
  }
};


class DroughtProject {
  constructor(userFieldId) {
    this.userFieldId = userFieldId;
    this.monicaProject = null;
    this.soilProfile = 0;
    this.calculation = {};
    this.created = Date.now();
    this.updated = Date.now();
  }
}


// Save a newly created userField in DB
function saveUserField(name, geomJson) {
  return new Promise((resolve, reject) => {
    const requestData = {
      csrfmiddlewaretoken: csrfToken,
      geom: JSON.stringify(geomJson.geometry),
      name: name,
      // swnTool: userField.swnTool,
    };
    fetch(saveUrl, {
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
      // received data is the id of the saved userField
      resolve(data); 
    })
    .catch(error => {
      console.log(data)
      console.log('Error: ', error);
      reject(error); 
    });
  });
};

// Load all user fields from DB
const getData = async function () {
  fetch(loadUrl, {
    method: "GET",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "X-Requested-With": "XMLHttpRequest",
      // "X-CSRFToken": getCookie("csrftoken"),
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
        layer,
        el.id,
        el.user_projects    
      );
      // Add the layer to the droughtFeutureGroup layer group
        featureGroup.addLayer(userField.layer);
        userField.leafletId  = featureGroup.getLayerId(userField.layer);
        userFields[userField.leafletId ] = userField;

        addLayerToSidebar(userField);
        // console.log("getData, userFields: ", userFields);
    });
  });
};


// Modal Userfield Name 
const btnUserFieldSave = document.getElementById("btnUserFieldSave");
const btnUserFieldDismiss = document.getElementById("btnUserFieldDismiss");
const fieldNameInput = document.getElementById("fieldNameInput");


function dismissPolygon(layer, modalInstance) {
  modalInstance.hide();
  // temporary layer is removed from the map
  featureGroup.removeLayer(layer);
}

function updateFieldSelectorOption(userField) {
  const fieldSelector = document.getElementById("userFieldSelect");
  const option = document.createElement("option");
  option.value = userField.id;
  option.text = userField.name;
  fieldSelector.add(option);
}

// function connected to the "Save" and "SaveAndCalc" button in the modal
function handleSaveUserField(layer, bootstrapModal) {
  
  const fieldName = fieldNameInput.value;
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
            layerGeoJson,
            data.id,  
          );
          
          featureGroup.addLayer(userField.layer);
          // temporary layer is removed from the map
          featureGroup.removeLayer(layer);
          userField.leafletId  = featureGroup.getLayerId(userField.layer);
          userFields[userField.leafletId] = userField;
          addLayerToSidebar(userField);
          highlightLayer(userField.leafletId)
          updateFieldSelectorOption(userField);
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
}

function openUserFieldNameModal(layer) {
  // Set the modal content (e.g., name input)
  const modal = document.querySelector('#userFieldNameModal');
  // const nameInput = modal.querySelector('#fieldNameInput');
  // nameInput.value = ''; // Reset input

  const bootstrapModal = new bootstrap.Modal(modal);
  bootstrapModal.show();

  // Add event listeners for the save and dismiss actions
  modal.querySelector('#btnUserFieldSave').onclick = () => handleSaveUserField(layer, bootstrapModal);
  modal.querySelector('#btnUserFieldDismiss').onclick = () => dismissPolygon(layer, bootstrapModal);
  modal.querySelector('#btnUserFieldDismissTop').onclick = () => dismissPolygon(layer, bootstrapModal);
}

map.on("draw:created", function (event) {
  let layer = event.layer;
  // is added to the map only for display
  featureGroup.addLayer(layer);

  openUserFieldNameModal(layer);
});

// A list element is created and the corresponding userField object is attached to the li element in the sidebar
const addLayerToSidebar = (userField) => {
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
  // accordion.userField = userField;

  userFieldsAccordion.appendChild(accordion);
};


// Sidebar
// zoom to layer on dbclick in sidebar
accordionUserFields.addEventListener("dblclick", (e) => {
  const listElement = e.target.closest(".accordion-item");
  console.log("listElement", listElement);
  map.fitBounds(listElement.userField.layer.getBounds());
});


// Create a LayerGroup to hold the displayed polygons
var stateCountyDistrictLayer = L.layerGroup().addTo(map);

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

document.getElementById('monica-project-save').addEventListener('click', function () {

  saveProject();
});



function saveProject() {
  // var swnMonicaProject = JSON.parse(localStorage.getItem('project'));
  const project = MonicaProject.loadFromLocalStorage();
  // console.log('swnMonicaProject', swnMonicaProject);
  // try {
      project.updated = Date.now();
      // handleAlerts({'success': true, 'message': 'Project save trying'});

      fetch(saveProjectUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(project)
      })
        .then(response => response.json())
        .then(data => {
          console.log('data', data);
          handleAlerts(data.message);
        });
};

getData();
});