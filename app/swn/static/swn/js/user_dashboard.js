import { endpoint, chartDiv, crop, getChart } from "./chart_page.js";
import { btnSaveUserFieldDismiss, btnSaveUserFieldAndCalc } from "./modal_user_field_name.js";
let userFieldLayerCounter = 0;

/// helper functions
const typeOfLayer = (layer) => {
  if (layer instanceof L.Marker) {
    return "Marker";
  } else if (layer instanceof L.Circle) {
    return "Circle";
  // } else if (layer instanceof L.Polyline) {
  //   return "Polyline";
  } else if (layer instanceof L.Polygon) {
    return "Polygon";
    // Handle Polygon layer
  } else if (layer instanceof L.Rectangle) {
    return "Rectangle";
    // Handle Rectangle layer
  } else if (layer instanceof L.GeoJSON) {
    return "GeoJSON";
    // Handle GeoJSON layer
  } else {
    // Unknown layer type
    return "Unknown";
  }
}

const csrf = document.getElementsByName("csrfmiddlewaretoken");
// Fetch the CSRF token from the server
async function getCsrfToken() {
  const response = await fetch('get-csrf-token/');
  const data = await response.json();
  return data.csrfToken;
}

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
  //return csrfToken;
}



// alert bar at the top of the main container
// https://getbootstrap.com/docs/5.2/components/alerts/#examples
// types can be: primary, secondary, success, danger, warning, info, light, dark
const handleAlerts = (type, msg) => {
  alertBox.innerHTML = `
      <div class="alert alert-${type} alert-dismissible " role="alert">
          ${msg}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">
      </div>`;
  alertBox.classList.remove("d-none");
  setTimeout(() => {
    alertBox.classList.add("d-none");
  }, 2000);
};

// -----------User Field Name Modal -----------------

const projectModal = document.getElementById("projectModal");
const projectModalTitle = document.getElementById("projectModalTitle");
const chartCard = document.getElementById("chartCard");
const btnModalCal = document.getElementById("btnModalCal");

const alertBox = document.getElementById("alert-box");

const highlightColor = getComputedStyle(document.body).getPropertyValue('--bs-warning');
const primaryColor = getComputedStyle(document.body).getPropertyValue('--bs-primary');
const secondaryColor = getComputedStyle(document.body).getPropertyValue('--bs-secondary');
const successColor = getComputedStyle(document.body).getPropertyValue('--bs-success');
const infoColor = getComputedStyle(document.body).getPropertyValue('--bs-info');

var currentUserField;
var currentProject;


// -------------MAP --------------------------------------

// Boolean to inhibit map interactions for overlaying modals etc.
let isMapInteractionEnabled = true;

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
var videoUrl = 'https://www.mapbox.com/bites/00188/patricia_nasa.webm',
    videoBounds = droughtBounds;

const animation = L.videoOverlay(videoUrl, videoBounds, {opacity: 0.0});

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

// Spreewasser:N overlay, pilotRegion from data/pilotregion.js
const projectRegion = L.geoJSON(pilotRegion);

projectRegion.setStyle(function (feature) {
  return {
    fillColor: successColor,
    color: successColor,
  };
});
projectRegion.addTo(map);

// Leaflet Control top-right
// https://github.com/brunob/leaflet.fullscreen
const fullScreenControl = new L.Control.FullScreen({
  position: "topright",
});
map.addControl(fullScreenControl);

animation.addTo(map);

// added back-to-home bullseyer button to zoom controls
$(".leaflet-control-zoom").append(
  '<a class="leaflet-control-home" href="#" role="button" title="Project area" area-label="Project area"><i class="bi bi-bullseye"></i></a>'
);

// search for locations
const GeocoderControl = new L.Control.geocoder({
  position: "topright",
  marker: false,
});
map.addControl(GeocoderControl);

//add map scale
const mapScale = new L.control.scale({
  position: "bottomright",
}).addTo(map);


// handles clicks on a userField layer in the map
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

