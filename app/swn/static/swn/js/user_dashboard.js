import { endpoint, chartDiv, crop, getChart } from "./chart_page.js";
import { btnSaveUserFieldDismiss, btnSaveUserFieldAndCalc } from "./modal_user_field_name.js";

document.addEventListener("DOMContentLoaded", () => {

  /// helper functions
  const typeOfLayer = (layer) => {
    if (layer instanceof L.Marker) {
      return "Marker";
    } else if (layer instanceof L.Circle) {
      return "Circle";
    } else if (layer instanceof L.Polyline) {
      return "Polyline";
    } else if (layer instanceof L.Polygon) {
      return "Polygon";
    } else if (layer instanceof L.Rectangle) {
      return "Rectangle";
    } else if (layer instanceof L.GeoJSON) {
      return "GeoJSON";
    } else {
      return "Unknown";
    }
  };

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
    return csrfToken;
  };


// -----------User Field Name Modal -----------------

const projectModal = document.getElementById("projectModal");
const projectModalTitle = document.getElementById("projectModalTitle");
const chartCard = document.getElementById("chartCard");


const highlightColor = getComputedStyle(document.body).getPropertyValue('--bs-warning');
const primaryColor = getComputedStyle(document.body).getPropertyValue('--bs-primary');
const secondaryColor = getComputedStyle(document.body).getPropertyValue('--bs-secondary');
const successColor = getComputedStyle(document.body).getPropertyValue('--bs-success');
const infoColor = getComputedStyle(document.body).getPropertyValue('--bs-info');
const lightColor = getComputedStyle(document.body).getPropertyValue('--bs-light');

var currentUserField;
var currentProject;

// ------------------- Alert Box -------------------
// alert bar at the top of the main container
// https://getbootstrap.com/docs/5.2/components/alerts/#examples
// types can be: primary, secondary, success, danger, warning, info, light, dark

const alertBox = document.getElementById("alert-box");

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
var droughtFeatureGroup = new L.FeatureGroup();
var toolboxFeatureGroup = new L.FeatureGroup();
// the default app is drought.
var currentFeatureGroup = droughtFeatureGroup;

map.addLayer(currentFeatureGroup);
var projectRegion = new L.GeoJSON.AJAX('load_projectregion/',
  {
    style: function (feature) {
      return { 
        fillColor: lightColor,
        color: infoColor,};
    },
    attribution: 'Project Region',
    onEachFeature: function (feature, layer) {
      layer.bindTooltip(feature.properties.name);
    }
  });

  currentFeatureGroup.bringToFront();

droughtFeatureGroup.on("click", function (event) {
  const layer = event.layer;
  
  // const leafletId = droughtFeutureGroup.getLayerId(layer);
  let leafletId = Object.keys(event.layer._eventParents)[0];
  
  highlightLayer(leafletId);
  console.log("droughtFeutureGroup click event: highlight ", leafletId, event.layer);
  // highlightPolygon(event.layer)
});

toolboxFeatureGroup.on("click", function (event) {
  const layer = event.layer;
  
  // const leafletId = toolboxFeutureGroup.getLayerId(layer);
  let leafletId = Object.keys(event.layer._eventParents)[0];
  
  highlightLayer(leafletId);
  console.log("toolboxFeutureGroup click event: highlight ", leafletId, event.layer);
  // highlightPolygon(event.layer)
});

// highlight layer and li element on click in the sidebar

function highlightLayer(id) {
  // remove highlight from all layers
  currentFeatureGroup.eachLayer(function (layer) {
    const key = Object.keys(layer._layers)[0];
    const value = layer._layers[key];
    value._path.classList.remove("highlight");
  });
  // deselect layer/ header: remove highlight class from  header
  if ($(`#accordionHeader-${id}`).hasClass("highlight")) {
    $(`#accordionHeader-${id}`).removeClass("highlight");
    console.log("highlightLayer has class highlight");
    
    let key = Object.keys(currentFeatureGroup._layers[id]._layers)[0]
    console.log("Key: ", key, "id: ", id)
     currentFeatureGroup._layers[id]._layers[key]._path.classList.remove('highlight');
  } else { // select layer/ header: 
    
    console.log("highlightLayer does not have class highlight")
    switch (swnTool) {
      case 'drought': {
        const accordionDroughtHeaders = document.querySelectorAll('#accordionDroughtFields .accordion-header');
        accordionDroughtHeaders.forEach(header => {
          header.classList.remove('highlight')
        });
      };
      case 'toolbox': {
        const accordionToolboxHeaders = document.querySelectorAll('#accordionToolboxFields .accordion-header');
        accordionToolboxHeaders.forEach(header => {
          header.classList.remove('highlight')
        });
        };
      };
      //add highlight class to header
    $(`#accordionHeader-${id}`).addClass("highlight")
    console.log('currentFeatureGroup', currentFeatureGroup)
    // add highlight class to leaflet layer
    let key = Object.keys(currentFeatureGroup._layers[id]._layers)[0]
    currentFeatureGroup._layers[id]._layers[key]._path.classList.add('highlight');
  };
  };
      
  
// Draw functionality
var drawControl = new L.Control.Draw({
  position: "topright",
  edit: {
    featureGroup: currentFeatureGroup,
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
    var bounds = currentFeatureGroup.getBounds();
    map.fitBounds(bounds);
  } catch {
    return;
  }
});

//--------------------SIDEBAR---------------------------------



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

// const toolboxBaseLayerCollapse = document.getElementById("toolboxBaseLayerCollapse");
const baseLayerCollapse = document.getElementById("baseLayerCollapse")
const baseLayerCollapses = [baseLayerCollapse];

const overlayLayers = {
  "droughtOverlay": droughtOverlay,
  "demOverlay": demOverlay,
  "animation": animation,
  "projectRegion": projectRegion,
};

// ------------------- Field Menu Modal -------------------
function populateFieldMenuModalWithData(data) {
  // Assuming you have elements with IDs in your modal to display the data
  document.getElementById("fieldMenuModalTitle").innerText = data.text;
};


// ------------------- Sidebar eventlisteners -------------------

// -------------------Sidebar new----------------
const sidebarTabToolbox = document.getElementById("sidebarTabToolbox");
const sidebarTabDrought = document.getElementById("sidebarTabDrought");

// switch between SWN Toolbox and drought warning
const listElementDem = document.getElementById("liElementDem")
const listElementDroughtIndex = document.getElementById("liElementDroughtIndex")
const listElementNetCDF = document.getElementById("liElementNetCDF")

const accordionDroughtFields = document.getElementById("accordionDroughtFields")
const accordionToolboxFields = document.getElementById("accordionToolboxFields")
const sidebarToolsHeader = document.getElementById("sidebarToolsHeader");
let swnTool = 'drought'

function changeTab(swnTool) {
  console.log('changeTabFunction', swnTool)
  switch (swnTool) {
    case 'drought':
      sidebarToolsHeader.innerText = "Dürreberechnung";
      listElementDem.classList.remove("d-none");
      listElementDroughtIndex.classList.remove("d-none");
      listElementNetCDF.classList.remove("d-none");
      accordionDroughtFields.classList.remove("d-none");
      accordionToolboxFields.classList.add("d-none");

      console.log("Case drought", sidebarToolsHeader.innerText );
      toolboxFeatureGroup.remove();
      droughtFeatureGroup.addTo(map);
      currentFeatureGroup = droughtFeatureGroup;

      break;
    case 'toolbox':
      sidebarToolsHeader.innerText = "Toolbox";
      listElementDem.classList.add("d-none");
      listElementDroughtIndex.classList.add("d-none");
      listElementNetCDF.classList.add("d-none");
      accordionDroughtFields.classList.add("d-none");
      accordionToolboxFields.classList.remove("d-none");

      droughtFeatureGroup.remove();
      toolboxFeatureGroup.addTo(map);
      currentFeatureGroup = toolboxFeatureGroup;
      
      console.log("Case toolbox")
      break;
  }
  console.log("CurrentFeatureGroup", currentFeatureGroup)
};

// Click of drought and toolbox icon of the sidebar
const sidebarTabListDrought = document.getElementById("sidebarTabListDrought");
const sidebarTabListToolbox = document.getElementById("sidebarTabListToolbox");

sidebarTabDrought.addEventListener("click", () => {
  sidebarTabListToolbox.classList.remove("active");
  if (sidebarTabListDrought.classList.contains('active')) {
    console.log('Drought contains active')
    if (swnTool === 'toolbox') {
      swnTool = 'drought'
      changeTab( swnTool);
    }    
  } 
});

sidebarTabToolbox.addEventListener("click", () => {
  sidebarTabListDrought.classList.remove("active");
  if (sidebarTabListToolbox.classList.contains('active')) {
    console.log('Toolbox contains active')
    // sidebarToolsHeader.innerText = "Toolbox";
    if (swnTool === 'drought') {
      swnTool = 'toolbox'
      changeTab(swnTool);
    }
  }
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
    currentUserField = userField;
    if (clickedElement.classList.contains("delete")) {
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
      // TODO the hardcoded # fieldMenuModal is triggered from button
        const fieldMenuModal = new bootstrap.Modal(document.getElementById('fieldMenuModal'));
          fieldMenuModal.show();
      // $('#fieldMenuModal').modal('show');
      // console.log("field-menu clicked", leafletId);
    } else if (clickedElement.classList.contains("field-edit")) {
        // TODO the hardcoded modal is triggered from button
        console.log("field-edit clicked", leafletId, userField.id);
        // projectModalTitle.innerText = userField.name;
        const url = `/login/Dashboard/field-menu/${userField.id}/`;
        // window.location.href = url;
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
// const accordionDroughtFields = document.getElementById("accordionDroughtFields");
// const accordionToolboxFields = document.getElementById("accordionToolboxFields");



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
  constructor(name, layer, swnTool, id=null) {
    this.name = name;
    this.layer = layer;
    this.swnTool = swnTool;
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


class droughtProject {
  constructor(userField, cropID) {
    this.userField = userField;
    this.cropID = cropID;
    this.soilProfile = 0;
    this.calculation = {};
    this.timestamp = Date.now();
  }
}

// Save a newly created userField in DB
function saveUserField(userField) {
  return new Promise((resolve, reject) => {
    const requestData = {
      csrfmiddlewaretoken: csrfToken,
      geom: JSON.stringify(userField.layer.toGeoJSON().geometry),
      name: userField.name,
      swnTool: userField.swnTool,
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
        console.log("detData, element: ", el);
        const userField = new UserField(
          el.name,
          layer,
          el.swn_tool,
          el.id         
        );
        const leafletId = 0;
        // Add the layer to the droughtFeutureGroup layer group
        switch (el.swn_tool) {
          case 'drought': {
            droughtFeatureGroup.addLayer(userField.layer);
            userField.leafletId  = droughtFeatureGroup.getLayerId(userField.layer);
            break;
          }
          case 'toolbox': {
            toolboxFeatureGroup.addLayer(userField.layer);
            userField.leafletId  = toolboxFeatureGroup.getLayerId(userField.layer);
          }
        };
        // Store the userField object using the layer's leafletId
        
        // userField.leafletId = leafletId;
        userFields[userField.leafletId ] = userField;

        addLayerToSidebar(userField);
    });
})};


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
          highlightLayer(userField.leafletId)
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
  droughtFeatureGroup.removeLayer(userField.layer);
  currentUserField = null;
});

// EventListener for the draw event 
map.on("draw:created", function (event) {
  if (isMapInteractionEnabled) {
    let layer = event.layer;
    const layer2 = L.geoJSON(layer.toGeoJSON().geometry);
    currentFeatureGroup.addLayer(layer2);

        
      let userField = new UserField("", layer, swnTool);
      console.log("draw:created userField", userField);
      userField.leafletId = layer2._leaflet_id;
      currentUserField = userField;

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
          <a href="field-menu/${userField.id}" type="button" class="btn btn-outline-secondary btn-sm field-name user-field-action field-edit" leaflet-id="${userField.leafletId}">
            <span><i class="bi bi-pencil-square user-field-action field-edit" leaflet-id="${userField.leafletId}"></i></span>
          </a>
    
          <button type="button" class="btn btn-outline-secondary btn-sm user-field-action field-menu" leaflet-id="${userField.leafletId}">
            <span><i class="bi bi-list user-field-action field-menu" leaflet-id="${userField.leafletId}"></i></span>
          </button>
          <button type="button" class="btn btn-outline-secondary btn-sm user-field-action delete" leaflet-id="${userField.leafletId}">
            <span><i class="bi bi-trash user-field-action delete" leaflet-id="${userField.leafletId}"></i></span>
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

  if (userField.swnTool === 'drought') {
    console.log('AddLayerToSidebar drought')
    accordionDroughtFields.appendChild(accordion);
  } else if (userField.swnTool === 'toolbox') {
    console.log('AddLayerToSidebar toolbox')
    accordionToolboxFields.appendChild(accordion);
  } else { console.log('else in addLayerToSidebar') };
};

var highlight = {
  color: successColor,
};



// Sidebar
// zoom to layer on dbclick in sidebar
accordionDroughtFields.addEventListener("dblclick", (e) => {
  const listElement = e.target.closest("div");
  console.log("listElement", listElement);
  map.fitBounds(listElement.userField.layer.getBounds());
});

const monicaFieldCalculation = () => {
  console.log("monicaFieldCalculation");
};



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

// state county district selection

// Create a LayerGroup to hold the displayed polygons
var stateCountyDistrictLayer = L.layerGroup().addTo(map);

// Handle dropdown menu change event
// Multiple Select from https://www.cssscript.com/select-box-virtual-scroll/
VirtualSelect.init({ 
  ele: '#stateSelect',
  placeholder: 'Bundessland',
  required: false,
});

VirtualSelect.init({ 
  ele: '#districtSelect',
  placeholder: 'Regierungsbezirk',
  required: false,
});
VirtualSelect.init({ 
  ele: '#countySelect',
  placeholder: 'Landkreis',
  required: false,
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
    console.log("event fired", selectedAdminAreas);

    for (let key in selectedAdminAreas) {
      if (selectedAdminAreas[key].length > 0) {
        selectedAdminAreas[key].forEach(function (polygon) {
          var url = '/login/Dashboard/load_polygon/' + key + '/' + polygon + '/';
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
            style: function (feature) {
                return { color: color };
            },
            onEachFeature: function (feature, layer) {
                layer.bindTooltip(feature.properties.nuts_name);
            }
        });
        console.log("geojsonLayer", geojsonLayer)
        geojsonLayer.addTo(stateCountyDistrictLayer);
        });
      }
  };
});
});

getData();

});