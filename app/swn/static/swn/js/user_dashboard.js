import { endpoint, chartDiv, crop, getChart } from "./chart_page.js";
import { btnSaveUserFieldDismiss, btnSaveUserFieldAndCalc } from "./modal_user_field_name.js";


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
var drawnItems = new L.FeatureGroup()
  .on("click", function (event) {
    console.log("click on drawnitems", event.layer._leaflet_id)
    let leafletID = event.layer._leaflet_id;
    if ($("#accordionHeader-"+leafletID).hasClass("highlight")) {
      deselectLayer(leafletID);
    } else {
      highlightLayer(leafletID);
    }
  })
  .on("dblclick", (event) => {
    console.log("dblclick on drawnitems");
    console.log("drawnitems on dbclick event", event.layer._leaflet_id);
    map.fitBounds(event.layer.getBounds());
  })
  .addTo(map);

  
// Draw functionality
var drawControl = new L.Control.Draw({
  position: "topright",
  draw: {
    circlemarker: false,
    polyline: false,
    polygon: {
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
  if (clickedElement.classList.contains("user-field-header")) {
    console.log("user-field-header clicked");
    const leafletID = clickedElement.getAttribute("leaflet-id");
    console.log("user-field-header clicked", leafletID);
    highlightLayer(leafletID);
    // the icons in the sidebar
  } else if (clickedElement.classList.contains("user-field-action")) {
    const leafletID = clickedElement.getAttribute("leaflet-id");
    console.log("user-field-action clicked", leafletID);
    const userField = userFields[leafletID];
    currentUserField = userField;
    if (clickedElement.classList.contains("delete")) {
      console.log("delete clicked", leafletID);
      let confirmDelete = confirm(`Are you sure to delete ` + userField.name + "?");
      if (confirmDelete) {
        delete userFields[userField.leafletID];
        userField.layer.remove(); // removes shape from map
        const listElement = document.getElementById("accordion-"+leafletID);
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
      console.log("field-menu clicked", leafletID);
    } else if (clickedElement.classList.contains("field-edit")) {
      // TODO the hardcoded modal is triggered from button
      console.log("field-edit clicked", leafletID);
      projectModalTitle.innerText = userField.name;
    } else { console.log("else in eventlistener") }
 
    }
  });


leafletSidebarContent.addEventListener("change", (event) => {
  const switchInput = event.target;
  console.log("leafletSidebarContent.addEventListener", switchInput)
  if (switchInput.classList.contains("basemap-switch")) {
    changeBasemap(switchInput);
  } else if (switchInput.classList.contains("layer-switch")) {
    console.log("Event listener contains layer-switch");
    const layerId = switchInput.getAttribute("data-layer");
    console.log("layerId", layerId)
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
    const leafletID = switchInput.getAttribute("leaflet-id");
    const userField = userFields[leafletID];
    if (switchInput.checked) {
      map.addLayer(userField.layer);
    } else {
      map.removeLayer(map._layers[leafletID]);
    }
  }
});


// Create a function to handle the basemap change
function changeBasemap(basemap) {
  console.log("basemap", basemap);
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
    // the leafletID gets reassigned when the layer is added to the drawnItems layerGroup
    this.leafletID = layer._leaflet_id;
    this.id = id;
    this.projects = [];
    console.log("UserField constructor leafletID: " + this.leafletID);
  }
  hideLayer() {
    map.removeLayer(this.layer);
  }
  showLayer() {
    map.addLayer(this.layer);
  }
}

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
    .then(
      response => response.json())
    .then(data => {
      // cleaar all userfieluserFields from map and sidebar
      $("#display-data").empty();
      console.log("getData response: ", data);
      const userFieldsDb = data.user_fields;
      userFieldsDb.forEach((el) => {
        var layer = L.geoJSON(el.geom_json);
     
        const userField = new UserField(
          el.name,
          // el.geom_json,
          layer,
          el.id
        );
        userField.layer.options.color = primaryColor;
        userField.layer.options.fillColor = primaryColor;
        // userField.layer.addTo(drawnItems); NEW
        drawnItems.addLayer(userField.layer);
        const leafletId = drawnItems.getLayerId(layer);
        userField.leafletId = leafletId;


        userFields[userField.leafletID] = userField;
        addLayerToSidebar(userField);
      });
    })
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
          console.log("handleSaveUserField userField: ", userField)
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
map.on(L.Draw.Event.CREATED, function (event) {
  if (isMapInteractionEnabled) {
    let layer = event.layer;
    layer.options.color = secondaryColor;
    layer.options.fillColor = secondaryColor;

    console.log(layer);
    layer.addTo(drawnItems);
    let userField = new UserField("", layer);
    console.log("UserField from draw created: ", userField);
    currentUserField = userField;
    // Open modal to enter field name
    console.log("DRAW EVENT CREATED userFields: ", userFields);
    $('#userFieldNameModal').modal('show');
  }
});

// A list element is created and the corresponding userField object is attached to the li element in the sidebar
const addLayerToSidebar = (userField) => {
  
  // new Accordion UserField style
  const accordion = document.createElement("div");
  accordion.setAttribute("class", "accordion-item");
  accordion.setAttribute("id", `accordion-${userField.leafletID}`);
  accordion.setAttribute("data-leaflet-id", userField.leafletID);

  accordion.innerHTML = ` 
    <div class="accordion-header nested user-field-header d-flex align-items-center justify-content-between" id="accordionHeader-${userField.leafletID}" leaflet-id="${userField.leafletID}">
    <span class="form-check form-switch h6">  
      <input type="checkbox" class="form-check-input user-field-switch" leaflet-id="${userField.leafletID}" id="fieldSwitch-${userField.leafletID}" checked>
    </span>
    <button class="accordion-button nested btn collapsed user-field-btn" type="button" id="accordionButton-${userField.leafletID}" data-bs-toggle="collapse" data-bs-target="#accordionField-${userField.leafletID}" aria-expanded="false" aria-controls="accordionField-${userField.leafletID}"> 
        ${userField.name}
        </button>
      <span class="column col-4 field-btns-col">
        <form id="deleteAndCalcForm-${userField.leafletID}">
          <button type="button" class="btn btn-outline-secondary btn-sm field-name user-field-action field-edit" leaflet-id="${userField.leafletID}" data-bs-toggle="modal" data-bs-target="#projectModal">
            <span><i class="fa-regular fa-pen-to-square user-field-action field-edit" leaflet-id="${userField.leafletID}"></i></span>
          </button>
    
          <button type="button" class="btn btn-outline-secondary btn-sm user-field-action field-menu" leaflet-id="${userField.leafletID}" data-bs-toggle="modal" data-bs-target="#fieldInfoModal">
            <span><i class="fa-solid fa-ellipsis-vertical user-field-action field-menu" leaflet-id="${userField.leafletID}"></i></span>
          </button>
          <button type="button" class="btn btn-outline-secondary btn-sm user-field-action delete" leaflet-id="${userField.leafletID}">
            <span><i class="fa-regular fa-trash-can user-field-action delete" leaflet-id="${userField.leafletID}"></i></span>
          </button>
        </form>
      </span>  
  </div>
  <div id="accordionField-${userField.leafletID}" class="accordion-collapse collapse" data-bs-parent="#accordion-${userField.leafletID}">
    <div class="accordion-body">
      <ul class="list-group" id="projectList-${userField.leafletID}">
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
  // weight: 2,
  // opacity: 1,
  
};



// highlight layer and li element on click in the sidebar
function highlightLayer(id) {
  console.log("highlightLayer")
  // reset all styles
  Object.keys(drawnItems._layers).forEach((key) => {
    try {
      //reset style for all layers
      drawnItems._layers[key].resetStyle();
    }
    catch(err) {
      console.log("reset style error ID ", key)
    }
    
    // $("#accordion-"+ key).removeClass("focus");
    $("#accordionHeader-"+ key).removeClass("highlight");
  });
  try {
    // set style for the selected layer
    drawnItems._layers[id].setStyle(highlight);
    console.log("highlighted layer ", map._layers[id])
    $("#accordionHeader-"+ id).addClass("highlight");
  } catch(err) {console.log("highlight error ID ", id)}
  // set style for the selected sidebar item
 
  
  // $("#accordion-"+ id).addClass("focus");
};

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

// interactions with sidebar via eventbubbling
// accordionUserFields.addEventListener("click", (e) => {
//   const listElement = e.target.closest(".accordion-item");
//   console.log("listElement", listElement);
//   const userField = listElement.userField;
//   currentUserField = userField;
//   if (e.target.classList.contains("delete")) {
    
//     let confirmDelete = confirm("Are you sure to delete");
//     if (confirmDelete) {
//       const id = listElement.userField.id;
//       delete userFields[userField.leafletID];
//       listElement.userField.layer.remove(); // removes shape from map
//       listElement.remove(); // removes HTML element from sidebar
//       // removes field from db
//       $.ajax({
//         type: "POST",
//         url: deleteUrl + id,
//         data: {
//           csrfmiddlewaretoken: csrfToken,
//         },
//         success: function (response) {
//           console.log("Delete Success");
//         },
//         error: function (response) {
//           console.log(error);
//         },
//       });
//     }
//   } else if (e.target.classList.contains("field-menu")) {
//     // TODO the hardcoded modal is triggered from button
//     console.log("field-menu clicked");
//   } else if (e.target.classList.contains("field-edit")) {
//     // TODO the hardcoded modal is triggered from button
//     console.log("field-edit clicked");
//     projectModalTitle.innerText = listElement.userField.name;
//     console.log("listElement.layer", listElement.userField.layer);
//     console.log("Area", L.GeometryUtil.geodesicArea(userField.layer.getLatLngs()))
//   } else {
//     // TODO the hardcoded modal is triggered from button

//     if (listElement.userField !== undefined) {
      
//       if (listElement.classList.contains("focus")) {
//         deselectLayer(listElement.userField.leafletID);
//       } else {
//         highlightLayer(listElement.userField.leafletID);
//       }
//       console.log("listElement.userfield", listElement.userField)
//     } else {
//       console.log("listlement undefined");
//     }
//   }
// });

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


// Sidebarstuff

getData();

