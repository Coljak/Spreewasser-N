import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, toolboxSinks, updateDropdown } from '/static/toolbox/toolbox.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { initializeInfiltration } from '/static/toolbox/infiltration.js';
import { initializeSiekerSurfaceWaters } from '/static/toolbox/sieker_surface_waters.js';
import { initializeSiekerSink } from '/static/toolbox/sieker_sink.js';
initializeSiekerSink
import { 
  projectRegion, 
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
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

document.addEventListener("DOMContentLoaded", () => {
  // Hide the coordinate form card from plain Monica
  const project = new ToolboxProject();
  project.saveToLocalStorage();


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
    let project = ToolboxProject.loadFromLocalStorage();
    // TODO: featureGroup as getFeatureGroup
    selectUserField(userFieldId,  project, featureGroup);
    
  });

  $('#saveToolboxProjectButton').on('click', () => {
    console.log('saveToolboxProjectButton clicked');
    
      // Get the project name field
      const projectNameInput = $('#id_project_name');
      const projectName = projectNameInput.val().trim();
  
      // Check if the project name is empty
      if (!projectName) {
          projectNameInput.addClass('is-invalid'); // Bootstrap class for red highlight
          projectNameInput.focus();
          return; // Stop execution if validation fails
      } else {
          projectNameInput.removeClass('is-invalid'); // Remove error class if fixed
      }
  

      const project = new ToolboxProject();
  
      try {
          project.userField = $('#userFieldSelect').val();
      } catch (e) {
          console.log('UserField not found');
      }

      try {
        project.toolboxType = $('#projectTypeSelect').val();
    } catch (e) {
        console.log('ProjectType not found');
    }
  
      project.name = projectName;
      project.description = $('#id_project_description').val();
  
      project.saveToLocalStorage();
  
      fetch('save-project/', {
          method: 'POST',
          body: JSON.stringify(project),
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCSRFToken(),
          }
      })
      .then(response => response.json())
      .then(data => {
          console.log('data', data);
          if (data.message.success) {
              project.id = data.project_id;
              // $('#project-info').find('.card-title').text('Project '+ data.project_name);
              addToDropdown(data.project_id, data.project_name, document.querySelector('.toolbox-project.form-select'));
              // updateDropdown('toolbox-project', data.project_id);
              handleAlerts(data.message);
              
              projectModalForm.reset();
              
              $('#toolboxProjectModal').modal('hide');
              project.saveToLocalStorage();
          } else {
              handleAlerts(data.message);
          }
      });
  });


const demBounds = [
  [47.136744752, 15.57241882],
  [55.058996788, 5.564783468],
];
const toolboxBounds = [
  [51.9015194452089901, 14.5048979594768852],
  [52.7436194452089921, 13.4503979594768843]
];
const sinksBounds = [
  [51.903417526,14.473467455],
  [52.742055454,13.500732582]
];

const demOverlay = L.imageOverlay(demUrl, demBounds, { opacity: 0.5 });
const toolboxOverlaySoil = L.imageOverlay(toolboxUrl, toolboxBounds, { opacity: 1.0 });
const toolboxOverlaySinks = L.imageOverlay(toolboxSinksUrl, sinksBounds, { opacity: 1.0 });

const toolboxOutlineInjection = new L.geoJSON(outline_injection, {
  attribution: 'Outline Injection',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name);
}
});

const toolboxOutlineSurfaceWater = new L.geoJSON(outline_surface_water, {
  attribution: 'Outline Surface Water',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name);
}
});

const toolboxOutlineInfiltration = new L.geoJSON(outline_infiltration, {
  attribution: 'Outline Infiltration',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name);
}
});


const markers = L.markerClusterGroup({
    iconCreateFunction: function (cluster) {
    const count = cluster.getChildCount();

    const html = `
      <div class="custom-cluster-icon">
        <img src="/static/images/water-level-circle_green_small.png" alt="icon" />
        <span class="count">${count}</span>
      </div>
    `;

    return L.divIcon({
      html: html,
      className: 'water-level-cluster-wrapper',
    });
  }

});


const waterLevelIcon = L.icon({
  iconUrl: '/static/images/water-level-circle_blue_small.png',
  iconSize: [30, 30], // size of the icon
  iconAnchor: [15, 15], // point of the icon which will correspond to marker's location
  popupAnchor: [0, 0] // point from which the popup should open relative to the iconAnchor
});
//https://www.pegelonline.wsv.de/webservice/dokuRestapi
fetch('https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json?includeTimeseries=true&includeCurrentMeasurement=true') // Replace with your actual API
  .then(response => response.json())
  .then(data => {
    data.forEach(station => {
      if (station.latitude && station.longitude) {
        const marker = new L.Marker([station.latitude, station.longitude], {
          icon: waterLevelIcon,
          title: station.shortname || station.name // Use shortname or name as title
        });

        // Create tooltip content
        const tooltipContent = `
          <strong>${station.shortname}</strong><br>
          Nummer: ${station.number}<br>
          Behörde: ${station.agency}<br>
          Gewässer: ${station.water?.shortname || 'N/A'}</br>
          Flusskilometer: ${station.km || 'N/A'}<br>
          Aktuelle Messung: ${station.timeseries[0].currentMeasurement?.value || 'N/A'} ${station.timeseries[0]?.unit || ''}<br>
          Wasserstand: ${station.timeseries[0].currentMeasurement?.stateMnwMhw || 'N/A'},  ${station.timeseries[0].currentMeasurement?.stateNswHsw || ''}<br>
          <a href="https://www.pegelonline.wsv.de/charts/OnlineVisualisierungGanglinie?pegeluuid=${station.uuid}&imgBreite=450&pegelkennwerte=HSW,GLW&dauer=300" target="_blank">Details</a><br>
          <a href="https://www.pegelonline.wsv.de/webservices/zeitreihe/visualisierung?pegeluuid=${station.uuid}" target="_blank">Zeitreihe</a>
        `;

        marker.bindPopup(tooltipContent);
        marker.bindTooltip(tooltipContent, {
          permanent: false,
          direction: 'top',
          className: 'water-level-tooltip'
        });
        marker.on('click', function () {

            marker.openPopup();

        });
        marker.on('mouseover', function () {
          marker.openTooltip();
        });
        marker.on('mouseout', function () {
          marker.closeTooltip();
        });
        markers.addLayer(marker);
        ;
      }
    });
    return markers
  })
  .catch(error => {
    console.error('Error fetching data:', error);
  });

  
  // markers.addTo(map);

