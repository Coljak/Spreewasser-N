import { MonicaProject,  loadProjectFromDB, loadProjectToGui, handleDateChange } from '/static/monica/monica_model.js';
import { getGeolocation, handleAlerts, getCSRFToken, saveProject } from '/static/shared/utils.js';
// import { projectRegion, baseMaps, map, initializeMapEventlisteners, initializeDrawControl } from '/static/shared/map_utils.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  createBaseLayerSwitchGroup, 
  changeBasemap, 
  initializeSidebarEventHandler, 
  addLayerToSidebar, 
  getUserFieldIdByLeafletId, 
  getLeafletIdByUserFieldId, 
  getData, 
  highlightLayer, 
  selectUserField,
  handleSaveUserField,
  dismissPolygon,
  
} from '/static/shared/map_sidebar_utils.js';



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

    
  let csrfToken = getCSRFToken();


  // in Create new project modal
  $('#userFieldSelect').on('change', function () { 
    console.log('userFieldSelect change event');
    var userFieldId = $(this).val();
    let project = MonicaProject.loadFromLocalStorage();
    selectUserField(userFieldId,  project, featureGroup);
    
  });
  // all other datepickers are managed in monica_model.js
  $('#todaysDatePicker').on('changeDate focusout', handleDateChange);




// Bounds for DEM image overlay
  const demBounds = [[47.136744752, 15.57241882],[55.058996788, 5.564783468],];
  const droughtBounds = [[46.89, 15.33], [55.31, 5.41],];
  const demOverlay = L.imageOverlay(demUrl, demBounds, { opacity: 0.5 });
  const droughtOverlay = L.imageOverlay(droughtUrl, droughtBounds, { opacity: 0.5 });


// handles clicks on a userField layer in the map
var featureGroup = new L.FeatureGroup()
map.addLayer(featureGroup);
featureGroup.bringToFront();



// zoom to user's layers via chrosshair
// added back-to-home bullseyer button to zoom controls
$(".leaflet-control-zoom").append(
  '<a class="leaflet-control-home" href="#" role="button" title="Project area" area-label="Project area"><i class="bi bi-bullseye"></i></a>',
  '<a class="leaflet-control-geolocation" href="#" role="button" title="My location" area-label="User location"><i class="bi bi-geo"></i></a>'
);


const overlayLayers = {
  "droughtOverlay": droughtOverlay,
  "demOverlay": demOverlay,
  "projectRegion": projectRegion,

};


// ------------------- Sidebar eventlisteners -------------------

// -------------------Sidebar new----------------
initializeDrawControl(map, featureGroup);






  
initializeSidebarEventHandler({
  sidebar: document.querySelector(".sidebar-content"),
  map,
  baseMaps,
  overlayLayers,
  getUserFields: () => localStorage.getItem("userFields") ? JSON.parse(localStorage.getItem("userFields")) : {},
  getFeatureGroup: () => { return featureGroup; },
  getProject: () => MonicaProject.loadFromLocalStorage(),
});

initializeMapEventlisteners(map, featureGroup);

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
});

document.querySelector(".zoom-to-project-region").addEventListener("click", () => {
  map.fitBounds(projectRegion.getBounds());
});

const goToLocationPin = document.getElementsByClassName("leaflet-control-geolocation")[0];
goToLocationPin.addEventListener("click", () => {
  getGeolocation()
    .then((position) => {
      map.setView([position.latitude, position.longitude], 12);
    })
    .catch((error) => {
      console.error(error.message);
      handleAlerts({ success: false, message: error.message });
    });
});


// sidebar Base Layers
createBaseLayerSwitchGroup(baseMaps, map);


//---------------MAP END-------------------------------







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
  const project = MonicaProject.loadFromLocalStorage();

  saveProject(saveProjectUrl, project);
});


getData(loadDataUrl, featureGroup);

});