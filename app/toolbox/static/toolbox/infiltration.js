import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { updateDropdown, addChangeEventListener, addFeatureCollectionToTable, tableCheckSelectedItems, addClickEventListenerToToolboxPanel, addPointFeatureCollectionToLayer } from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
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
  removeLegendFromMap,
} from '/static/shared/map_sidebar_utils.js';
import {Infiltration} from '/static/toolbox/infiltration_model.js';
import { Layers } from '/static/toolbox/layers.js';



const sinkFeatureGroup = Layers.sink

const enlargedSinkFeatureGroup = Layers.enlarged_sink

const lakesFeatureGroup = new L.FeatureGroup()
lakesFeatureGroup.toolTag = 'infiltration';
const streamsFeatureGroup = new L.FeatureGroup()
streamsFeatureGroup.toolTag = 'infiltration';
const inletConnectionsFeatureGroup = new L.featureGroup()
inletConnectionsFeatureGroup.toolTag = 'infiltration';
let sinkMarkers = L.markerClusterGroup();
sinkMarkers.toolTag = 'infiltration';

//TODO: this is not pretty
const connectionLayerMap = {};


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
};

function getSinks(sinkType) {
  const featureGroup = Layers[sinkType]
  let url = `filter_${sinkType}s/`;
 
  const infiltration = Infiltration.loadFromLocalStorage();
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(infiltration),
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
    }
  })
  .then(response => response.json())
  .then(data => {
    featureGroup.clearLayers();
    
    if (data.message.success) {
      const selected_sinks = infiltration[`selected_${sinkType}s`];
      infiltration[`selected_${sinkType}s`] = [];
      
      // Initialize marker cluster
      let markers = L.markerClusterGroup();

      const elId = sinkType === 'sink' ? 'sink-table-container' : 'enlarged_sink-table-container';  



      console.log('data', data);
      const sink_indices = {}
      

      addPointFeatureCollectionToLayer(
        {
          featureCollection: data.feature_collection, 
          dataInfo: data.dataInfo, 
          featureGroup: featureGroup,
          colorByIndex: 'index_sink_total',
          // markerCluster: sinkMarkers, 
          selectable: true
        })

      addFeatureCollectionToTable(Infiltration, data.feature_collection, data.dataInfo)
      infiltration[`selected_${sinkType}s`] = selected_sinks.filter(sink => infiltration[`all_${sinkType}_ids`].includes(sink));
      localStorage.setItem(`${sinkType}_indices`, JSON.stringify(sink_indices));
      // infiltration.saveToLocalStorage();
      // Add the cluster group to the map
      // featureGroup.addLayer(markers);

    
    } else {
      handleAlerts(data.message);
      return;
    }
    return {'infiltration': infiltration, sinkType: sinkType}
}).then(data => {
  tableCheckSelectedItems(data.infiltration, data.sinkType)
})
.catch(error => console.error("Error fetching data:", error));
};