drawnItems.on("click", function (event) {
  console.log("drawnItems.on('click')", event.target);
  const layer = event.layer;
  const leafletId = drawnItems.getLayerId(layer);
  let leafletId2 = Object.keys(event.layer._eventParents)[0];
  highlightLayer(leafletId2);
  // console.log("Clicked leafletId", leafletId);
  // console.log("Clicked leafletId2", leafletId2);

  // console.log("event.target._layers.options", event.target._layers.options);
});

  
// Draw functionality
var drawControl = new L.Control.Draw({
  position: "topright",
  edit: {
    featureGroup: drawnItems
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
const chrosshair = document.getElementsByClassName("leaflet-control-home")[0];

chrosshair.addEventListener("click", () => {
  try {
    var bounds = drawnItems.getBounds();
    map.fitBounds(bounds);
  } catch {
    return;
  }
});


const sidebarLeft = L.control
  .sidebar("sidebar", {
    autopan: true,
    container: 'sidebar',
    closeButton: true,
    position: "left",
  })
  .addTo(map);

//-------------------- Baselayers ------------------------------
const leafletSidebarContent = document.querySelector(".leaflet-sidebar-content");
const droughtBaseLayerCollapse = document.getElementById("droughtBaseLayerCollapse");
const toolboxBaseLayerCollapse = document.getElementById("toolboxBaseLayerCollapse");

const baseLayerCollapses = [droughtBaseLayerCollapse, toolboxBaseLayerCollapse];

const overlayLayers = {
  "droughtOverlay": droughtOverlay,
  "demOverlay": demOverlay,
  "animation": animation,
  "projectRegion": projectRegion,
};

// ------------------- Sidebar eventlisteners -------------------
leafletSidebarContent.addEventListener("click", (event) => {
  const clickedElement = event.target;
  console.log("leafletSidebarContent.addEventListener", clickedElement)
  if (clickedElement.classList.contains("user-field-header") || clickedElement.classList.contains("user-field-btn")) {
    const leafletId = clickedElement.getAttribute("leaflet-id");
    console.log("user-field-header clicked", leafletId);
   
    highlightLayer(leafletId);
    
    
    // the icons in the sidebar
  } else if (clickedElement.classList.contains("user-field-action")) {
    const leafletId = clickedElement.getAttribute("leaflet-id");
    console.log("user-field-action clicked", leafletId);
    const userField = userFields[leafletId];
    currentUserField = userField;
    if (clickedElement.classList.contains("delete")) {
      console.log("delete clicked", leafletId);
      let confirmDelete = confirm(`Are you sure to delete ` + userField.name + "?");
      if (confirmDelete) {
        delete userFields[userField.leafletId];
        userField.layer.remove(); // removes shape from map
        const listElement = document.getElementById("accordion-"+leafletId);
        listElement.remove(); // removes HTML element from sidebar
        // removes field from db
        $.ajax({
          type: "POST",
          url: deleteUrl + userField.id,
          data: {
            csrfmiddlewaretoken: csrfToken,
          },
          success: function (response) {
            console.log("Delete Success");
          },
          error: function (response) {
            console.log(error);
          },
        });
      }
    } else if (clickedElement.classList.contains("field-menu")) {
      // TODO the hardcoded modal is triggered from button
      console.log("field-menu clicked", leafletId);
    } else if (clickedElement.classList.contains("field-edit")) {
      // TODO the hardcoded modal is triggered from button
      console.log("field-edit clicked", leafletId);
      projectModalTitle.innerText = userField.name;
    } else { console.log("else in eventlistener") }
 
    }
  });


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
      opacitySlider.disabled = false;
    } else {
      overlay.remove();
      opacitySlider.disabled = true;
    }
  } else if (switchInput.classList.contains("user-field-switch")) {
    const leafletId = switchInput.getAttribute("leaflet-id");
    const userField = userFields[leafletId];
    if (switchInput.checked) {
      map.addLayer(userField.layer);
    } else {
      map.removeLayer(map._layers[leafletId]);
    }
  }
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

  // synchronizes all other switches for the same basemap
  const switches = document.querySelectorAll(`input[data-basemap="${selectedBasemap}"]`);
  switches.forEach((switchInput) => {
    switchInput.checked = basemap.checked;
  });
}
}

let switchGroupId = 1; 

baseLayerCollapses.forEach(element => {
  let initialBasemapChecked = false; 
  const baseLayerControlList = document.createElement("ul");
  baseLayerControlList.classList.add("list-group", "sidebar-list", "base-layer-control-list");
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
  element.appendChild(baseLayerControlList);
  switchGroupId++;

  if (!initialBasemapChecked) {
    const initialBasemapSwitches = baseLayerControlList.querySelectorAll(".basemap-switch");
    initialBasemapSwitches[0].checked = true;
    changeBasemap(initialBasemapSwitches[0]);
    initialBasemapChecked = true;
  }

});

const initialBasemap = baseLayerControlList.querySelectorAll(".basemap-switch");
initialBasemap.checked = true;
changeBasemap(initialBasemap);

//-------------------- Baselayers end ------------------------------


//---------------MAP END-------------------------------
var userFields = {};
const accordionUserFields = document.getElementById("accordionUserFields");



