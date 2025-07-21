import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, toolboxSinks, updateDropdown } from '/static/toolbox/toolbox.js';
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

const sinkFeatureGroup = new L.FeatureGroup()
const enlargedSinkFeatureGroup = new L.FeatureGroup()
const lakesFeatureGroup = new L.FeatureGroup()
const streamsFeatureGroup = new L.FeatureGroup()
const inletConnectionsFeatureGroup = L.featureGroup()

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
        "targets": 4, // Volumen Barriere
        "visible": sinkType === 'sink'? false : true, 
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 5, // Zusätzliches Volumen
        "visible": sinkType === 'sink'? false : true, 
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 6, // Eignung Senkenproportionen
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 7, // Bodeneignung 
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 8, // Landnutzung
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 9, // Bodenpunkte
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 10, //Eignungsindex Ertragsverluste/ Feasibility
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 11, // Hydrogeologie
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 12, // Eignungsindex Hydrogeologie<
        "orderable": true,
        "searchable": false
      },
            {
        "targets": 13, // Gesamteignung
        "orderable": true,
        "searchable": false
      }
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
              <th>Volumen Barriere</th>
              <th>Zusätzliches Volumen</th>
              <th>Eignung Senkenproportionen</th>
              <th>Bodeneignung</th>
              <th>Landnutzung</th>
              <th>Bodenpunkte</th>
              <th>Eignung Ertragsverluste</th>
              <th>Hydrogeologie</th>
              <th>Eignung Hydrogeologie</th>
              <th>Gesamteignung Senke</th>
            </tr>
          </thead>
          <tbody>
      `;
      console.log('data', data);
      const sink_indices = {}
      
      // Iterate through features and add them to the cluster
      data.feature_collection.features.forEach(feature => {

        const p = feature.properties;
        ids.push(p.id);
        sink_indices[p.id] = {
          index_sink_total: p.index_sink_total,
          index_soil: p.index_soil,
          index_proportions: p.index_proportions,
          index_feasibility: p.index_feasibility,
          index_hydrogeology: p.index_hydrogeology,
          index_total: p.index_sink_total,
        }



        let coords = feature.coordinates; // Get the lat/lng coordinates
        let latlng = [coords[1], coords[0]]; // Swap for Leaflet format
        // Create popup content with all properties
        
        let popupContent = `
            <b>Tiefe:</b> ${p.depth} m<br>
            <b>Fläche:</b> ${p.area} m²<br>
            <b>Volumen:</b> ${p.volume} m³<br>
            <b>Bodeneignung:</b> ${p.index_soil}%<br>
            ${p.volume_gained ? `<b>Zusätzliches Volumen:</b> ${p.volume_gained}<br>` : ''}
            ${p.volume_construction_barrier ? `<b>Volumen Barriere:</b> ${p.volume_construction_barrier}<br>` : ''}
            <b>Landnuntzung 1:</b> ${p.land_use_1}<br>
            ${p.land_use_2 ? `<b>Landnuntzung 2:</b> ${p.land_use_2}<br>` : ''}
            ${p.land_use_3 ? `<b>Landnuntzung 3:</b> ${p.land_use_3}<br>` : ''}
            ${p.land_use_4 ? `<b>Landnuntzung 4:</b> ${p.land_use_4}<br>` : ''}
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
                  <button class="btn btn-outline-secondary show-sink-outline" data-type="${sinkType}" sinkId=${p.id}">Show Sink Outline</button>
                  <button class="btn btn-outline-secondary select-sink" data-type="${sinkType}" sinkId="${p.id}">Toggle Sink selection</button>
              `)
              .openOn(map);
        });
        markers.addLayer(marker);
          // Add marker to cluster
        
        
        tableHTML += `
          <tr data-sink-id="${p.id}">
            <td><input type="checkbox" class="sink-select-checkbox" data-type=${sinkType} data-id="${p.id}"></td>
            <td>${p.depth}</td>
            <td>${p.area}</td>
            <td>${p.volume}</td>
            <td>${p.volume_construction_barrier ?? '-'}</td>
            <td>${p.volume_gained ?? '-'}</td>
            <td>${p.index_proportions}%</td>
            <td>${p.index_soil ?? '-'}%</td>
            <td>${p.land_use_1}${p.land_use_2 ? `, ${p.land_use_2}`: ''}${p.land_use_3 ? `, ${p.land_use_3}`: ''}${p.land_use_4 ? `, ${p.land_use_4}`: ''}</td>
            <td>${p.soil_points ?? '-'}</td>
            <td>${p.index_feasibility ?? '-'}%</td>
            <td>${p.hydrogeology ?? '-'}</td>
            <td>${p.index_hydrogeology ?? '-'}%</td>
            <td class="index-total" data-type=${sinkType} data-id="${p.id}"><b>${p.index_sink_total ?? '-'}</b></td>
            
            
          </tr>
        `;
      });
      localStorage.setItem(`${sinkType}_indices`, JSON.stringify(sink_indices));
      project.saveToLocalStorage();
      // Add the cluster group to the map
      featureGroup.addLayer(markers);


      // Data Table
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
                  <h6><b> ${feature.properties.name}</b></h6>
                  <b>Fließgewässer-ID:</b> ${feature.properties.fgw_id}<br>
                  <b>Länge:</b> ${feature.properties.shape_length} m<br>
                  ${feature.properties.shape_area ? `<b>Fläche:</b> ${feature.properties.shape_area} m²<br>` : ''}         
                  <b>Ökologisch bedingter Mindestwasserabfluss:</b> ${feature.properties.minimum_environmental_flow ? `${feature.properties.minimum_environmental_flow} m³/s` : 'unbekannt'}<br>
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

function addToInletTable(inlet, connectionId) {
  const row = document.createElement('tr');
  console.log('inlet.rating_connection + inlet.index_sink_total)/2', inlet.rating_connection, inlet.index_sink_total)
  row.innerHTML = `
    <td>${inlet.sink_id}</td>
    <td>${inlet.is_enlarged_sink ? 'Ja' : 'Nein'}</td>
    <td>${inlet.index_sink_total ?? inlet.index_sink_total}%</td>
    <td>${inlet.waterbody_type} ${inlet.waterbody_id}: ${inlet.waterbody_name}</td>
    <td>${inlet.length_m}</td>
    <td>${inlet.rating_connection ?? inlet.rating_connection}%</td>
    <td>${((inlet.rating_connection + inlet.index_sink_total)/2)}%</td>
    <td><button class="btn btn-sm btn-primary result-aquifer-recharge hide-connection" data-id="${connectionId}"">Hide</button></td>
    <td><button class="btn btn-sm btn-primary result-aquifer-recharge edit-connection" data-id="${connectionId}">Zuleitung editieren</button></td>
    <td><button class="btn btn-sm btn-primary result-aquifer-recharge choose-waterbody" data-id="${connectionId}">Gewässer wählen</button></td>

  `;

  // On row click: update info card
  row.addEventListener('click', (e) => {
    updateInletInfoCard(inlet);
    if (e.target.classList.contains('result-aquifer-recharge')) {
      if (e.target.classList.contains('hide-connection')) {
        toggleConnection(e.target);
      } else if (e.target.classList.contains('edit-connection')) {
        editConnection(e.target);
      } else if (e.target.classList.contains('choose-waterbody')) {
        openUserFieldNameModal({
          title: 'Gewässer auswählen',
          buttonText: 'Gewässer auswählen',
          onSubmit: (userFieldName) => {
            console.log('Selected user field name:', userFieldName);
          }
        });
      }
    }
}   );

  document.querySelector('#inlet-table tbody').appendChild(row);
};

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

        const enlarged_sink_indices = JSON.parse(localStorage.getItem('enlarged_sink_indices')) || {};
        const sink_indices = JSON.parse(localStorage.getItem('sink_indices')) || {};
;
        data.inlets_sinks.forEach(inlet => {
          console.log('inlet', inlet);

          if (inlet.is_enlarged_sink) {
            inlet.index_sink_total = enlarged_sink_indices[inlet.sink_id]?.index_total || 0;
          }
          else {
            inlet.index_sink_total = sink_indices[inlet.sink_id]?.index_total || 0;
          }

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

function updateInletInfoCard(inlet) {
  const card = document.getElementById('inlet-info-card');
  card.innerHTML = `
    <div class="row">
      <div class="card-body col-6">
        <h5 class="card-title">Sink ${inlet.sink_id} ${inlet.is_enlarged_sink ? '(Enlarged)' : ''}</h5>
        <p class="card-text">
          Connected to: ${inlet.waterbody_type} (ID ${inlet.waterbody_id})<br>
          Distance: ${inlet.length_m} meters
        </p>
      </div>
      <div class="card-body col-6">
        <h5 class="card-title">Tägliches Anreicherungsvolumen </h5>
        <img src="/static/toolbox/anreicherung.jpg" alt="Inlet" class="img-fluid rounded" style="max-height: 500px;" />
      </div>
    </div>
  `;
  card.style.display = 'block';
}



const connectionLayerMap = {};
function toggleConnection(button) {
  const id = button.getAttribute('data-id');
  const layer = connectionLayerMap[id];

  if (!layer) {
    console.warn(`No layer found for connectionId: ${id}`);
    return;
  }

  if (map.hasLayer(layer)) {
    map.removeLayer(layer);
    button.textContent = 'Show';
    button.classList.replace('btn-primary', 'btn-outline-secondary');
  } else {
    console.log('Trying to show layer again...');
    console.log('Map has layer already?', map.hasLayer(layer));
    
    // TODO : this is not correct!!! The layer needs to be added to the inletConnectionsFeatureGroup, not directly to the map
    layer.addTo(map);
    // inletConnectionsFeatureGroup.addLayer(layer);  // ← correct way to add
    // if (!map.hasLayer(inletConnectionsFeatureGroup)) {
    //   map.addLayer(inletConnectionsFeatureGroup);
    // }
    button.textContent = 'Hide';
    button.classList.replace('btn-outline-secondary', 'btn-primary');
  }
}

function initializeInfiltration() {
  console.log('Initialize Infiltraion');
  map.addLayer(sinkFeatureGroup);
  map.addLayer(enlargedSinkFeatureGroup);
  map.addLayer(lakesFeatureGroup);
  map.addLayer(streamsFeatureGroup);
  map.addLayer(inletConnectionsFeatureGroup);


  $('#toolboxPanel').on('change',  function (event) {
    const $target = $(event.target);
    const project = ToolboxProject.loadFromLocalStorage();
    // console.log('change event', $target);
    if ($target.hasClass('double-slider')) {
      const inputName = $target.attr('name');
      const minName = inputName + '_min';
      const maxName = inputName + '_max'; 
      const inputVals = $target.val().split(',');
      project.infiltration[minName] = inputVals[0];
      project.infiltration[maxName] = inputVals[1];
      project.saveToLocalStorage();
    } else if ($target.hasClass('single-slider')) {   
      const inputName = $target.attr('name'); 
      const inputVal = $target.val();
      project.infiltration[inputName] = inputVal;
      project.saveToLocalStorage();
    }else if ($target.hasClass('form-check-input')) {
      // checkboxes 
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
    
    // } else if ($target.hasClass('evaluate-selected-sinks')) {
    //   console.log('ClassList contains  evaluate-selected-sinks');
    //   const project = ToolboxProject.loadFromLocalStorage();
    //   calculateIndexForSelection(project)
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

  // TODO I tttttttttthink      this is not working!
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

}

initializeInfiltration();