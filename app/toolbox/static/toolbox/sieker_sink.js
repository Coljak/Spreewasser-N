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

const siekerSinkFeatureGroup = new L.FeatureGroup()
siekerSinkFeatureGroup.toolTag = 'sieker-sink';



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
        "targets": 1, // volume
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 2, // area
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 3, // sink_depth
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 4, // avg_depth
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 5, // max_elevation
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 6, // min_elevation
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 7, // urbanarea_percent
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 8, // wetlands_percent 
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 9, // distance_t
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 10, // dist_lake
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 10, //waterdist
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 11, // umsetzbark 
        "orderable": true,
        "searchable": false
      },
    ]
  }
}

function getSiekerSinks(sinkType, featureGroup) {
  let url = 'filter_sieker_sinks/';
  
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
  
    const selected_sinks = project.siekerSink['selected_sinks'];
    if (data.message.success) {
      
      project.siekerSink['selected_sinks'] = [];
      
      // Initialize marker cluster
      let markers = L.markerClusterGroup();
      let ids = [];

      const tableContainer = document.getElementById('sieker-sink-table');

      let tableHTML = ` 
        <table class="table table-bordered table-hover" id="sieker-sink-table">
          <caption>Senke</caption>
          <thead>
            <tr>
              <th><input type="checkbox" class="sink-select-all-checkbox" data-type="sieker-sink">Select all</th>
              <th>Volumen (m³)</th>
              <th>Fläche (m²)</th>
              <th>Tiefe (m)</th>
              <th>Ø Tiefe (m)</th>
              <th>Max. Elevation</th>
              <th>Min. Elevation</th>
              <th>Urbane Fläche (%)</th>
              <th>Fläche Feuchtgebiet (%)</th>
              <th>Distanz t???</th>
              <th>Distanz See</th>
              <th>Distanz Wasser</th>
              <th>Umsetzbarkeit</th>
            </tr>
          </thead>
          <tbody>
      `;
      console.log('data', data);
      const sink_indices = {}
      
      // Iterate through features and add them to the cluster
      data.feature_collection.features.forEach(feature => {

        const p = feature.properties;
        const { id, ...props } = p;
        sink_indices[id] = props;
        
        let coords = feature.coordinates; // Get the lat/lng coordinates
        let latlng = [coords[1], coords[0]]; // Swap for Leaflet format
        // Create popup content with all properties
        
        let popupContent = `
            <b>Volumen:</b> ${p.volume} m³<br>
            <b>Fläche:</b> ${p.area} m²<br>
            <b>Tiefe:</b> ${p.sink_depth} m<br>
            <b>Ø Tiefe:</b> ${p.avg_depth} m<br>
            <b>Max. Elevation:</b> ${p.max_elevation} (m)<br>
            <b>Min. Elevation:</b> ${p.min_elevation} (m)<br>
            <b>Urbane Fläche (%):</b> ${p.urbanarea_percent} (m)<br>
            <b>Fläche Feuchtgebiet (%):</b> ${p.wetlands_percent} (m)<br>
            <b>Distanz t???:</b> ${p.distance_t} (m)<br>
            <b>Distanz See:</b> ${p.dist_lake} (m)<br>
            <b>Distanz Wasser:</tbh> ${p.waterdist} (m)<br>
            <b>Umsetzbarkeit:</b> ${p.umsetzbark}<br>
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
            <td>${p.volume}</td>
            <td>${p.area}</td>
            <td>${p.sink_depth}</td>
            <td>${p.avg_depth}</td>
            <td>${p.max_elevation}</td>
            <td>${p.min_elevation}</td>
            <td>${p.urbanarea_percent}%</td>
            <td>${p.wetlands_percent}%</td>
            <td>${p.distance_t}</td>
            <td>${p.dist_lake}</td>
            <td>${p.waterdist}</td>
            <td>${p.umsetzbark}</td>
          </tr>
        `;
      });
      localStorage.setItem(`sieker_sink_indices`, JSON.stringify(sink_indices));
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

// function getWaterBodies(waterbody, featureGroup){
//   let url = 'filter_lakes/';
//   if (waterbody === 'streams') {
//     url = 'filter_streams/';
//   } 
//   const project = ToolboxProject.loadFromLocalStorage();
//   // project['lakes'] = true;
//   fetch(url, {
//     method: 'POST',
//     body: JSON.stringify(project),
//     headers: {
//         'Content-Type': 'application/json',
//         'X-CSRFToken': getCSRFToken(),
//     }
//   })
//   .then(response => response.json())
//   .then(data => {
//     featureGroup.clearLayers();

//     if (data.message.success) {

//       data.feature_collection.features.forEach(feature => {
//         try {

//             let layer = L.geoJSON(feature, {
//               style: {
//                 color: 'purple',
//                 weight: 2,
//                 fillOpacity: 0.5
//               },
//               onEachFeature: function (feature, layer) {
//                 project.infiltration[`selected_${waterbody}`].push(feature.properties.id);
//                 let popupContent = `
//                   <h6><b> ${feature.properties.name}</b></h6>
//                   <b>Fließgewässer-ID:</b> ${feature.properties.fgw_id}<br>
//                   <b>Länge:</b> ${feature.properties.shape_length} m<br>
//                   ${feature.properties.shape_area ? `<b>Fläche:</b> ${feature.properties.shape_area} m²<br>` : ''}         
//                   <b>Ökologisch bedingter Mindestwasserabfluss:</b> ${feature.properties.minimum_environmental_flow ? `${feature.properties.minimum_environmental_flow} m³/s` : 'unbekannt'}<br>
//                   <b>Mindestüberschuss:</b> ${feature.properties.min_surplus_volume} m³<br>
//                   <b>Durchschnittsüberschuss 1:</b> ${feature.properties.mean_surplus_volume} m³<br>
//                   <b>Maximalüberschuss:</b> ${feature.properties.max_surplus_volume} m³<br>
//                   <b>Tage mit Überschuss:</b> ${feature.properties.plus_days}<br>
//                  `;
//                 layer.bindTooltip(popupContent);
//                 layer.on('mouseover', function () {
//                   this.openPopup();
//                 });
//               }
//             })
//             layer.on('contextmenu', function (event) {
//                     L.popup()
//                         .setLatLng(event.latlng)
//                         .setContent(`
//                             <b>Sink Options</b><br>
                            
//                             <button class="btn btn-outline-secondary select-${waterbody}" ${waterbody}Id=${feature.properties.id}">Select Waterbody</button>
//                         `)
//                         .openOn(map);
//                       });
//             layer.addTo(featureGroup);

//       //     
//       } catch {
//         console.log('Error processing feature:', feature.properties.id);
//       }
//       });
//       project.saveToLocalStorage();
  
//     }  else {
//       handleAlerts(data.message);
//     } 
// })
// .catch(error => console.error("Error fetching data:", error));
// }

// function addToInletTable(inlet, connectionId) {
//   const row = document.createElement('tr');
//   console.log('inlet.rating_connection + inlet.index_sink_total)/2', inlet.rating_connection, inlet.index_sink_total)
//   row.innerHTML = `
//     <td>${inlet.sink_id}</td>
//     <td>${inlet.is_enlarged_sink ? 'Ja' : 'Nein'}</td>
//     <td>${inlet.index_sink_total ?? inlet.index_sink_total}%</td>
//     <td>${inlet.waterbody_type} ${inlet.waterbody_id}: ${inlet.waterbody_name}</td>
//     <td>${inlet.length_m}</td>
//     <td>${inlet.rating_connection ?? inlet.rating_connection}%</td>
//     <td>${((inlet.rating_connection + inlet.index_sink_total)/2)}%</td>
//     <td><button class="btn btn-sm btn-primary result-aquifer-recharge hide-connection" data-id="${connectionId}"">Hide</button></td>
//     <td><button class="btn btn-sm btn-primary result-aquifer-recharge edit-connection" data-id="${connectionId}">Zuleitung editieren</button></td>
//     <td><button class="btn btn-sm btn-primary result-aquifer-recharge choose-waterbody" data-id="${connectionId}">Gewässer wählen</button></td>

//   `;

//   // On row click: update info card
//   row.addEventListener('click', (e) => {
//     updateInletInfoCard(inlet);
//     if (e.target.classList.contains('result-aquifer-recharge')) {
//       if (e.target.classList.contains('hide-connection')) {
//         toggleConnection(e.target);
//       } else if (e.target.classList.contains('edit-connection')) {
//         editConnection(e.target);
//       } else if (e.target.classList.contains('choose-waterbody')) {
//         openUserFieldNameModal({
//           title: 'Gewässer auswählen',
//           buttonText: 'Gewässer auswählen',
//           onSubmit: (userFieldName) => {
//             console.log('Selected user field name:', userFieldName);
//           }
//         });
//       }
//     }
// }   );

//   document.querySelector('#inlet-table tbody').appendChild(row);
// };

// function getInlets() {
//     const project = ToolboxProject.loadFromLocalStorage();
//     fetch('get_inlets/', {
//       method: 'POST',
//       body: JSON.stringify(project),
//       headers: {
//           'Content-Type': 'application/json',
//           'X-CSRFToken': getCSRFToken(),
//       }
//     })
//     .then(response => response.json())
//     .then(data => {
//       if (data.message.success) {
//         console.log('data', data);
//         // handleAlerts(data.message);

//         const enlarged_sink_indices = JSON.parse(localStorage.getItem('enlarged_sink_indices')) || {};
//         const sink_indices = JSON.parse(localStorage.getItem('sink_indices')) || {};
// ;
//         data.inlets_sinks.forEach(inlet => {
//           console.log('inlet', inlet);

//           if (inlet.is_enlarged_sink) {
//             inlet.index_sink_total = enlarged_sink_indices[inlet.sink_id]?.index_total || 0;
//           }
//           else {
//             inlet.index_sink_total = sink_indices[inlet.sink_id]?.index_total || 0;
//           }

//           const connectionId = `${inlet.is_enlarged_sink ? 'enl' : 'sink'}_${inlet.sink_id}_${inlet.waterbody_type}_${inlet.waterbody_id}`;

//           // Create sink marker
//           const sinkLayer = L.geoJSON(inlet.sink_geom, {
//             pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
//               radius: 6,
//               fillColor: '#ff5722',
//               color: '#000',
//               weight: 1,
//               opacity: 1,
//               fillOpacity: 0.8
//             })
//           });

//           // Create line
//           const lineLayer = L.geoJSON(inlet.line, {
//             style: {
//               color: inlet.waterbody_type === 'lake' ? '#007bff' : '#28a745',
//               weight: 3,
//               dashArray: '4,4'
//             }
//           });

//           // Combine both into a LayerGroup
//           const group = L.layerGroup([sinkLayer, lineLayer]).addTo(inletConnectionsFeatureGroup);
//           connectionLayerMap[connectionId] = group;

//           addToInletTable(inlet, connectionId);  // builds a row in the table

//         });
  
//         // $('#navInfiltrationResult').removeClass('disabled').addClass('active').trigger('click');
//          const resultTab = document.getElementById('navInfiltrationResult');
//         resultTab.classList.remove('disabled');
//         resultTab.removeAttribute('aria-disabled');

//         // Activate the tab using Bootstrap's API
//         const tab = new bootstrap.Tab(resultTab);
//         tab.show();

//         map.removeLayer(sinkFeatureGroup);
//         map.removeLayer(enlargedSinkFeatureGroup);
//         map.addLayer(streamsFeatureGroup);
//         map.addLayer(lakesFeatureGroup);

//       } else {
//         handleAlerts(data.message);
//       }
//   });
// };

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

function toggleConnection(button) {
  
  const id = button.getAttribute('data-id');
  const layer = connectionLayerMap[id];
  console.log(toggleConnection, 'id', id, 'layer', layer);

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

export function initializeSiekerSink() {
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag === 'sieker-surface-waters') {
            map.removeLayer(layer);
        }
        });
  console.log('Initialize Infiltraion');
  map.addLayer(siekerSinkFeatureGroup);
  
      
  initializeSliders();
      
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
        project.siekerSink[changedSlider.name] = sliderObj[startIndex].val;
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
        project.siekerSink[sObj.name] = newVal;
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

    $('#toolboxPanel').on('change',  function (event) {
    const $target = $(event.target);
    const project = ToolboxProject.loadFromLocalStorage();
    // console.log('change event', $target);
    if ($target.hasClass('double-slider')) {
      const inputName = $target.attr('name');
      const minName = inputName + '_min';
      const maxName = inputName + '_max'; 
      const inputVals = $target.val().split(',');
      project.siekerSink[minName] = inputVals[0];
      project.siekerSink[maxName] = inputVals[1];
      project.saveToLocalStorage();
    } else if ($target.hasClass('single-slider')) {   
      const inputName = $target.attr('name'); 
      const inputVal = $target.val();
      project.siekerSink[inputName] = inputVal;
      project.saveToLocalStorage();
    }else if ($target.hasClass('form-check-input')) {
      // checkboxes 
      console.log("Checkbox!!")
      const inputId = $target.attr('id');
      console.log("inputId", inputId)
      const inputName = $target.attr('name');
      console.log("inputName", inputName)
      const inputPrefix = $target.attr('prefix');
      console.log("inputPrefix", inputPrefix)
      const inputValue = $target.attr('value');
      console.log("inputValue", inputValue)
      const inputChecked = $target.is(':checked');
      console.log("inputChecked", inputChecked)

      // const key = inputName;
      // console.log("key", key)

      const index = project.siekerSink[inputName].indexOf(inputValue);
      console.log("index", index)

      if (index > -1) {
        // Value exists — remove it
        project.siekerSink[inputName] = project.siekerSink[inputName].filter(
          (v) => v !== inputValue
        );
        console.log('Checkbox unchecked:', inputId, '=', inputValue);
      } else {
        // Value does not exist — add it
        project.siekerSink[inputName].push(inputValue);
        console.log('Checkbox checked:', inputId, '=', inputValue);
      }
      project.saveToLocalStorage();

    } else if ($target.hasClass('sink-select-all-checkbox')) {
      
      const allSelected = $target.is(':checked');
      const sinkType = $target.data('type');
      console.log('sinkType', sinkType);
      
      
      const key = sinkType === 'sink' ? 'selected_sinks' : 'selected_enlarged_sinks';
      if (!allSelected) {
        project.siekerSink[key] = [];
      }
      $(`.sink-select-checkbox[data-type="${sinkType}"]`).each(function(){
        const $checkbox = $(this);
        $checkbox.prop('checked', allSelected);
        const sinkId = $checkbox.data('id');
        if (allSelected) {
          console.log("Selected sink:", sinkId);
          project.siekerSink[key].push(sinkId);
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
          project.siekerSink[key].push($target.data('id'));
          project.saveToLocalStorage();

        } else {
          const sinkId = $target.data('id');
          console.log("Selected sink:", sinkId);
          const project= ToolboxProject.loadFromLocalStorage();
          const index = project.siekerSink[key].indexOf(sinkId);
          if (index > -1) {
            project.siekerSink[key].splice(index, 1);
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
        
    } else if ($target.attr('id') === 'btnFilterSiekerSinks') {
      getSiekerSinks('siekerSink', siekerSinkFeatureGroup);
    
    // } else if ($target.attr('id') === 'btnFilterEnlargedSinks') {
    //   getSinks('enlarged_sink', enlargedSinkFeatureGroup);
    
    // } else if ($target.attr('id') === 'btnFilterStreams') {
    //   getWaterBodies('streams', streamsFeatureGroup);
    
    // } else if ($target.attr('id') === 'btnFilterLakes') {
    //   getWaterBodies('lakes', lakesFeatureGroup);
    
    // } else if ($target.hasClass('evaluate-selected-sinks')) {
    //   console.log('ClassList contains  evaluate-selected-sinks');
    //   const project = ToolboxProject.loadFromLocalStorage();
    //   calculateIndexForSelection(project)
    // } else if ($target.attr('id') === 'btnGetInlets') {
    //     getInlets(); 
    // } else if ($target.attr('id') === 'navInfiltrationSinks') {
    //     map.addLayer(sinkFeatureGroup);
    // } else if ($target.attr('id') === 'navInfiltrationEnlargedSinks') {
    //     map.addLayer(enlargedSinkFeatureGroup);
    // } else if ($target.attr('id') === 'navInfiltrationResult') {
    //     map.removeLayer(sinkFeatureGroup);
    //     map.removeLayer(enlargedSinkFeatureGroup);
    } else if ($target.attr('id') === 'toggleSinks') {
      if (map.hasLayer(siekerSinkFeatureGroup)) {
        map.removeLayer(siekerSinkFeatureGroup);
        $target.text('einblenden');
      } else {
          map.addLayer(siekerSinkFeatureGroup);
          $target.text('ausblenden');
      }
    // } else if ($target.attr('id') === 'toggleEnlargedSinks') {
    //   if (map.hasLayer(enlargedSinkFeatureGroup)) {
    //     map.removeLayer(enlargedSinkFeatureGroup);
    //     $target.text('einblenden');
    //   } else {
    //       map.addLayer(enlargedSinkFeatureGroup);
    //       $target.text('ausblenden');
    //   }
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
    $('#map').on('click', function (event) {
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

  $('input[type="checkbox"][name="land_use"]').prop('checked', true);
  $('input[type="checkbox"][name="land_use"]').trigger('change');


}

