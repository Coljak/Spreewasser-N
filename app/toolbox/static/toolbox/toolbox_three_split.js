import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, toolboxSinks, updateDropdown } from '/static/toolbox/toolbox.js';
// import {initializeSliders} from '/static/toolbox/custom_slider.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
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


  // $('#map').on('click', function (e) {
  //   if (e.target.classList.contains('show-sink-outline')) {
  //     const sinkId = e.target.getAttribute('sinkId');
  //     console.log('sinkId', sinkId);
  //   } else if (e.target.classList.contains('select-sink')) {
  //       const sinkId = e.target.getAttribute('sinkId');
  //       console.log('sinkId', sinkId);
  //     }
  // });


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



  const overlayLayers = {
    // "droughtOverlay": droughtOverlay,
    "demOverlay": demOverlay,
    "projectRegion": projectRegion,
    "toolboxOverlaySoil": toolboxOverlaySoil,
    "toolboxOverlaySinks": toolboxOverlaySinks,
    "toolboxOutlineInjection": toolboxOutlineInjection,
    "toolboxOutlineSurfaceWater": toolboxOutlineSurfaceWater,
    "toolboxOutlineInfiltration": toolboxOutlineInfiltration,
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

var inletConnectionsFeatureGroup = L.featureGroup()
map.addLayer(inletConnectionsFeatureGroup);



// document.getElementById('toolbox-project-save').addEventListener('click', function () {
//   const project = ToolboxProject.loadFromLocalStorage();

//   saveProject(project);
// });

document.getElementById('map').addEventListener('click', function (event) {
  if (event.target.classList.contains('select-sink')) {
    const sinkId = event.target.getAttribute('sinkId');
    const sinkType = event.target.getAttribute('data-type');
    console.log('sinkId', sinkId);
    console.log('sinkType', sinkType);

    const checkbox = document.querySelector(`.sink-select-checkbox[data-type="${sinkType}"][data-id="${sinkId}"]`);
    checkbox.checked = !checkbox.checked;
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
  }
});



function createSinkTableSettings(sinkType, indexVisible) {
  return {
    "order": [[1, "asc"]],
    "searching": false,
    "columnDefs": [
      {
        "targets": 0, // Select a checkbox
        "orderable": false,
        "searchable": false
      },
      {
        "targets": 1, // Tiefe
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 2, // Fläche
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 3, // Volumen
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 4, // Bodeneignung
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 5, // Bodeneignung berechnet
        "visible": indexVisible,
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 6, // Volumen Barriere
        "visible": sinkType === 'sink'? false : true, 
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 7, // Zusätzliches Volumen
        "visible": sinkType === 'sink'? false : true, 
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 8, // Landnutzung 1
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 9, //Landnutzung 2
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 10, //Landnutzung 3
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 11,
        "visible": sinkType === 'sink'? false : true, // Landnutzung 4
        "orderable": true,
        "searchable": false
      },
      // {
      //   "targets": 12,
      //   "visible": indexVisible, // Total Sink Index
      //   "orderable": true,
      //   "searchable": false
      // }
    ]
  }
}

function getSinks(sinkType, featureGroup) {
  let url = 'filter_sinks/';
  if (sinkType === 'enlarged_sink') {
    url = 'filter_enlarged_sinks/';
  }
  const project = ToolboxProject.loadFromLocalStorage();
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(project),
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
    }
  })
  .then(response => response.json())
  .then(data => {
    featureGroup.clearLayers();
    console.log('project', project);
    console.log('project.infiltration', project.infiltration);
    console.log('project.infiltration[`selected_${sinkType}s`]', project.infiltration[`selected_${sinkType}s`]);

    const selected_sinks = project.infiltration[`selected_${sinkType}s`];
    if (data.message.success) {
      
      project.infiltration[`selected_${sinkType}s`] = [];
      
      // Initialize marker cluster
      let markers = L.markerClusterGroup();
      let ids = [];
      
      // Iterate through features and add them to the cluster
      data.feature_collection.features.forEach(feature => {
        ids.push(feature.properties.id);
          let coords = feature.coordinates; // Get the lat/lng coordinates
          let latlng = [coords[1], coords[0]]; // Swap for Leaflet format


          // Create popup content with all properties
          let popupContent = `
              <b>Tiefe:</b> ${feature.properties.depth} m<br>
              <b>Fläche:</b> ${feature.properties.area} m²<br>
              <b>Volumen:</b> ${feature.properties.volume} m³<br>
              <b>Bodeneignung:</b> ${feature.properties.index_soil}<br>
              ${feature.properties.volume_gained ? `<b>Zusätzliches Volumen:</b> ${feature.properties.volume_gained}<br>` : ''}
              ${feature.properties.volume_construction_barrier ? `<b>Volumen Barriere:</b> ${feature.properties.volume_construction_barrier}<br>` : ''}
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
                    <button class="btn btn-outline-secondary show-sink-outline" data-type="${sinkType}" sinkId=${feature.properties.id}">Show Sink Outline</button>
                    <button class="btn btn-outline-secondary select-sink" data-type="${sinkType}" sinkId="${feature.properties.id}">Toggle Sink selection</button>
                `)
                .openOn(map);
        });
          // Add marker to cluster
          markers.addLayer(marker);
      });
      project.saveToLocalStorage();
      // Add the cluster group to the map
      featureGroup.addLayer(markers);


      // Data Table
      const elId = sinkType === 'sink' ? 'sink-table-container' : 'enlarged-sink-table-container';  
      const tableContainer = document.getElementById(elId);


      let tableHTML = ` 
        <table class="table table-bordered table-hover" id="${sinkType}-table">
          <caption>${sinkType === 'sink' ? 'Sinks' : 'Enlarged Sinks'}</caption>
          <thead>
            <tr>
              <th><input type="checkbox" class="sink-select-all-checkbox" data-type="${sinkType}">Select all</th>
              <th>Tiefe (m)</th>
              <th>Fläche (m²)</th>
              <th>Volumen (m³)</th>
              <th>Bodeneignung standard</th>
              <th>Bodeneignung berechnet</th>
              <th>Volumen Barriere</th>
              <th>Zusätzliches Volumen</th>
              <th>Landnutzung 1</th>
              <th>Landnutzung 2</th>
              <th>Landnutzung 3</th>
              <th>Landnutzung 4</th>
            </tr>
          </thead>
          <tbody>
      `;

      data.feature_collection.features.forEach((feature, index) => {
        const p = feature.properties;
        
        tableHTML += `
          <tr data-sink-id="${p.id}">
            <td><input type="checkbox" class="sink-select-checkbox" data-type=${sinkType} data-id="${p.id}"></td>
            <td>${p.depth}</td>
            <td>${p.area}</td>
            <td>${p.volume}</td>
            <td>${p.index_soil}</td>
            <td class="index-total" data-type=${sinkType} data-id="${p.id}"></td>
            <td>${p.volume_construction_barrier ?? '-'}</td>
            <td>${p.volume_gained ?? '-'}</td>
            <td>${p.land_use_1 ?? '-'}</td>
            <td>${p.land_use_2 ?? '-'}</td>
            <td>${p.land_use_3 ?? '-'}</td>
            <td>${p.land_use_4 ?? '-'}</td>
          </tr>
        `;
      });

      tableHTML += `</tbody></table>`;
      tableContainer.innerHTML = tableHTML;
      const tableSettings = createSinkTableSettings(sinkType, false);
      $('#' + elId + ' table').DataTable(tableSettings);


      // display card with table
      const tableCardId = sinkType === 'sink' ? 'cardSinkTable' : 'cardEnlargedSinkTable';
      const tableCard = document.getElementById(tableCardId);
      if (selected_sinks !== undefined && selected_sinks.length > 0) {
        selected_sinks.forEach(sinkId => {
          const checked = ids.includes(sinkId) ? true : false;
          const checkbox = document.querySelector(`.sink-select-checkbox[data-type="${sinkType}"][data-id="${sinkId}"]`);
          if (checkbox && checked) {
            checkbox.checked = checked;
            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
          }
        })
      }
      tableCard.classList.remove('d-none');
    
    } else {
      handleAlerts(data.message);
    }
})
.catch(error => console.error("Error fetching data:", error));
};

