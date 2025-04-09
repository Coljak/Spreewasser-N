import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, toolboxSinks, updateDropdown } from '/static/toolbox/toolbox.js';
import {initializeSliders} from '/static/toolbox/custom_slider.js';
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



document.addEventListener("DOMContentLoaded", () => {
  // Hide the coordinate form card from plain Monica
  const project = new ToolboxProject();
  project.saveToLocalStorage();


  $('#map').on('click', function (e) {
    if (e.target.classList.contains('show-sink-outline')) {
      const sinkId = e.target.getAttribute('sinkId');
      console.log('sinkId', sinkId);
    } else if (e.target.classList.contains('select-sink')) {
        const sinkId = e.target.getAttribute('sinkId');
        console.log('sinkId', sinkId);
      }
  });


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

const toolboxOutlineGeste = new L.geoJSON(outline_geste, {
  attribution: 'Geste??',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name);
}
});

  const overlayLayers = {
    // "droughtOverlay": droughtOverlay,
    "demOverlay": demOverlay,
    "projectRegion": projectRegion,
    "toolboxOverlaySoil": toolboxOverlaySoil,
    "toolboxOverlaySinks": toolboxOverlaySinks,
    "toolboxOutlineInjection": toolboxOutlineInjection,
    "toolboxOutlineSurfaceWater": toolboxOutlineSurfaceWater,
    "toolboxOutlineInfiltration": toolboxOutlineInfiltration,
    "toolboxOutlineGeste": toolboxOutlineGeste,
    "sinks": toolboxSinks,
  };



// swn-drought specific overlays
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

// sidebar Base Layers
createBaseLayerSwitchGroup(baseMaps, map);

var sinkFeatureGroup = new L.FeatureGroup()
map.addLayer(sinkFeatureGroup);

var enlargedSinkFeatureGroup = new L.FeatureGroup()
map.addLayer(enlargedSinkFeatureGroup);

var lakesFeatureGroup = new L.FeatureGroup()
map.addLayer(lakesFeatureGroup);

var streamsFeatureGroup = new L.FeatureGroup()
map.addLayer(streamsFeatureGroup);

// document.getElementById('toolbox-project-save').addEventListener('click', function () {
//   const project = ToolboxProject.loadFromLocalStorage();

//   saveProject(project);
// });

const showSinkOutline = function (sinkId) {
  const project = ToolboxProject.loadFromLocalStorage();
  console.log('project', project);
  console.log('showSinkOutline sinkId', sinkId);
}

function getSinks(isEnlargedSink) {
  const project = ToolboxProject.loadFromLocalStorage();
  project['enlargedSink'] = isEnlargedSink;
  fetch('get_selected_sinks/', {
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
    const activeGroup = isEnlargedSink ? enlargedSinkFeatureGroup : sinkFeatureGroup;

    // Clear existing markers
    activeGroup.clearLayers();

    // Initialize marker cluster
    let markers = L.markerClusterGroup();

    // Iterate through features and add them to the cluster
    data.features.forEach(feature => {
        let coords = feature.coordinates; // Get the lat/lng coordinates
        let latlng = [coords[1], coords[0]]; // Swap for Leaflet format

        // Create popup content with all properties
        let popupContent = `
            <b>Tiefe:</b> ${feature.properties.depth} m<br>
            <b>Fläche:</b> ${feature.properties.area} m²<br>
            <b>Bodeneignung:</b> ${feature.properties.index_soil}<br>
            <b>Landnuntzung 1:</b> ${feature.properties.land_use_1}<br>
            ${feature.properties.land_use_2 ? `<b>Landnuntzung 2:</b> ${feature.properties.land_use_2}<br>` : ''}
            ${feature.properties.land_use_3 ? `<b>Landnuntzung 3:</b> ${feature.properties.land_use_3}<br>` : ''}
            ${feature.properties.land_use_4 ? `<b>Landnuntzung 4:</b> ${feature.properties.land_use_4}<br>` : ''}
        `;


        // Create a marker
        let marker = L.marker(latlng).bindPopup(popupContent);
        marker.on('mouseover', function () {
          this.openPopup();
        });

        // Hide popup when not hovering
        marker.on('mouseout', function () {
            this.closePopup();
        });
        marker.on('contextmenu', function (event) {
          L.popup()
              .setLatLng(event.latlng)
              .setContent(`
                  <b>Sink Options</b><br>
                  <button class="btn btn-outline-secondary show-sink-outline" sinkId=${feature.properties.id}">Show Sink Outline</button>
                  <button class="btn btn-outline-secondary select-sink" sinkId=${feature.properties.id}">Select Sink</button>
              `)
              .openOn(map);
      });
      

        // Add marker to cluster
        markers.addLayer(marker);
    });

    // Add the cluster group to the map
    activeGroup.addLayer(markers);
    map.fitBounds(markers.getBounds());
})
.catch(error => console.error("Error fetching data:", error));
};

