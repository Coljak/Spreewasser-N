import { MonicaCalculation, MonicaProject, Rotation, Workstep, loadProjectFromDB, loadProjectToGui, handleDateChange } from '/static/monica/monica.js';
import { getGeolocation, handleAlerts, getCSRFToken, saveProject } from '/static/shared/utils.js';
// import { projectRegion, baseMaps, map, initializeMapEventlisteners, initializeDrawControl } from '/static/shared/map_utils.js';
import { 
  projectRegion, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  createNUTSSelectors,
  initializeSidebarEventHandler, 
  getUserFieldsFromDb, 
  highlightLayer, 
  selectUserField,
  dismissPolygon,
  demOverlay,
} from '/static/shared/map_sidebar_utils.js';



var userFieldStore = null;
function addSwnProject(userFieldId){
  
            
            
  // $('#newProjectForm')[0].reset();
  $('#monicaNewProjectModal').find('.modal-title').text('Neues Projekt erstellen');
  $('#monicaNewProjectModal').modal('show');
}

document.addEventListener("DOMContentLoaded", () => {
  // Hide the coordinate form card from plain Monica
  console.log('Content loaded')
  $('#coordinateFormCard').hide();

  // center map at geolocation
  getGeolocation()
    .then((position) => {
      map.setView([position.latitude, position.longitude], 12);
    })
    .catch((error) => {
        console.error(error.message);
        handleAlerts({ success: false, message: error.message });

        // Fallback: center map on projectRegion if geolocation fails
      if (typeof projectRegion !== 'undefined' && projectRegion.getBounds) {
        map.fitBounds(projectRegion.getBounds());
      } else {
        // Optional hard fallback if projectRegion is not defined
        map.setView([52.40, 14.174], 10);
      }
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

  $('#btnDownloadCsv').on('click', function() {
    fetch('/monica/download_irrigation_csv/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
      },
      body: JSON.stringify({
        // You can send additional data if needed
      }),
    })
    .then(response => response.blob())
    .then(blob => {
      // Create a link to download the file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'bewaesserungsempfehlung.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
    })
    .catch(error => {
      console.error('Error downloading CSV:', error);
      handleAlerts({ success: false, message: error.message });
    });
});

// Bounds for DEM image overlay

const droughtBounds = [[46.89, 15.33], [55.31, 5.41],];

const droughtOverlay = L.imageOverlay(droughtUrl, droughtBounds, { opacity: 0.5, pane: 'overlayRasterPane' });



const overlayLayers = {
  "droughtOverlay": droughtOverlay,
  "demOverlay": demOverlay,
  "projectRegion": projectRegion,
};



// swn-drought specific overlays
var featureGroup = new L.FeatureGroup({pane: "polygonPane",})
map.addLayer(featureGroup);
featureGroup.bringToFront();

initializeMapEventlisteners(map, featureGroup, MonicaProject);
initializeDrawControl(map, featureGroup);
document.addEventListener('drought:dom-ready', () => {
  initializeSidebarEventHandler({
    sidebar: document.querySelector(".sidebar-content"),
    map,
    overlayLayers,
    getUserFields: () => localStorage.getItem("userFields") ? JSON.parse(localStorage.getItem("userFields")) : {},
    getFeatureGroup: () => { return featureGroup; },
    getProject: () => MonicaProject.loadFromLocalStorage(),
    loadProjectFromDb: (projectId) => loadProjectFromDB(projectId),
    startApplication: (project) => loadProjectToGui(project),
    addProject: (userFieldId) => addSwnProject(userFieldId),
});
});
 


createNUTSSelectors({getFeatureGroup: () => { return featureGroup; }});

// sidebar Base Layers
// createBaseLayerSwitchGroup(baseMaps, map);



getUserFieldsFromDb(featureGroup);
if (projectRegionSwitch) {
    projectRegionSwitch.checked = true;

    // Dispatch a native 'change' event
    const event = new Event('change', { bubbles: true });
    projectRegionSwitch.dispatchEvent(event);
  }

// inject the rest of Monica html

async function loadDeferredMonicaHtml() {
  const rotationHtml = await fetch(getMonicaRotationUrl).then(r => r.text());
  $('#swnMonica').after(rotationHtml);

  const tabHtml = await fetch(getTabRotationUrl).then(r => r.text());
  $('#tabGeneralParameters').after(tabHtml);
  document.dispatchEvent(new Event('drought:dom-ready'));
}

loadDeferredMonicaHtml().catch(console.error);



});