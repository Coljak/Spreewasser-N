import { MonicaCalculation, MonicaProject, Rotation, Workstep, loadProjectFromDB, handleDateChange } from '/static/monica/monica.js';
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
  getUserFieldsFromDb, 
  highlightLayer, 
  selectUserField,
  handleSaveUserField,
  dismissPolygon,
  
} from '/static/shared/map_sidebar_utils.js';


var userFieldStore = null;

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
    // TODO: featureGroup as getFeatureGroup
    selectUserField(userFieldId,  project, featureGroup);
    
  });

  // all other datepickers are managed in monica_model.js
  $('#todaysDatePicker').on('changeDate focusout', handleDateChange);


// Bounds for DEM image overlay
  const demBounds = [[47.136744752, 15.57241882],[55.058996788, 5.564783468],];
  const droughtBounds = [[46.89, 15.33], [55.31, 5.41],];
  const demOverlay = L.imageOverlay(demUrl, demBounds, { opacity: 0.5 });
  const droughtOverlay = L.imageOverlay(droughtUrl, droughtBounds, { opacity: 0.5 });

const overlayLayers = {
  "droughtOverlay": droughtOverlay,
  "demOverlay": demOverlay,
  "projectRegion": projectRegion,
};



// swn-drought specific overlays
var featureGroup = new L.FeatureGroup()
map.addLayer(featureGroup);
featureGroup.bringToFront();

initializeMapEventlisteners(map, featureGroup, MonicaProject);
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

// sidebar Base Layers
createBaseLayerSwitchGroup(baseMaps, map);


// document.getElementById('monica-project-save').addEventListener('click', function () {
//   const project = MonicaProject.loadFromLocalStorage();

//   saveProject(project);
// });


getUserFieldsFromDb(featureGroup);

});