function getWaterBodies(waterbody, featureGroup){
  let url = 'filter_lakes/';
  if (waterbody === 'streams') {
    url = 'filter_streams/';
  } 
  const project = ToolboxProject.loadFromLocalStorage();
  // project['lakes'] = true;
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(project),
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
    }
  })
  .then(response => response.json())
  .then(data => {
    featureGroup.clearLayers();

    if (data.message.success) {

      data.feature_collection.features.forEach(feature => {
        try {

            let layer = L.geoJSON(feature, {
              style: {
                color: 'purple',
                weight: 2,
                fillOpacity: 0.5
              },
              onEachFeature: function (feature, layer) {
                project.infiltration[`selected_${waterbody}`].push(feature.properties.id);
                let popupContent = `
                   <b>Länge:</b> ${feature.properties.shape_length} m<br>
                   ${feature.properties.shape_area ? `<b>Fläche:</b> ${feature.properties.shape_area} m²<br>` : ''}         
                   <b>Mindestüberschuss:</b> ${feature.properties.min_surplus_volume} m³<br>
                   <b>Durchschnittsüberschuss 1:</b> ${feature.properties.mean_surplus_volume} m³<br>
                   <b>Maximalüberschuss:</b> ${feature.properties.max_surplus_volume} m³<br>
                   <b>Tage mit Überschuss:</b> ${feature.properties.plus_days}<br>
                 `;
                layer.bindTooltip(popupContent);
                layer.on('mouseover', function () {
                  this.openPopup();
                });
              }
            })
            layer.on('contextmenu', function (event) {
                    L.popup()
                        .setLatLng(event.latlng)
                        .setContent(`
                            <b>Sink Options</b><br>
                            
                            <button class="btn btn-outline-secondary select-${waterbody}" ${waterbody}Id=${feature.properties.id}">Select Waterbody</button>
                        `)
                        .openOn(map);
                      });
            layer.addTo(featureGroup);

      //     
      } catch {
        console.log('Error processing feature:', feature.properties.id);
      }
      });
      project.saveToLocalStorage();
  
    }  else {
      handleAlerts(data.message);
    } 
})
.catch(error => console.error("Error fetching data:", error));
}


