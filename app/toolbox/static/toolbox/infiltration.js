import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { updateDropdown, addLegend, addChangeEventListener, addFeatureCollectionToTable, tableCheckSelectedItems, addClickEventListenerToToolboxPanel, addPointFeatureCollectionToLayer, addFeatureCollectionToLayer, loadProjectToGui } from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  openUserFieldNameModal,
  removeLegendFromMap,
} from '/static/shared/map_sidebar_utils.js';
import {Infiltration} from '/static/toolbox/infiltration_model.js';
import { Layers } from '/static/toolbox/layers.js';


const legendSettings = {
    'header': 'Senkeneignung',
    'grades': [1, 0.75, 0.5, 0.25, 0],
    'gradientLabels': [' 100%', ' 75%', ' 50%', ' 25%', ' 0%']
} 


//TODO: this is not pretty
const connectionLayerMap = {};


function filterSinks(sinkType) {
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
     


      console.log('data', data);
      const sink_indices = {}
      

      addPointFeatureCollectionToLayer(data);

      addFeatureCollectionToTable(data)
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


function getWaterBodies(dataType){
  
  let url = `filter_waterbodies/`;

  const infiltration = Infiltration.loadFromLocalStorage();

  fetch(url, {
    method: 'POST',
    body: JSON.stringify({
      dataType: dataType,
      project: infiltration}),
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
    }
  })
  .then(response => response.json())
  .then(data => {
    console.log('data', data)
    if (data.message.success) {
      addFeatureCollectionToLayer(data)
      addFeatureCollectionToTable(data)
    }  else {
      handleAlerts(data.message);
    } 
  })
  .catch(error => console.error("Error fetching data:", error));
};

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
    

  `;

  // On row click: update info card
  row.addEventListener('click', (e) => {
    updateInletInfoCard(inlet);
    if (e.target.classList.contains('result-aquifer-recharge')) {
      if (e.target.classList.contains('hide-connection')) {
        toggleConnection(e.target);
      } else if (e.target.classList.contains('edit-connection')) {
        editConnection(e.target);
      // } else if (e.target.classList.contains('choose-waterbody')) {
      //   openUserFieldNameModal({
      //     title: 'Gewässer auswählen',
      //     buttonText: 'Gewässer auswählen',
      //     onSubmit: (userFieldName) => {
      //       console.log('Selected user field name:', userFieldName);
      //     }
      //   });
      }
    }
}   );

  document.querySelector('#inlet-table tbody').appendChild(row);
};

function getInfiltrationResults() {
    const infiltration = Infiltration.loadFromLocalStorage();
    fetch('get_infiltration_results/', {
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
          const group = L.layerGroup([sinkLayer, lineLayer]).addTo(Layers.inletConnectionsFeatureGroup);
          
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
        
        map.addLayer(Layers.inletConnectionsFeatureGroup)
        map.removeLayer(Layers.sink);
        map.removeLayer(Layers.enlarged_sink);
        map.addLayer(Layers.stream);
        map.addLayer(Layers.lake);

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
        <button class="btn btn-primary show-injection-result-chart" data-waterbody-type="${inlet.waterbody_type}" data-waterbody-id="${inlet.waterbody_id}">Anreicherungsvolumen anzeigen</button>
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

  if (Layers.inletConnectionsFeatureGroup.hasLayer(layer)) {
    Layers.inletConnectionsFeatureGroup.removeLayer(layer);
    button.textContent = 'Show';
    button.classList.replace('btn-primary', 'btn-outline-secondary');
  } else {
    console.log('Trying to show layer again...');
    console.log('Map has layer already?', map.hasLayer(layer));
    
    // TODO : this is not correct!!! The layer needs to be added to the inletConnectionsFeatureGroup, not directly to the map
    layer.addTo(Layers.inletConnectionsFeatureGroup);
    // inletConnectionsFeatureGroup.addLayer(layer);  // ← correct way to add
    // if (!map.hasLayer(inletConnectionsFeatureGroup)) {
    //   map.addLayer(inletConnectionsFeatureGroup);
    // }
    button.textContent = 'Hide';
    button.classList.replace('btn-outline-secondary', 'btn-primary');
  }
}

export function initializeInfiltration() {

  
  
  
  
  removeLegendFromMap(map);
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag && layer.toolTag !== 'infiltration') {
            map.removeLayer(layer);
        }
      });
  console.log('Initialize Infiltraion');

      
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
      const infiltration = Infiltration.loadFromLocalStorage(); // TODO this is not needed but check
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
    $('#toolboxPanel').off('click');
    addClickEventListenerToToolboxPanel(Infiltration)
    $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.attr('id') === 'btnFilterSinks') {
      filterSinks('sink');
    
    } else if ($target.attr('id') === 'btnFilterEnlargedSinks') {
      filterSinks('enlarged_sink');
    
    } else if ($target.attr('id') === 'btnFilterStreams') {
      getWaterBodies('stream');
    
    } else if ($target.attr('id') === 'btnFilterLakes') {
      getWaterBodies('lake');

    } else if ($target.attr('id') === 'btnGetInfiltrationResults') {
        getInfiltrationResults(); 
    } else if ($target.attr('id') === 'navInfiltrationSinks') {
        map.addLayer(Layers.sink);
    } else if ($target.attr('id') === 'navInfiltrationEnlargedSinks') {
        map.addLayer(Layers.enlarged_sink);
    } else if ($target.attr('id') === 'navInfiltrationResult') {
        map.removeLayer(Layers.sink);
        map.removeLayer(Layers.enlarged_sink);
    } else if ($target.hasClass('show-injection-result-chart')) {
        const waterbodyType = $target.data('waterbody-type');
        const waterbodyId = $target.data('waterbody-id');
        console.log('Show injection chart for', waterbodyType, waterbodyId);
        fetch(`get_injection_volume_chart/${waterbodyType}/${waterbodyId}/`)
        .then(response => response.json())
        .then(data => {
            console.log('Chart data', data);
            const chartData = data.chart_data;
            // Render chart in the canvas
            const ctx = document.getElementById('inletVolumeChart').getContext('2d');
            // if (window.inletVolumeChart) {
            //     window.inletVolumeChart.destroy();
            // }
            const deLocale = dateFns.locale?.de;
            
            // new Chart(ctx, {
            //   type: 'bar',
            //   data: {
            //     datasets: [{
            //       label: 'Abfluss (m³/s)',
            //       data: chartData, // expects [{x: date, y: value}]
            //       borderWidth: 0,
            //       backgroundColor: 'rgba(54, 162, 235, 0.6)',
            //     }]
            //   },
            //   options: {
            //     responsive: true,
            //     parsing: false, // we already have x/y format
            //     scales: {
            //       x: {
            //         type: 'time',
            //         time: {
            //           unit: 'month', // 'day' | 'month' | 'year'
            //           displayFormats: {
            //             day: 'dd-MM-yyyy',
            //             month: 'MM-yyyy',
            //             year: 'yyyy',
            //           },
            //         },
            //         adapters: {
            //           date: { locale: deLocale },
            //         },
            //         title: {
            //           display: true,
            //           text: 'Datum'
            //         }
            //       },
            //       y: {
            //         title: {
            //           display: true,
            //           text: 'Abfluss (m³/s)'
            //         },
            //         beginAtZero: true
            //       }
            //     },
            //     plugins: {
            //       legend: { display: true },
            //       tooltip: {
            //         callbacks: {
            //           label: ctx => `${ctx.formattedValue} m³/s`,
            //         }
            //       }
            //     }
            //   }

            // })

            new Chart(ctx, {
              type: 'bar',
              data: { datasets: [{ label: 'Abfluss (m³/s)', data: chartData }] },
              options: {
                scales: {
                  x: {
                    type: 'time',
                    adapters: { date: { locale: deLocale } },
                    time: { unit: 'month', displayFormats: { month: 'MM-yyyy' } }
                  }
                }
              }
            })
            .catch(err => console.error('Chart data error:', err));

        });
    }
    }); 

  $('input[type="checkbox"][name="land_use"]').prop('checked', true);
  $('input[type="checkbox"][name="land_use"]').trigger('change');

  const infiltration = Infiltration.loadFromLocalStorage();
  loadProjectToGui(infiltration)


}

