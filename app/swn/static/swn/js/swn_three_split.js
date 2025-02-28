import { MonicaProject,  loadProjectFromDB, loadProjectToGui, handleDateChange } from '/static/monica/monica_model.js';
import { getGeolocation, handleAlerts } from '/static/shared/utils.js';
import { projectRegion, baseMaps, map, initializeMapEventlisteners } from '/static/shared/map_utils.js';
import { createBaseLayerSwitchGroup, changeBasemap, initializeSidebarEventHandler, addLayerToSidebar } from '/static/shared/map_sidebar_utils.js';



document.addEventListener("DOMContentLoaded", () => {
  // Hide the coordinate form card from plain Monica
  $('#coordinateFormCard').hide();

  // center map at geolocation
  getGeolocation()
    .then((position) => {
      map.setView([position.latitude, position.longitude], 12);
    })
    .catch((error) => {
        console.error(error.message);
        handleAlerts({ success: false, message: error.message });
    });

    
  let csrfToken = document.cookie
    .split("; ")
    .find(row => row.startsWith("csrftoken="))
    .split("=")[1];


  // in Create new project modal
  $('#userFieldSelect').on('change', function () { 
    console.log('userFieldSelect change event');
    var userFieldId = $(this).val();
    let leafletId = getLeafletIdByUserFieldId(userFieldId);
    highlightLayer(leafletId);
    selectUserField(userFieldId);
    
  });
  // all other datepickers are managed in monica_model.js
  $('#todaysDatePicker').on('changeDate focusout', handleDateChange);

  // -----------User Field Name Modal -----------------

  // -------------MAP --------------------------------------




// Bounds for DEM image overlay
  const demBounds = [[47.136744752, 15.57241882],[55.058996788, 5.564783468],];
  const droughtBounds = [[46.89, 15.33], [55.31, 5.41],];
  const demOverlay = L.imageOverlay(demUrl, demBounds, { opacity: 0.5 });
  const droughtOverlay = L.imageOverlay(droughtUrl, droughtBounds, { opacity: 0.5 });


  function selectUserField(userFieldId) {
    console.log("selectUserField", userFieldId);
    const project = MonicaProject.loadFromLocalStorage();
    if (project.userField && project.userField != userFieldId && project.id) {
      let modal = document.getElementById('interactionModal');
      let modalInstance = new bootstrap.Modal(modal);
      document.getElementById('interactionModalTitle').innerHTML = "User Field Selection";
      document.getElementById('interactionModalText').innerHTML = "you are changing a Monica Project without UserField to a SWN Project with UserField. The location of the project will be changed to the UserField location.";
      $('#interactionModalOK').on('click', function () {
        project.userField = userFieldId;
        project.saveToLocalStorage();
        highlightLayer(getLeafletIdByUserFieldId(userFieldId));
      }
      );
      modalInstance.show(); 
    }
    //  else {
    //   alert('uncaught option')
    //   project.userField = userFieldId;
    //   project.saveToLocalStorage();
    //   highlightLayer(getLeafletIdByUserFieldId(userFieldId));
    // }
    
    
  }


// handles clicks on a userField layer in the map
var featureGroup = new L.FeatureGroup()
map.addLayer(featureGroup);
featureGroup.bringToFront();

featureGroup.on("click", function (event) {
  let leafletId = Object.keys(event.layer._eventParents)[0];
  let userFieldId = getUserFieldIdByLeafletId(leafletId);
  selectUserField(userFieldId);
  console.log("droughtFeutureGroup click event: highlight ", leafletId, event.layer);
  // highlightPolygon(event.layer)
});

// highlight layer and li element on click in the sidebar

function highlightLayer(leafletId) {
  console.log("HIGHLIGHT", leafletId);
  // remove highlight from all layers
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

     
function getLeafletIdByUserFieldId(id) {
  const entry = Object.values(userFields).find(field => field.id == id);
  console.log("getLeafletIdByUserFieldId", id, entry, userFields);
  return entry ? entry.leafletId : null;
};

function getUserFieldIdByLeafletId(leafletId) {
  const entry = Object.values(userFields).find(field => field.leafletId == leafletId);
  console.log("getUserFieldIdByLeafletId", leafletId, entry, userFields);
  return entry ? entry.id : null;
};

// zoom to user's layers via chrosshair
// added back-to-home bullseyer button to zoom controls
$(".leaflet-control-zoom").append(
  '<a class="leaflet-control-home" href="#" role="button" title="Project area" area-label="Project area"><i class="bi bi-bullseye"></i></a>',
  '<a class="leaflet-control-geolocation" href="#" role="button" title="My location" area-label="User location"><i class="bi bi-geo"></i></a>'
);



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



//-------------------- Baselayers ------------------------------
const leafletSidebarContent = document.querySelector(".sidebar-content");

const overlayLayers = {
  "droughtOverlay": droughtOverlay,
  "demOverlay": demOverlay,
  "projectRegion": projectRegion,

};


// ------------------- Sidebar eventlisteners -------------------

// -------------------Sidebar new----------------
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


$(function () {
  $('[data-toggle="tooltip"]').tooltip();
});

// -------------------Sidebar new end----------------
leafletSidebarContent.addEventListener("click", (event) => {
  const clickedElement = event.target;
  if (clickedElement.classList.contains("user-field-header") || clickedElement.classList.contains("user-field-btn")) {
    const leafletId = clickedElement.getAttribute("leaflet-id");
    console.log("user-field-header clicked", leafletId);

    selectUserField(getUserFieldIdByLeafletId(leafletId));
    
  } else if (clickedElement.classList.contains("user-field-action")) {
    const leafletId = clickedElement.getAttribute("leaflet-id");
    console.log("user-field-action clicked", leafletId);
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
            const project = loadProjectFromDB(projectId);
            loadProjectToGui(project);
            selectUserField(project.userField);
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

  
  initializeSidebarEventHandler({
    sidebar: document.querySelector(".sidebar-content"),
    map,
    baseMaps,
    overlayLayers,
    getUserFields: () => userFields, // Always returns the latest userFields
    featureGroup,
});

initializeMapEventlisteners(map, featureGroup);

document.querySelector(".zoom-to-project-region").addEventListener("click", () => {
  map.fitBounds(projectRegion.getBounds());
});


// sidebar Base Layers
createBaseLayerSwitchGroup(baseMaps, map);


//---------------MAP END-------------------------------
var userFields = {};
// localStorage.setItem('userFields', JSON.stringify(userFields));



class UserField {
  constructor(name, id=null, userProjects=[]) {
    this.name = name;
    // this.layer = layer;
    this.id = id;
    this.userProjects = userProjects;
  }
};



// Save a newly created userField in DB
function saveUserField(name, geomJson) {
  return new Promise((resolve, reject) => {
    const requestData = {
      csrfmiddlewaretoken: csrfToken,
      geom: JSON.stringify(geomJson.geometry),
      name: name,
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
      handleAlerts({'success': true, 'message': 'UserField saved successfully'});
      resolve(data); 
    })
    .catch(error => {
      handleAlerts({'success': false, 'message': 'Error saving UserField: ', error});
      reject(error); 
    });
  });
};

// Load all user fields from DB
const getData = async function () {
  // let userFields = {};
  fetch(loadUrl, {
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
  });
};


// Modal Userfield Name 
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
            // layerGeoJson,
            data.id,  
          );
          
          featureGroup.addLayer(layerGeoJson);
          // temporary layer is removed from the map
          featureGroup.removeLayer(layer);
          userField.leafletId  = featureGroup.getLayerId(layerGeoJson);
          userFields[userField.leafletId] = userField;
          addLayerToSidebar(userField, layerGeoJson);
          selectUserField(userField.id);
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
  const project = MonicaProject.loadFromLocalStorage();
      project.updated = Date.now();

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