$('#toolboxPanel').on('change',  function (event) {
  const $target = $(event.target);
  // console.log('change event', $target);
  if ($target.hasClass('double-slider')) {

    const project = ToolboxProject.loadFromLocalStorage();
    const inputName = $target.attr('name');
    const minName = inputName + '_min';
    const maxName = inputName + '_max'; 
    const inputVals = $target.val().split(',');
    project.infiltration[minName] = inputVals[0];
    project.infiltration[maxName] = inputVals[1];
    project.saveToLocalStorage();
  } else if ($target.hasClass('single-slider')) {

    const project = ToolboxProject.loadFromLocalStorage();
    const inputName = $target.attr('name'); 
    const inputVal = $target.val();
    project.infiltration[inputName] = inputVal;
    project.saveToLocalStorage();
  }else if ($target.hasClass('form-check-input')) {
    // checkboxes
    const project = ToolboxProject.loadFromLocalStorage();
    const inputId = $target.attr('id');
    const inputName = $target.attr('name');
    const inputPrefix = $target.attr('prefix');
    const inputValue = $target.attr('value');
    const inputChecked = $target.is(':checked');

    
    const key = `${inputPrefix}_${inputName}`;

  const index = project.infiltration[key].indexOf(inputValue);

  if (index > -1) {
    // Value exists — remove it
    project.infiltration[key] = project.infiltration[key].filter(
      (v) => v !== inputValue
    );
    console.log('Checkbox unchecked:', inputId, '=', inputValue);
  } else {
    // Value does not exist — add it
    project.infiltration[key].push(inputValue);
    console.log('Checkbox checked:', inputId, '=', inputValue);
  }
  project.saveToLocalStorage();

  } else if ($target.hasClass('sink-select-all-checkbox')) {
    const project = ToolboxProject.loadFromLocalStorage();
    const allSelected = $target.is(':checked');
    const sinkType = $target.data('type');
    console.log('sinkType', sinkType);
    
    
    const key = sinkType === 'sink' ? 'selected_sinks' : 'selected_enlarged_sinks';
    if (!allSelected) {
      project.infiltration[key] = [];
    }
    $(`.sink-select-checkbox[data-type="${sinkType}"]`).each(function(){
      const $checkbox = $(this);
      $checkbox.prop('checked', allSelected);
      const sinkId = $checkbox.data('id');
      if (allSelected) {
        console.log("Selected sink:", sinkId);
        project.infiltration[key].push(sinkId);
      } 
    })
    project.saveToLocalStorage();
  } else if ($target.hasClass('sink-select-checkbox')) {
    const sinkType = $target.data('type');
    const key = sinkType === 'sink' ? 'selected_sinks' : 'selected_enlarged_sinks';
    console.log('sinkType', sinkType);
      if ($target.is(':checked')) {
        console.log("Selected sink:", $target.data('id'));
        const project= ToolboxProject.loadFromLocalStorage();
        project.infiltration[key].push($target.data('id'));
        project.saveToLocalStorage();

      } else {
        const sinkId = $target.data('id');
        console.log("Selected sink:", sinkId);
        const project= ToolboxProject.loadFromLocalStorage();
        const index = project.infiltration[key].indexOf(sinkId);
        if (index > -1) {
          project.infiltration[key].splice(index, 1);
        }
        project.saveToLocalStorage();
      }

      // You can trigger your map sink selection logic here
    };
  });

