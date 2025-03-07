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
  openUserFieldNameModal,
  createNUTSSelectors,
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


  // dropDownMenu in the project modal
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


// swn-drought specific overlays
var featureGroup = new L.FeatureGroup()
map.addLayer(featureGroup);
featureGroup.bringToFront();

const overlayLayers = {
  "droughtOverlay": droughtOverlay,
  "demOverlay": demOverlay,
  "projectRegion": projectRegion,
};

initializeMapEventlisteners(map, featureGroup);
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

createNUTSSelectors({getFeatureGroup: () => { return featureGroup; }});


// $(function () {
//   $('[data-toggle="tooltip"]').tooltip();
// });


// sidebar Base Layers
createBaseLayerSwitchGroup(baseMaps, map);


// export function createNUTSSelectors() {
// // Create a LayerGroup to hold the displayed polygons
// // const stateCountyDistrictLayer = L.layerGroup().addTo(map);
// const stateCountyDistrictLayer = new L.FeatureGroup().addTo(map);
// stateCountyDistrictLayer.on("click", function (event) {
//   console.log("stateCountyDistrictLayer click event: ", event);

//   // Get the clicked layer
//   let clickedLayer = event.layer;
  
//   // Confirm action with the user
//   if (confirm("Save this region as a user field?")) {
//     openUserFieldNameModal(clickedLayer, featureGroup) 
//   }
// });


// stateCountyDistrictLayer.on("click", function (event) {
//   console.log("stateCountyDistrictLayer click event: ", event);
// });

// // Handle dropdown menu change event
// // Multiple Select from https://www.cssscript.com/select-box-virtual-scroll/
// VirtualSelect.init({ 
//   ele: '#stateSelect',
//   placeholder: 'Bundesland',
//   required: false,
//   disableSelectAll: true,
// });
// VirtualSelect.init({ 
//   ele: '#districtSelect',
//   placeholder: 'Regierungsbezirk',
//   required: false,
//   disableSelectAll: true,
// });
// VirtualSelect.init({ 
//   ele: '#countySelect',
//   placeholder: 'Landkreis',
//   required: false,
//   disableSelectAll: true,
// });

// var administrativeAreaDiv = document.querySelectorAll('div.administrative-area');
// var selectedAdminAreas = {
//   states: [],
//   counties: [],
//   districts: [],
// };


// administrativeAreaDiv.forEach(function (areaDropdown) {
//   areaDropdown.addEventListener('change', function (event) {
//     stateCountyDistrictLayer.clearLayers();
//     var name = areaDropdown.getAttribute("name");
//     var selectedOptions = areaDropdown.value;
//     selectedAdminAreas[name] = selectedOptions;

//     for (let key in selectedAdminAreas) {
//       if (selectedAdminAreas[key].length > 0) {
//         selectedAdminAreas[key].forEach(function (polygon) {
//           var url = loadNutsUrl + key + '/' + polygon + '/';
//         console.log("URL", url)
//         var color = '';
//         if (key == 'states') {
//             color = 'purple';
//         } else if (key == 'counties') {
//             color = 'blue';
//         } else if (key == 'districts') {
//             color = 'green';
//         }
//         var geojsonLayer = new L.GeoJSON.AJAX(url, {
//             style: {
//                 color: color 
//             },
//             onEachFeature: function (feature, layer) {
//                 layer.bindTooltip(`${feature.properties.nuts_name}`);
//                 layer.setStyle({
//                   fill: false, 
//                 });
//             }
//         });
//         console.log("geojsonLayer", geojsonLayer)
//         geojsonLayer.addTo(stateCountyDistrictLayer);
//         });
//       }
//     }
//   }); 
// });

// };

document.getElementById('monica-project-save').addEventListener('click', function () {
  const project = MonicaProject.loadFromLocalStorage();

  saveProject(saveProjectUrl, project);
});


getData(loadDataUrl, featureGroup);

});