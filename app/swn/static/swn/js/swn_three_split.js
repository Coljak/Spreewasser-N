document.addEventListener("DOMContentLoaded", () => {


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

  // longitude and latitude of the project region;
  // $('#coordinateFormCard').hide();

  $('#userFieldSelect').on('change', function () {
    // get centroid of the userfield
    console.log('userFieldSelect change event');
    var userField = $(this).val();
    localStorage.setItem('project.userField', userField);

    if (userField != null) {
        fetch('/login/Dashboard/get_lat_lon/' + userField + '/')
      .then((response) => response.json())
      .then((data) => {
        console.log('data', data);
        $('#id_latitude').val(data.lat);
        $('#id_longitude').val(data.lon);
      });
    }
  });
  
  $('#userFieldSelect').trigger('change');

  function modifyStorageProject(key, value) {
    var project = JSON.parse(localStorage.getItem('project'));
    project[key] = value;
    localStorage.setItem('project', JSON.stringify(project));
  };




// -----------User Field Name Modal -----------------


// bootstrap colors
const highlightColor = getComputedStyle(document.body).getPropertyValue('--bs-warning');
const primaryColor = getComputedStyle(document.body).getPropertyValue('--bs-primary');
const secondaryColor = getComputedStyle(document.body).getPropertyValue('--bs-secondary');
const successColor = getComputedStyle(document.body).getPropertyValue('--bs-success');
const infoColor = getComputedStyle(document.body).getPropertyValue('--bs-info');
const lightColor = getComputedStyle(document.body).getPropertyValue('--bs-light');

var currentUserField;


// ------------------- Alert Box -------------------
// alert bar at the top of the main container
// https://getbootstrap.com/docs/5.2/components/alerts/#examples
// types can be: primary, secondary, success, danger, warning, info, light, dark



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
  console.log("HIGHLIGHT");
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
const baseLayerCollapses = [baseLayerCollapse];

const overlayLayers = {
  "droughtOverlay": droughtOverlay,
  "demOverlay": demOverlay,
  "projectRegion": projectRegion,

};




// ------------------- Sidebar eventlisteners -------------------

// -------------------Sidebar new----------------


// switch between SWN Toolbox and drought warning
const listElementDem = document.getElementById("liElementDem")
const listElementDroughtIndex = document.getElementById("liElementDroughtIndex")
const listElementNetCDF = document.getElementById("liElementNetCDF")
const droughtSidebarLiElements = document.querySelectorAll(".drought-overlay-sidebar-item")


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

    currentUserField = userField;

    if (clickedElement.classList.contains("delete")) {
      let confirmDelete = confirm(`Are you sure to delete ` + userField.name + "?");
      if (confirmDelete) {
        delete userFields[userField.leafletId];
        userField.layer.remove(); // removes shape from map
        const listElement = document.getElementById("accordion-"+leafletId);
        listElement.remove(); // removes HTML element from sidebar
        // removes field from db
        console.log("delete UserField ", userField)
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
        $('#monicaProjectModal form')
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


const loadUrl = "/login/Dashboard/load/";
const saveUrl = "/login/Dashboard/save/";
const deleteUrl = "/login/Dashboard/delete/";


class UserField {
  constructor(name, layer, id=null) {
    this.name = name;
    this.layer = layer;
    this.id = id;
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
function saveUserField(userField) {
  return new Promise((resolve, reject) => {
    const requestData = {
      csrfmiddlewaretoken: csrfToken,
      geom: JSON.stringify(userField.layer.toGeoJSON().geometry),
      name: userField.name,
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
      console.log("getData, element: ", el);
      const userField = new UserField(
        el.name,
        layer,
        // el.swn_tool,
        el.id         
      );
      // Add the layer to the droughtFeutureGroup layer group

        featureGroup.addLayer(userField.layer);
        userField.leafletId  = featureGroup.getLayerId(userField.layer);
        userFields[userField.leafletId ] = userField;

        addLayerToSidebar(userField);
        console.log("getData, userFields: ", userFields);
      
      // Store the userField object using the layer's leafletId
      
      // userField.leafletId = leafletId;

    });
  });
};

// function getData = async function(userFields) {

//   console.log("getData", userFields)
//     // clear all userFields from map and sidebar
//     $("#display-data").empty();
//     // const userFieldsDb = data.user_fields;
//     userFields.forEach((el) => {
//       var layer = L.geoJSON(el.geom_json);
//       layer.bindTooltip(el.name);
//       console.log("getData, element: ", el);
//       const userField = new UserField(
//         el.name,
//         layer,
//         // el.swn_tool,
//         el.id         
//       );
//       // Add the layer to the droughtFeutureGroup layer group

//         featureGroup.addLayer(userField.layer);
//         userField.leafletId  = featureGroup.getLayerId(userField.layer);
//         userFields[userField.leafletId ] = userField;

//         addLayerToSidebar(userField);
        
      
//       // Store the userField object using the layer's leafletId
      
//       // userField.leafletId = leafletId;

//     });

// };


// Modal Userfield Name 
const btnUserFieldSave = document.getElementById("btnUserFieldSave");
const btnUserFieldDismiss = document.getElementById("btnUserFieldDismiss");
const fieldNameInput = document.getElementById("fieldNameInput");

btnUserFieldSave.addEventListener("click", (event) => {
  event.preventDefault();
  handleSaveUserField();
});


btnUserFieldDismiss.addEventListener("click", (event) => {
  const userField = currentUserField;
  featureGroup.removeLayer(userField.layer);
  currentUserField = null;
});

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



// EventListener for the draw event 
map.on("draw:created", function (event) {

  let layer = event.layer;
  const layer2 = L.geoJSON(layer.toGeoJSON().geometry);
  featureGroup.addLayer(layer2);

  let userField = new UserField("", layer);
  console.log("draw:created userField", userField);
  userField.leafletId = layer2._leaflet_id;
  currentUserField = userField;
  // Show the modal to enter the userField name. After the name is entered, the userField is saved in the DB
  $('#userFieldNameModal').modal('show'); 
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
 

  accordion.innerHTML = ` 
    <div 
    class="accordion-header nested user-field-header d-flex align-items-center justify-content-between" 
    id="accordionHeader-${userField.leafletId}" 
    leaflet-id="${userField.leafletId}"
    >
    <span class="form-check form-switch h6">  
      <input type="checkbox" class="form-check-input user-field-switch" leaflet-id="${userField.leafletId}" "user-field-id"=${userField.id}  id="fieldSwitch-${userField.leafletId}" checked>
    </span>
    <button class="accordion-button nested btn collapsed user-field-btn" type="button" leaflet-id="${userField.leafletId}" "user-field-id"=${userField.id} id="accordionButton-${userField.leafletId}" data-bs-toggle="collapse" data-bs-target="#accordionField-${userField.leafletId}" aria-expanded="false" aria-controls="accordionField-${userField.leafletId}"> 
        ${userField.name}
        </button>
      <span class="column col-4 field-btns-col">
        <form id="deleteAndCalcForm-${userField.leafletId}">
          <button type="button" class="btn btn-outline-secondary btn-sm field-name user-field-action field-edit" leaflet-id="${userField.leafletId}" "user-field-id"=${userField.id}>
            <span><i class="bi bi-pencil-square user-field-action field-edit" leaflet-id="${userField.leafletId}" "user-field-id"=${userField.id}></i></span>
          </button>
    
          <button type="button" class="btn btn-outline-secondary btn-sm user-field-action field-menu" leaflet-id="${userField.leafletId}"  "user-field-id"=${userField.id}>
            <span><i class="bi bi-list user-field-action field-menu" leaflet-id="${userField.leafletId}" "user-field-id"=${userField.id}></i></span>
          </button>
          <button type="button" class="btn btn-outline-secondary btn-sm user-field-action delete " leaflet-id="${userField.leafletId}" "user-field-id"=${userField.id}>
            <span><i class="bi bi-trash user-field-action delete" leaflet-id="${userField.leafletId}" "user-field-id"=${userField.id}></i></span>
          </button>
        </form>
      </span>  
  </div>
  <div id="accordionField-${userField.leafletId}" class="accordion-collapse collapse">
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
  // highlightPolygon(event.layer);
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
    console.log("event fired", selectedAdminAreas);

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
            style: function (feature) {
                return { color: color };
            },
            onEachFeature: function (feature, layer) {
                layer.bindTooltip(`${feature.properties.nuts_name}`);
                  // {
              //   <div>
              //   <strong>${feature.properties.nuts_name}!!</strong><br>
              //   <button class="btn save-user-field-btn">Save as User Field</button>
              //     </div>
              // `, { 
                // direction: 'top',
                // permanent: false, // Tooltip is shown on hover
                // // sticky: true,     // Tooltip stays open near the cursor
                // className: 'custom-tooltip' // Optional custom CSS class
              // }
            // );
            //   layer.on('tooltipopen', function (e) {
            //     var saveButton = this._tooltip._contentNode.querySelector('.save-user-field-btn');
            //     var feature = e.target.feature;
            //     saveButton.addEventListener('click', function (e, feature) {
            //       var userField = new UserField(feature.properties.nuts_name, layer);

            //       console.log(`Save as User Field button clicked for feature ID: ${featureId}`, saveButton, featureId);
                  
 

            //   });
            // });
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
  saveProject('save');
});

document.getElementById('monica-project-save-as').addEventListener('click', function () {
  saveProject('save-as');
}
);

function saveProject(saveMode) {
  var swnMonicaProject = JSON.parse(localStorage.getItem('project'));
  console.log('swnMonicaProject', swnMonicaProject);
  // try {

      swnMonicaProject.updated = Date.now();
      handleAlerts({'success': true, 'message': 'Project save trying'});

      fetch(saveProjectUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          csrfmiddlewaretoken: csrfToken,
          swnMonicaProject: swnMonicaProject,
          saveMode: saveMode,
        }),
      })
        .then(response => response.json())
        .then(data => {
          console.log('data', data);
          handleAlerts(data.message);
        });
      
    // } catch { error => console.log('error', error)}


  // } catch (error) {
  // }
    
  
};



console.log("userFields before getData", userFields);
getData();
});