const connectionLayerMap = {};

function addToInletTable(inlet, connectionId) {
  const row = document.createElement('tr');
  row.innerHTML = `
    <td>${inlet.sink_id}</td>
    <td>${inlet.is_enlarged_sink ? 'Ja' : 'Nein'}</td>
    <td>${inlet.waterbody_type} ${inlet.waterbody_id}</td>
    <td>${inlet.length_m}</td>
    <td><button class="btn btn-sm btn-primary" data-id="${connectionId}"">Hide</button></td>
    <td><button class="btn btn-sm btn-primary" data-id="${connectionId}">Zuleitung editieren</button></td>
    <td><button class="btn btn-sm btn-primary" data-id="${connectionId}">Gewässer wählen</button></td>

  `;

  // On row click: update info card
  row.addEventListener('click', () => {
    updateInletInfoCard(inlet);
  });

  document.querySelector('#inlet-table tbody').appendChild(row);
};

function toggleConnection(button) {
  const id = button.getAttribute('data-id');
  const layer = connectionLayerMap[id];

  if (map.hasLayer(layer)) {
    map.removeLayer(layer);
    button.textContent = 'Show';
    button.classList.replace('btn-primary', 'btn-outline-secondary');
  } else {
    layer.addTo(inletConnectionsFeatureGroup);
    button.textContent = 'Hide';
    button.classList.replace('btn-outline-secondary', 'btn-primary');
  }
};

function updateInletInfoCard(inlet) {
  const card = document.getElementById('inlet-info-card');
  card.innerHTML = `
    <div class="card-body">
      <h5 class="card-title">Sink ${inlet.sink_id} ${inlet.is_enlarged_sink ? '(Enlarged)' : ''}</h5>
      <p class="card-text">
        Connected to: ${inlet.waterbody_type} (ID ${inlet.waterbody_id})<br>
        Distance: ${inlet.length_m} meters
      </p>
    </div>
  `;
  card.style.display = 'block';
}


function getInlets() {
    const project = ToolboxProject.loadFromLocalStorage();
    fetch('get_inlets/', {
      method: 'POST',
      body: JSON.stringify(project),
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.message.success) {
        console.log('data', data);
        // handleAlerts(data.message);
;
        data.inlets_sinks.forEach(inlet => {
          console.log('inlet', inlet);

          const connectionId = `${inlet.is_enlarged_sink ? 'enl' : 'sink'}_${inlet.sink_id}_${inlet.waterbody_type}_${inlet.waterbody_id}`;

          // Create sink marker
          const sinkLayer = L.geoJSON(inlet.sink_geom, {
            pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
              radius: 6,
              fillColor: '#ff5722',
              color: '#000',
              weight: 1,
              opacity: 1,
              fillOpacity: 0.8
            })
          });

          // Create line
          const lineLayer = L.geoJSON(inlet.line, {
            style: {
              color: inlet.waterbody_type === 'lake' ? '#007bff' : '#28a745',
              weight: 3,
              dashArray: '4,4'
            }
          });

          // Combine both into a LayerGroup
          const group = L.layerGroup([sinkLayer, lineLayer]).addTo(inletConnectionsFeatureGroup);
          connectionLayerMap[connectionId] = group;

          addToInletTable(inlet, connectionId);  // builds a row in the table




        });
  
        // $('#navInfiltrationResult').removeClass('disabled').addClass('active').trigger('click');
         const resultTab = document.getElementById('navInfiltrationResult');
        resultTab.classList.remove('disabled');
        resultTab.removeAttribute('aria-disabled');

        // Activate the tab using Bootstrap's API
        const tab = new bootstrap.Tab(resultTab);
        tab.show();

        map.removeLayer(sinkFeatureGroup);
        map.removeLayer(enlargedSinkFeatureGroup);
        map.addLayer(streamsFeatureGroup);
        map.addLayer(lakesFeatureGroup);

      } else {
        handleAlerts(data.message);
      }
  });
};