const overlayLayers = {
  "demOverlay": demOverlay,
  "projectRegion": projectRegion,
  "toolboxOverlaySoil": toolboxOverlaySoil,
  "toolboxOverlaySinks": toolboxOverlaySinks,
  "toolboxOutlineInjection": toolboxOutlineInjection,
  "toolboxOutlineSurfaceWater": toolboxOutlineSurfaceWater,
  "toolboxOutlineInfiltration": toolboxOutlineInfiltration,
  "sinks": toolboxSinks,
  "waterLevels": markers,
};



// toolbox specific overlays
var featureGroup = new L.FeatureGroup()
map.addLayer(featureGroup);
featureGroup.bringToFront();

initializeMapEventlisteners(map, featureGroup);
initializeDrawControl(map, featureGroup);
 
initializeSidebarEventHandler({
  sidebar: document.querySelector(".sidebar-content"),
  map,
  baseMaps,
  overlayLayers,
  getUserFields: () => localStorage.getItem("userFields") ? JSON.parse(localStorage.getItem("userFields")) : {},
  getFeatureGroup: () => { return featureGroup; },
  getProject: () => ToolboxProject.loadFromLocalStorage(),
});

createNUTSSelectors({getFeatureGroup: () => { return featureGroup; }});





// document.getElementById('toolbox-project-save').addEventListener('click', function () {
//   const project = ToolboxProject.loadFromLocalStorage();

//   saveProject(project);
// });



function startInfiltration() {
  console.log('start Infiltration')
  const userField = ToolboxProject.loadFromLocalStorage().userField;
  // const userField = project.userField;
  if (userField) {
  
    fetch('load_infiltration_gui/' + userField + '/')
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        handleAlerts(data);
        return;
      }
        // Replace HTML content
      $('#toolboxButtons').addClass('d-none');
      $('#toolboxPanel').removeClass('d-none');
      $('#toolboxPanel').html(data.html);
    })
    .then(() => {
      initializeInfiltration();
      // initializeSliders();

    })
    // .catch(error => console.error("Error fetching data:", error));
  } else {
    handleAlerts({ success: false, message: 'Please select a user field!' });
  }
};


// Sieker
function startSurfaceWaters() {
  console.log('startSurfaceWaters')
  const userField = ToolboxProject.loadFromLocalStorage().userField;
  let layers = {}
  // const userField = project.userField;
  if (userField) {
  
    fetch('load_surface_waters_gui/' + userField + '/')
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        handleAlerts(data);
        return;
      }
        // Replace HTML content
      $('#toolboxButtons').addClass('d-none');
      $('#toolboxPanel').removeClass('d-none');
      $('#toolboxPanel').html(data.html);
      layers = data.layers || {};
      return layers;
    })
    .then((layers) => {
      if (!layers || Object.keys(layers).length === 0) { 
        return;
      } else {
        initializeSiekerSurfaceWaters(layers);
      }
    })
    // .catch(error => console.error("Error fetching data:", error));
  } else {
    handleAlerts({ success: false, message: 'Please select a user field!' });
  }
};


function startSiekerSinks() {
  console.log('start Infiltration')
  const userField = ToolboxProject.loadFromLocalStorage().userField;
  // const userField = project.userField;
  if (userField) {
  
    fetch('load_sieker_sink_gui/' + userField + '/')
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        handleAlerts(data);
        return;
      }
        // Replace HTML content
      $('#toolboxButtons').addClass('d-none');
      $('#toolboxPanel').removeClass('d-none');
      $('#toolboxPanel').html(data.html);
    })
    .then(() => {
      initializeSiekerSink();
      // initializeSliders();

    })
    // .catch(error => console.error("Error fetching data:", error));
  } else {
    handleAlerts({ success: false, message: 'Please select a user field!' });
  }
};







$('#startInfiltration').on('click', () => {
  console.log('startInfiltration clicked');
  startInfiltration()
});
$('#startInjection').on('click', () => {
  console.log('startInjection clicked');
  // startInjection()
});
$('#startSurfaceWaters').on('click', () => {
  console.log('startSurfaceWaters clicked');
  startSurfaceWaters()
});
$('#startSiekerSinks').on('click', () => {
  console.log('startSiekerSinks clicked');
  startSiekerSinks()
});
$('#startWaterDevelopment').on('click', () => {
  console.log('startWaterDevelopment clicked');
  // startWaterDevelopment()
});
$('#startFormerWetlands').on('click', () => {
  console.log('startFormerWetlands clicked');
  // startFormerWetlands()
});
$('#startDrainage').on('click', () => {
  console.log('startDrainage clicked');
  // startDrainage()
});



getUserFieldsFromDb(featureGroup);
if (projectRegionSwitch) {
    projectRegionSwitch.checked = true;

    // Dispatch a native 'change' event
    const event = new Event('change', { bubbles: true });
    projectRegionSwitch.dispatchEvent(event);
  }

});