// User Field Name Modal
const userFieldNameModalElement = document.getElementById("userFieldNameModal");
const btnUserFieldSave = document.getElementById("btnUserFieldSave");
const btnUserFieldSaveAndCalc = document.getElementById("btnUserFieldSaveAndCalc");
const btnUserFieldDismiss = document.getElementById("btnUserFieldDismiss");
const fieldNameInput = document.getElementById("fieldNameInput");

const loadUrl = "load/";
const saveUrl = "save/";
const deleteUrl = "delete/";

class UserField {
  constructor(name, layer, id = null) {

    this.name = name;
    this.layer = layer;
    this.id = id;
    this.projects = [];

  }
  hideLayer() {
    map.removeLayer(this.layer);
  }
  showLayer() {
    map.addLayer(this.layer);
  }
};


class UserProject {
  constructor(userField, cropID) {
    this.userField = userField;
    this.cropID = cropID;
    this.calculation = {};
    this.timestamp = Date.now();
  }
}

// Save a newly created userField in DB
function saveUserField(userField) {
  console.log("saveUserField");
  return new Promise((resolve, reject) => {
    const requestData = {
      csrfmiddlewaretoken: csrfToken,
      geom: JSON.stringify(userField.layer.toGeoJSON().geometry),
      name: userField.name,
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
      resolve(data.id); 
    })
    .catch(error => {
      console.log('Error: ', error);
      reject(error); // Reject the promise in case of an error
    });
  });
}

// Load all user fields from DB
const getData = async function () {
  console.log("getData executed")
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
      console.log("getData response: ", data);
      const userFieldsDb = data.user_fields;
      userFieldsDb.forEach((el) => {
        var layer = L.geoJSON(el.geom_json);
        console.log("drawnItems before: ", drawnItems);

        const userField = new UserField(
          el.name,
          layer,
          el.id
        );

        userField.layer.options.color = primaryColor;
        userField.layer.options.fillColor = primaryColor;

        // Add the layer to the drawnItems layer group
        drawnItems.addLayer(userField.layer);
        console.log("drawnItems after: ", drawnItems);
        // Store the userField object using the layer's leafletId
        const leafletId = drawnItems.getLayerId(userField.layer);
        console.log("GetData layer: ", Object.keys(userField.layer._layers)[0]);
        userField.leafletId = leafletId;
        userFields[userField.leafletId] = userField;

        addLayerToSidebar(userField);
      });

      console.log("userFields from getData: ", userFields);
    });
};



// function connected to the "Save" and "SaveAndCalc" button in the modal
function handleSaveUserField() {
  const userField = currentUserField; 
  
  console.log("handleSaveUserField", typeof userField, userField);
  const fieldName = fieldNameInput.value;
  if (fieldName !== "") {
    if (Object.values(userFields).some((proj) => proj.name === fieldName)) {
      alert(`Please change the name since "${fieldName}" already exists.`);
    } else {
      userField.name = fieldName;
      saveUserField(userField)
        .then((id) => {
          userField.id = id;

          userFields[userField.leafletId] = userField;
          addLayerToSidebar(userField);
        })
        .catch((error) => {
          console.log("Error: ", error);
        });
      // hide modal
      $('#userFieldNameModal').modal('hide');
      // reset name input field
      fieldNameInput.value = '';
    }
  } else {
    alert("This field cannot be empty. Please enter a name!");
  }
}

// Modal Userfield Name 
btnUserFieldSave.addEventListener("click", (event) => {
  event.preventDefault();
  handleSaveUserField();
});

btnUserFieldSaveAndCalc.addEventListener("click", (event) => {
  event.preventDefault();
  handleSaveUserField();
  // Additional actions after saving and calculating
  console.log("Save and calculation complete. Additional actions here.");
});

btnUserFieldDismiss.addEventListener("click", (event) => {
  const userField = currentUserField;
  drawnItems.removeLayer(userField.layer);
  currentUserField = null;
});

// EventListener for the draw event 
map.on("draw:created", function (event) {
  if (isMapInteractionEnabled) {
    let layer = event.layer;

    const layer2 = L.geoJSON(layer.toGeoJSON().geometry);
    // console.log("Draw event layer2._layers._leaflet_id: ", Object.keys(layer2._layers)[0]);
    drawnItems.addLayer(layer2);
    let userField = new UserField("", layer);
    userField.leafletId = layer2._leaflet_id
    layer.on("click", function (event) {
      console.log("Layer click event: ", event.target);
      highlightLayer(event.target._leaflet_id);
      // Handle the click event on the layer
    });


    
    currentUserField = userField;
    console.log("Draw created event: ", event);

    $('#userFieldNameModal').modal('show');
  }
});