function getWaterBodies(waterbody, featureGroup){
  let url = 'filter_lakes/';
  if (waterbody === 'streams') {
    url = 'filter_streams/';
  } 
  const infiltration = Infiltration.loadFromLocalStorage();
  // infiltration['lakes'] = true;
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(infiltration),
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
                infiltration[`selected_${waterbody}`].push(feature.properties.id);
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
      infiltration.saveToLocalStorage();
  
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
    <td>${inlet.waterbody_type} ${inlet.waterbody_id}: ${inlet.waterbody_name}</td>
    <td>${inlet.length_m}</td>
    <td>${inlet.rating_connection ?? inlet.rating_connection}%</td>
    <td>${inlet.index_sink_total ?? inlet.index_sink_total}%</td>
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
    const infiltration = Infiltration.loadFromLocalStorage();
    fetch('get_inlets/', {
      method: 'POST',
      body: JSON.stringify(infiltration),
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

export function initializeInfiltration(userField) {

  const infiltration = new Infiltration();
  infiltration.userField = userField;
  infiltration.saveToLocalStorage();
  
  removeLegendFromMap(map);
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag && layer.toolTag !== 'infiltration') {
            map.removeLayer(layer);
        }
      });
  console.log('Initialize Infiltraion');
  map.addLayer(sinkFeatureGroup);
  map.addLayer(enlargedSinkFeatureGroup);
  map.addLayer(lakesFeatureGroup);
  map.addLayer(streamsFeatureGroup);
  map.addLayer(inletConnectionsFeatureGroup);
      
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
        const infiltration = Infiltration.loadFromLocalStorage();
        console.log('infiltration from initialize sliders', infiltration)
        const changedSlider = e.target;

        const startIndex = Object.keys(sliderObj).find(
          key => sliderObj[key].slider === changedSlider
        );
        // let changedSlider = sliderObj[startIndex].slider;
        const newVal = parseInt(changedSlider.value);
        let diff = newVal - sliderObj[startIndex].val;
        
        sliderObj[startIndex].val = newVal;
        infiltration[changedSlider.name] = sliderObj[startIndex].val;
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
        infiltration[sObj.name] = newVal;
        slider.value = newVal;
        slider.dispatchEvent(new Event('input', { bubbles: true }));
    
        nextIndex = (nextIndex + 1) % length;

        if (nextIndex == startIndex) break;
      }
      infiltration.saveToLocalStorage();
      });
    });

    const resetBtn = form.querySelector('input.reset-all');
    resetBtn.addEventListener('click', function (e) {
      let infiltration = Infiltration.loadFromLocalStorage();
      // const sliderList = form.querySelectorAll('input.single-slider');
      Object.keys(sliderObj).forEach(idx => {
        sliderObj[idx].slider.value = parseFloat(sliderObj[idx].slider.dataset.defaultValue);
        sliderObj[idx].slider.dispatchEvent(new Event('input'));
        sliderObj[idx].val = parseFloat(sliderObj[idx].slider.dataset.defaultValue);
      });
      infiltration.saveToLocalStorage();
    });

    
    });

    $('#toolboxPanel').off('change'); // Remove any previous change event handlers
    addChangeEventListener(Infiltration);
    
    addClickEventListenerToToolboxPanel(Infiltration)
    $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.attr('id') === 'btnFilterSinks') {
      getSinks('sink');
    
    } else if ($target.attr('id') === 'btnFilterEnlargedSinks') {
      getSinks('enlarged_sink');
    
    } else if ($target.attr('id') === 'btnFilterStreams') {
      getWaterBodies('streams', streamsFeatureGroup);
    
    } else if ($target.attr('id') === 'btnFilterLakes') {
      getWaterBodies('lakes', lakesFeatureGroup);

    } else if ($target.attr('id') === 'btnGetInlets') {
        getInlets(); 
    } else if ($target.attr('id') === 'navInfiltrationSinks') {
        map.addLayer(sinkFeatureGroup);
    } else if ($target.attr('id') === 'navInfiltrationEnlargedSinks') {
        map.addLayer(enlargedSinkFeatureGroup);
    } else if ($target.attr('id') === 'navInfiltrationResult') {
        map.removeLayer(sinkFeatureGroup);
        map.removeLayer(enlargedSinkFeatureGroup);

    } else if ($target.hasClass('toggle-feature-group')) {
      console.log('toggle-feature-group')
      const dataType = $target.attr('data-type')
      if (dataType === 'sink') {
        if (map.hasLayer(Layers[dataType])) {
        map.removeLayer(Layers[dataType]);
        $target.text('einblenden');
      } else {
          map.addLayer(Layers[dataType]);
          $target.text('ausblenden');
      }
      } else
      {if (map.hasLayer(enlargedSinkFeatureGroup)) {
        map.removeLayer(enlargedSinkFeatureGroup);
        $target.text('einblenden');
      } else {
          map.addLayer(enlargedSinkFeatureGroup);
          $target.text('ausblenden');
      }}
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



  $('input[type="checkbox"][name="land_use"]').prop('checked', true);
  $('input[type="checkbox"][name="land_use"]').trigger('change');


}