$('#toolboxPanel').on('click', function (event) {
  const $target = $(event.target);
  if ($target.hasClass('toolbox-back-to-initial')) {
    $('#toolboxButtons').removeClass('d-none');
      $('#toolboxPanel').addClass('d-none');
  } else if ($target.attr('id') === 'btnFilterSinks') {
    getSinks('sink', sinkFeatureGroup);
  
  } else if ($target.attr('id') === 'btnFilterEnlargedSinks') {
    getSinks('enlarged_sink', enlargedSinkFeatureGroup);
  
  } else if ($target.attr('id') === 'btnFilterStreams') {
    getWaterBodies('streams', streamsFeatureGroup);
  
  } else if ($target.attr('id') === 'btnFilterLakes') {
    getWaterBodies('lakes', lakesFeatureGroup);
  
  } else if ($target.hasClass('evaluate-selected-sinks')) {
    console.log('ClassList contains  evaluate-selected-sinks');
    const project = ToolboxProject.loadFromLocalStorage();
    calculateIndexForSelection(project)
  } else if ($target.attr('id') === 'btnGetInlets') {
      getInlets(); 
  } else if ($target.attr('id') === 'navInfiltrationSinks') {
      map.addLayer(sinkFeatureGroup);
  } else if ($target.attr('id') === 'navInfiltrationEnlargedSinks') {
      map.addLayer(enlargedSinkFeatureGroup);
  } else if ($target.attr('id') === 'navInfiltrationResult') {
      map.removeLayer(sinkFeatureGroup);
      map.removeLayer(enlargedSinkFeatureGroup);
  } else if ($target.attr('id') === 'toggleSinks') {
    if (map.hasLayer(sinkFeatureGroup)) {
      map.removeLayer(sinkFeatureGroup);
      $target.text('einblenden');
    } else {
        map.addLayer(sinkFeatureGroup);
        $target.text('ausblenden');
    }
  } else if ($target.attr('id') === 'toggleEnlargedSinks') {
    if (map.hasLayer(enlargedSinkFeatureGroup)) {
      map.removeLayer(enlargedSinkFeatureGroup);
      $target.text('einblenden');
    } else {
        map.addLayer(enlargedSinkFeatureGroup);
        $target.text('ausblenden');
    }
  } else if ($target.attr('id') === 'toggleStreams') {
    if (map.hasLayer(streamsFeatureGroup)) {
      map.removeLayer(streamsFeatureGroup);
      $target.text('einblenden');
    } else {
        map.addLayer(streamsFeatureGroup);
        $target.text('ausblenden');
    }
  } else if ($target.attr('id') === 'toggleLakes') {
    if (map.hasLayer(lakesFeatureGroup)) {
      map.removeLayer(lakesFeatureGroup);
      $target.text('einblenden');
    } else {
        map.addLayer(lakesFeatureGroup);
        $target.text('ausblenden');
    }
  }
}); 



