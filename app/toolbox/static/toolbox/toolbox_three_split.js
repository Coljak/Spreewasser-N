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

  //   const project = ToolboxProject.loadFromLocalStorage();
  //   let selectedSinks = project.infiltration[sinkType + '_selected'];
  //   if (selectedSinks.includes(sinkId)) {
      
  //     selectedSinks = selectedSinks.filter(id => id !== sinkId);
  //     project.infiltration[sinkType + '_selected'] = selectedSinks;
      
  //     console.log("Sink already selected:", sinkId);
  //   } else {
  //     console.log("Selected sink:", sinkId);
      
  //     selectedSinks.push(sinkId);
      
  //   } 
  //   project.saveToLocalStorage();
    
  // }


function selectSinkPopup(sinkId, sinkType) {
}

const showSinkOutline = function (sinkId) {
  const project = ToolboxProject.loadFromLocalStorage();
  console.log('project', project);
  console.log('showSinkOutline sinkId', sinkId);
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
    if (data.message.success) {

      // Initialize marker cluster
      let markers = L.markerClusterGroup();
      // project[sinkType] = data.feature_collection;
      project.saveToLocalStorage();
      // Iterate through features and add them to the cluster
      data.feature_collection.features.forEach(feature => {
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
              <th>Bodeneignung</th>
              <th class="hide-for-enlarged-sink">Volumen Barriere</th>
              <th class="hide-for-enlarged-sink">Zusätzliches Volumen</th>
              <th>Landnutzung 1</th>
              <th>Landnutzung 2</th>
              <th>Landnutzung 3</th>
              <th class="hide-for-enlarged-sink">Landnutzung 4</th>
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
            <td class="hide-for-enlarged-sink">${p.volume_construction_barrier ?? '-'}</td>
            <td class="hide-for-enlarged-sink">${p.volume_gained ?? '-'}</td>
            <td>${p.land_use_1 ?? '-'}</td>
            <td>${p.land_use_2 ?? '-'}</td>
            <td>${p.land_use_3 ?? '-'}</td>
            <td class="hide-for-enlarged-sink">${p.land_use_4 ?? '-'}</td>
          </tr>
        `;
      });

      tableHTML += `</tbody></table>`;
      tableContainer.innerHTML = tableHTML;

      $('#' + elId + ' table').DataTable(
        {
          "order": [[1, "asc"]],
          "searching": false,
          "columnDefs": [
            {
              "targets": 0,
              "orderable": false,
              "searchable": false
            },
            {
              "targets": 1,
              "orderable": true,
              "searchable": false
            },
            {
              "targets": 2,
              "orderable": true,
              "searchable": false
            },
            {
              "targets": 3,
              "orderable": true,
              "searchable": false
            },
            {
              "targets": 4,
              "orderable": true,
              "searchable": false
            },
            {
              "targets": 5,
              "visible": sinkType === 'sink'? false : true,
              "orderable": true,
              "searchable": false
            },
            {
              "targets": 6,
              "visible": sinkType === 'sink'? false : true,
              "orderable": true,
              "searchable": false
            },
            {
              "targets": 7,
              "orderable": true,
              "searchable": false
            },
            {
              "targets": 8,
              "orderable": true,
              "searchable": false
            },
            {
              "targets": 9,
              "orderable": true,
              "searchable": false
            },
            {
              "targets": 10,
              "visible": sinkType === 'sink'? false : true,
              "orderable": true,
              "searchable": false
            }
          ]
        }
      );
      if (sinkType === 'sink') {
        const tableColumns = document.querySelectorAll('hide-for-enlarged-sink');
        tableColumns.forEach(col => {
          col.style.display = 'none';
        });
      };
      

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
      // Initialize marker cluster
      // let markers = L.markerClusterGroup();
      project[waterbody] = data.feature_collection;
      project.saveToLocalStorage();
      console.log(data.feature_collection.features.length)
      data.feature_collection.features.forEach(feature => {
        try {
          // let coords = feature.properties.centroid; // Get the lat/lng coordinates
          // let latlng = [coords[1], coords[0]]; // Swap for Leaflet format
            let layer = L.geoJSON(feature, {
              style: {
                color: 'purple',
                weight: 2,
                fillOpacity: 0.5
              },
              onEachFeature: function (feature, layer) {
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

      // Add the cluster group to the map
      // featureGroup.addLayer(markers);
      // map.fitBounds(featureGroup.getBounds());    
    }  else {
      handleAlerts(data.message);
    } 
})
.catch(error => console.error("Error fetching data:", error));
}


$('#toolboxPanel').on('change',  function (event) {
  const $target = $(event.target);
  console.log('change event', $target);
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

    if (inputChecked) {
      project.infiltration[key].push(inputValue);
    } else {
      project.infiltration[key].pop(inputValue);
    }
    project.saveToLocalStorage();
    console.log('Updated infiltration', inputId, '=', inputValue);

  } else if ($target.hasClass('sink-select-all-checkbox')) {
    const project = ToolboxProject.loadFromLocalStorage();
    const allSelected = $target.is(':checked');
    const sinkType = $target.data('type');
    console.log('sinkType', sinkType);
    
    
    const key = sinkType === 'sink' ? 'sink_selected' : 'enlarged_sink_selected';
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
    const key = sinkType === 'sink' ? 'sink_selected' : 'enlarged_sink_selected';
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


$('#toolboxPanel').on('click', function (event) {
  const $target = $(event.target);
  if ($target.attr('id') === 'btnFilterSinks') {
    getSinks('sink', sinkFeatureGroup);
  
  } else if ($target.attr('id') === 'btnFilterEnlargedSinks') {
    getSinks('enlarged_sink', enlargedSinkFeatureGroup);
  
  } else if ($target.attr('id') === 'btnFilterStreams') {
    getWaterBodies('streams', streamsFeatureGroup);
  
  } else if ($target.attr('id') === 'btnFilterLakes') {
    getWaterBodies('lakes', lakesFeatureGroup);
  
  } 
}) 


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
        $('input[type="checkbox"][name="land_use"]').prop('checked', true);
        $('input[type="checkbox"][name="land_use"]').trigger('change');
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