// A list element is created and the corresponding userField object is attached to the li element in the sidebar
const addLayerToSidebar = (userField) => {
  
  // new Accordion UserField style
  const accordion = document.createElement("div");
  accordion.setAttribute("class", "accordion-item");
  accordion.setAttribute("id", `accordion-${userField.leafletId}`);
  accordion.setAttribute("leaflet-id", userField.leafletId);

  accordion.innerHTML = ` 
    <div class="accordion-header nested user-field-header d-flex align-items-center justify-content-between" id="accordionHeader-${userField.leafletId}" leaflet-id="${userField.leafletId}">
    <span class="form-check form-switch h6">  
      <input type="checkbox" class="form-check-input user-field-switch" leaflet-id="${userField.leafletId}" id="fieldSwitch-${userField.leafletId}" checked>
    </span>
    <button class="accordion-button nested btn collapsed user-field-btn" type="button" leaflet-id="${userField.leafletId}" id="accordionButton-${userField.leafletId}" data-bs-toggle="collapse" data-bs-target="#accordionField-${userField.leafletId}" aria-expanded="false" aria-controls="accordionField-${userField.leafletId}"> 
        ${userField.name}
        </button>
      <span class="column col-4 field-btns-col">
        <form id="deleteAndCalcForm-${userField.leafletId}">
          <button type="button" class="btn btn-outline-secondary btn-sm field-name user-field-action field-edit" leaflet-id="${userField.leafletId}" data-bs-toggle="modal" data-bs-target="#projectModal">
            <span><i class="fa-regular fa-pen-to-square user-field-action field-edit" leaflet-id="${userField.leafletId}"></i></span>
          </button>
    
          <button type="button" class="btn btn-outline-secondary btn-sm user-field-action field-menu" leaflet-id="${userField.leafletId}" data-bs-toggle="modal" data-bs-target="#fieldInfoModal">
            <span><i class="fa-solid fa-ellipsis-vertical user-field-action field-menu" leaflet-id="${userField.leafletId}"></i></span>
          </button>
          <button type="button" class="btn btn-outline-secondary btn-sm user-field-action delete" leaflet-id="${userField.leafletId}">
            <span><i class="fa-regular fa-trash-can user-field-action delete" leaflet-id="${userField.leafletId}"></i></span>
          </button>
        </form>
      </span>  
  </div>
  <div id="accordionField-${userField.leafletId}" class="accordion-collapse collapse" data-bs-parent="#accordion-${userField.leafletId}">
    <div class="accordion-body">
      <ul class="list-group" id="projectList-${userField.leafletId}">
        <li>some item 1</li>
        <li>some item 2</li>
      <ul>
    </div>
  </div>
`;

  // adding the UserField to the HTML-list element
  accordion.userField = userField;

  accordionUserFields.appendChild(accordion);
  };

var highlight = {
  color: highlightColor,
};



// highlight layer and li element on click in the sidebar
function highlightLayer(id) {
  console.log("highlightLayer")
  if ($(`#accordionHeader-${id}`).hasClass("highlight")) {
    
    deselectLayer(id);
  } else { 
  // reset all styles
  drawnItems.eachLayer(function(layer) {
    layer.resetStyle();
    console.log("highlight layer", layer._leaflet_id);
    $("#accordionHeader-"+ layer._leaflet_id).removeClass("highlight");
  });
  try {
    // set style for the selected layer
    drawnItems._layers[id].setStyle(highlight);
    $("#accordionHeader-"+ id).addClass("highlight");
  } catch(err) {console.log("highlight error ID ", id)}
}}

function deselectLayer(id) {
  console.log("deselectLayer");
  $("#accordionHeader-" + id).removeClass("highlight");
  map._layers[id].resetStyle();
}

// Sidebar
// zoom to layer on dbclick in sidebar
accordionUserFields.addEventListener("dblclick", (e) => {
  const listElement = e.target.closest("div");
  console.log("listElement", listElement);
  map.fitBounds(listElement.userField.layer.getBounds());
});

const monicaFieldCalculation = () => {
  console.log("monicaFieldCalculation");
};

btnModalCal.addEventListener("click", function () {
  getChart();
  chartCard.classList.remove("d-none");
});

$("#projectModal").on("hide.bs.modal", function (e) {
  if (!chartCard.classList.contains("d-none")) {
    chartCard.classList.add("d-none");
  }
});

$(document).ready(function () {
  $("#chartModal").on("show.bs.modal", function () {
    var chartModal = $("#chartModal");

    $(".modal-container").html(this);
    $("#map-container").hide();
  }),
    $("#chartModal").on("hide.bs.modal", function () {
      $("#map-container").show();
    });
});


getData();