function calculateIndexForSelection(project) {
  
  fetch('calculate_index_for_selection/', {
    method: 'POST',
    body: JSON.stringify(project),
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.message.success) {
      console.log('data', data);
      handleAlerts(data.message);
      const sinkTable = $('#sink-table').DataTable();
      const enlargedSinkTable = $('#enlarged_sink-table').DataTable();
      if (Object.keys(data.sinks).length !== 0) {
        let sinkType = 'sink';
        
        sinkTable.column(5).visible(true);
        Object.keys(data.sinks).forEach(key => {
          const sinkId = key;
          console.log(`td[data-id="${sinkId}"][data-type="${sinkType}"].index-total`)
          document.querySelector(`td[data-id="${sinkId}"][data-type="${sinkType}"].index-total`).textContent = `${data.sinks[key].index_total * 100} %`;    
        });
        $('#sink-table').DataTable().destroy();
        const tableSettings = createSinkTableSettings(sinkType, true);
        $('#sink-table').DataTable(tableSettings);

      };
      if (Object.keys(data.enlarged_sinks).length !== 0) {
        let sinkType = 'enlarged_sink';
        enlargedSinkTable.column(5).visible(true);
        Object.keys(data.enlarged_sinks).forEach(key => {
          const sinkId = key;
          document.querySelector(`td[data-id="${sinkId}"][data-type="${sinkType}"].index-total`).textContent = `${data.enlarged_sinks[key].index_total * 100}%`;      
      });
      $('#enlarged_sink-table').DataTable().destroy();
      const tableSettings = createSinkTableSettings(sinkType, true);
        $('#enlarged_sink-table').DataTable(tableSettings);
;
      };
    } else {
      handleAlerts(data.message);
    }
  });
};





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
      initializeSliders();
      $('input[type="checkbox"][name="land_use"]').prop('checked', true);
      $('input[type="checkbox"][name="land_use"]').trigger('change');

      
      const forms = document.querySelectorAll('.weighting-form')
      forms.forEach(form => {
        
        const sliderList = form.querySelectorAll('input.single-slider');
        const length = sliderList.length;
          
        const sliderObj = {};
        let index = 0;
        sliderList.forEach(slider => {
          sliderObj[index] = {
            'val': slider.value,
            'name': slider.name,
            'slider': slider
          };
          index++;
        });
        
        sliderList.forEach(slider => {
          slider.addEventListener('change', function (e) {
            const project = ToolboxProject.loadFromLocalStorage();
            const changedSlider = e.target;
   
            const startIndex = Object.keys(sliderObj).find(
              key => sliderObj[key].slider === changedSlider
            );
            // let changedSlider = sliderObj[startIndex].slider;
            const newVal = parseInt(changedSlider.value);
            let diff = newVal - sliderObj[startIndex].val;
            
            sliderObj[startIndex].val = newVal;
            project.infiltration[changedSlider.name] = sliderObj[startIndex].val;
            console.log("Slider ", startIndex, "new value", newVal, "diff", diff);

            let remainingDiff = diff;
            
            let nextIndex = (parseInt(startIndex) + 1) % length;
            while (remainingDiff !== 0) {

            let sObj = sliderObj[nextIndex];
            let slider = sObj.slider;
            let currentVal = parseInt(slider.value);
            let newVal = currentVal - remainingDiff;
        
            // Clamp between 0 and 100
            if (newVal < 0) {
              remainingDiff = - newVal; 
              newVal = 0;
            } else if (newVal > 100) {
              remainingDiff = newVal - 100;
              newVal = 100;
            } else {
              remainingDiff = 0;
            }
            sObj.val = newVal;
            project.infiltration[sObj.name] = newVal;
            slider.value = newVal;
            slider.dispatchEvent(new Event('input', { bubbles: true }));
        
            nextIndex = (nextIndex + 1) % length;

            if (nextIndex == startIndex) break;
          }
          project.saveToLocalStorage();
          });
        });

        const resetBtn = form.querySelector('input.reset-all');
        resetBtn.addEventListener('click', function (e) {
          let project = ToolboxProject.loadFromLocalStorage();
          // const sliderList = form.querySelectorAll('input.single-slider');
          Object.keys(sliderObj).forEach(idx => {
            sliderObj[idx].slider.value = parseFloat(sliderObj[idx].slider.dataset.defaultValue);
            sliderObj[idx].slider.dispatchEvent(new Event('input'));
            sliderObj[idx].val = parseFloat(sliderObj[idx].slider.dataset.defaultValue);
          });
          project.saveToLocalStorage();
        });

        
        });
    })
    .catch(error => console.error("Error fetching data:", error));
  } else {
    handleAlerts({ success: false, message: 'Please select a user field!' });
  }
  };

$('#infiltrationGo').on('click', () => {
  console.log('Infiltration Go clicked');
  startInfiltration()
});



// let sinksVisible = true;
// let enlargedSinksVisible = true;
// let lakesVisible = true;
// let streamsVisible = true;







getUserFieldsFromDb(featureGroup);

});