function getLakes(){
  const project = ToolboxProject.loadFromLocalStorage();
  project['lakes'] = true;
  fetch('get_selected_lakes/', {
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
    const activeGroup = project['lakes'] ? lakesFeatureGroup : streamsFeatureGroup;

    // Clear existing markers
    activeGroup.clearLayers();

    // Initialize marker cluster
    let markers = L.markerClusterGroup();

    // Iterate through features and add them to the cluster
    data.features.forEach(feature => {
        let coords = feature.coordinates; // Get the lat/lng coordinates
        let latlng = [coords[1], coords[0]]; // Swap for Leaflet format

        // Create popup content with all properties
        let popupContent = `
            <b>Länge:</b> ${feature.properties.shape_length} m<br>
            ${feature.properties.shape_area ? `<b>Fläche:</b> ${feature.properties.shape_area} m²<br>` : ''}         
            <b>Mindestüberschuss:</b> ${feature.properties.min_surplus_volume}<br>
            <b>Durchschnittsüberschuss 1:</b> ${feature.properties.mean_surplus_volume}<br>
            <b>Maximalüberschuss:</b> ${feature.properties.max_surplus_volume}<br>
            <b>Tage mit Überschuss:</b> ${feature.properties.plus_days}<br>
        `;


        // Create a marker
        let marker = L.marker(latlng).bindPopup(popupContent);
        marker.on('mouseover', function () {
          this.openPopup();
        });

        // Hide popup when not hovering
        marker.on('mouseout', function () {
            this.closePopup();
        });
        marker.on('contextmenu', function (event) {
          L.popup()
              .setLatLng(event.latlng)
              .setContent(`
                  <b>Sink Options</b><br>
                  <button class="btn btn-outline-secondary show-sink-outline" sinkId=${feature.properties.id}">Show Sink Outline</button>
                  <button class="btn btn-outline-secondary select-sink" sinkId=${feature.properties.id}">Select Sink</button>
              `)
              .openOn(map);
      });
      

        // Add marker to cluster
        markers.addLayer(marker);
    });

    // Add the cluster group to the map
    activeGroup.addLayer(markers);
    map.fitBounds(markers.getBounds());
})
.catch(error => console.error("Error fetching data:", error));
}

// document.getElementById('toolboxPanel').addEventListener('change', function (e) {
//   if (e.target.classList.contains('hiddeninput'))  {
//     // all sliders
//     const project = ToolboxProject.loadFromLocalStorage();
//     const inputId = e.target.id;
//     const inputVal = e.target.value;

//     // Set the corresponding property in the infiltration object
//     project.infiltration[inputId] = inputVal;

//     project.saveToLocalStorage();
//     console.log('Updated infiltration', inputId, '=', inputVal);
//   } else if (e.target.classList.contains('form-check-input')) {
//     // checkboxes
//     const project = ToolboxProject.loadFromLocalStorage();
//     const inputId = e.target.id;
//     const inputVal = e.target.checked;
    
//     // Set the corresponding property in the infiltration object
//     project.infiltration[inputId] = inputVal;

//     project.saveToLocalStorage();
//     console.log('Updated infiltration', inputId, '=', inputVal);

//   };
// }) 
$('#toolboxPanel').on('change',  function (event) {
  const $target = $(event.target);
  if ($target.hasClass('hiddeninput'))  {
  // all sliders
    const project = ToolboxProject.loadFromLocalStorage();
    const inputId = $target.attr('id');
    const inputVal = $target.val();

    // Set the corresponding property in the infiltration object
    project.infiltration[inputId] = inputVal;

    project.saveToLocalStorage();
    console.log('Updated infiltration', inputId, '=', inputVal);
  } else if ($target.hasClass('form-check-input')) {
    // checkboxes
    const project = ToolboxProject.loadFromLocalStorage();
    const inputId = $target.attr('id');
    const inputVal = $target.is(':checked');
    
    // Set the corresponding property in the infiltration object
    project.infiltration[inputId] = inputVal;

    project.saveToLocalStorage();
    console.log('Updated infiltration', inputId, '=', inputVal);

  };
});


$('#injectionGo').on('click', function () {
  const project = ToolboxProject.loadFromLocalStorage();
  const userField = project.userField;
  
  fetch('load_infiltration_gui/' + userField + '/')
      .then(response => response.json())
      .then(data => {
          
          
          // Replace HTML content
          $('#toolboxPanel').html(data.html);

      })
      .then(() => {
        initializeSliders();

    })
    
      .catch(error => console.error("Error fetching data:", error));
});

let sinksVisible = true;
let enlargedSinksVisible = true;
let lakesVisible = true;
let streamsVisible = true;
document.getElementById('toggleSinks').addEventListener('click', function () {
  if (sinksVisible) {
      map.removeLayer(sinkFeatureGroup);
  } else {
      map.addLayer(sinkFeatureGroup);
  }
  sinksVisible = !sinksVisible;
});
document.getElementById('toggleEnlargedSinks').addEventListener('click', function () {
  if (enlargedSinksVisible) {
      map.removeLayer(enlargedSinkFeatureGroup);
  } else {
      map.addLayer(enlargedSinkFeatureGroup);
  }
  enlargedSinksVisible = !enlargedSinksVisible;
});
document.getElementById('toggleLakes').addEventListener('click', function () {
  if (lakesVisible) {
      map.removeLayer(lakesFeatureGroup);
  } else {
      map.addLayer(lakesFeatureGroup);
  }
  lakesVisible = !lakesVisible;
});
document.getElementById('toggleStreams').addEventListener('click', function () {
  if (streamsVisible) {
      map.removeLayer(streamsFeatureGroup);
  } else {
      map.addLayer(streamsFeatureGroup);
  }
  streamsVisible = !streamsVisible;
});



getUserFieldsFromDb(featureGroup);

});