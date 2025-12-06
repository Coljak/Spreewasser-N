import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown, getBsColor } from '/static/shared/utils.js';
import { 
  updateDropdown, 
  addChangeEventListener, 
  addClickEventListenerToToolboxPanel,  
  tableCheckSelectedItems, 
  addFeatureCollectionToTable, 
  addFeatureCollectionToLayer, 
  loadProjectToGui,
  createSinkResultTable, 
} from '/static/toolbox/toolbox.js';
import { ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { SiekerWetland } from '/static/toolbox/sieker_wetland_model.js';
import {Layers} from '/static/toolbox/layers.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import {  
  map, 
  
} from '/static/shared/map_sidebar_utils.js';


function filterSiekerWetlands(project) {
  
  fetch('filter_sieker_wetlands/', {
    method: 'POST',
    body: JSON.stringify(project),
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    }
  }).then(
    response => response.json()
  ).then(data => {
    
    console.log(data)
    if(data.message.success) {
      Layers['wetland'].clearLayers();
 
      addFeatureCollectionToLayer({featureCollection: data.featureCollection, dataInfo: data.dataInfo}, true);
      addFeatureCollectionToTable({featureCollection: data.featureCollection, dataInfo: data.dataInfo});
    } else {
      handleAlerts(data.message);
      clearAndRemoveTable(SiekerWetland, 'wetland', data.message.message)
    }

  })
  .then(() => tableCheckSelectedItems(project, 'wetland'));
};

function getSiekerWetlandResults() {
  let url = 'get_sieker_wetland_results/'
  const project = SiekerWetland.loadFromLocalStorage();
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
    if (data.message.success) {
      console.log('getSiekerWetlandResult data', data);  
      Layers['wetland_result'].clearLayers();

      let resultMap = addFeatureCollectionToLayer({dataInfo: data.inlet_data_info, featureCollection: data.inlet_feature_collection}, true)
      resultMap = addFeatureCollectionToLayer({dataInfo: data.wetland_data_info, featureCollection: data.sink_feature_collection}, false, resultMap)
      console.log('Result Map: ', resultMap)
    
      createSinkResultTable({
          dataInfo: data.result_data_info, 
          inlets: data.results,
          inletDataInfo: data.inlet_data_info,
          waterbodyDataInfo: {
            'lake': data.lake_data_info, 
            'stream': data.stream_data_info
          },
          sinkDataInfo: {
            'sink': data.wetland_data_info,   

          },
        });

      $('#toolboxPanel').on('change', '.toggle-sink-result', function () {
              const inletId = $(this).attr('inlet-id');
              const sinkId  = $(this).attr('sink-id');
             
              const show    = $(this).is(':checked');

              // Direct map lookup - FAST and CLEAN
              const inletLayer = resultMap[inletId];
              const sinkLayer  = resultMap[sinkId];

              if (inletLayer) {
                  show ? map.addLayer(inletLayer) : map.removeLayer(inletLayer);
              }
              if (sinkLayer) {
                  show ? map.addLayer(sinkLayer) : map.removeLayer(sinkLayer);
              }
              
          });

        $('#toolboxPanel').on('change', '.table-select-all.switch-input', function () {
             
              const show    = $(this).is(':checked');
              if (show) {
                Object.keys(resultMap).forEach(key => {
                  map.addLayer(resultMap[key]);
                }) 
              } else {
                Object.keys(resultMap).forEach(key => {
                  map.removeLayer(resultMap[key]);
                })
              } 
  
              
          });
    

      const resultTab = document.getElementById('navSiekerWetlandsResult');
      resultTab.classList.remove('disabled');
      resultTab.removeAttribute('aria-disabled');
      const tab = new bootstrap.Tab(resultTab);
      tab.show();

      map.removeLayer(Layers.wetland);
      map.addLayer(Layers.wetland_lake);
      map.addLayer(Layers.wetland_stream);

    } else {

      handleAlerts(data.message);
      
      clearAndRemoveTable(SiekerWetland, dataType, data.message.message)
    }
})
.catch(error => console.error("Error fetching data:", error));
};


export function initializeSiekerWetland(data) {


  $('#toolboxPanel').off('change');
  $('#toolboxPanel').off('click');

    initializeSliders();

  // This is only for the priority slider that has string labels not numbers
  const slider = document.getElementById('wetland_feasibility_slider');
  const sliderLabelLeft = document.getElementById('wetland_feasibility_start_text');
  const sliderLabelRight = document.getElementById('wetland_feasibility_value');
  const sliderLabels = data['sliderLabels'];
  sliderLabelLeft.innerText = sliderLabels[Math.min(...Object.keys(sliderLabels).map(Number))];
  sliderLabelRight.innerText = sliderLabels[Math.max(...Object.keys(sliderLabels).map(Number))];

  if (slider && sliderLabels) {
    slider.addEventListener('change', function() {
      console.log('sliderChanged', slider.value);
      if (slider.value in sliderLabels) {
        sliderLabelLeft.innerText = sliderLabels[slider.value];
      }
    });
  }

  addChangeEventListener(SiekerWetland);
  addClickEventListenerToToolboxPanel(SiekerWetland)
  
  addFeatureCollectionToLayer({featureCollection: data.featureCollection, dataInfo: data.dataInfo}, true)
  addFeatureCollectionToTable({featureCollection: data.featureCollection, dataInfo: data.dataInfo})
  

  $('#cardSiekerWetlandTable').removeClass('d-none');
  

  $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
  if ($target.attr('id') === 'btnFilterSiekerWetlands') {
      const project = SiekerWetland.loadFromLocalStorage();
      if (project.selected_wetlands.length === 0) {
        handleAlerts({'success': false, 'message': 'Bitte wählen Sie Gewässer aus!'})
      } else {
        map.removeLayer(Layers['wetland']);
        // map.addLayer(Layers['filtered_wetland']);
        filterSiekerWetlands(project);
      }
      return;  

    } else if ($target.attr('id') === 'btnGetSiekerWetlandResults') {
      getSiekerWetlandResults();
      return;
    }
  });

  $('#navSiekerWetland').on('shown.bs.tab', function (event) {
    const targetPane = $($(event.target).attr('href')); 
    if (targetPane.hasClass('active')) {
      map.addLayer(Layers['wetland']);
    }
  });



  function selectWetland(event) {
    if (event.target.classList.contains('select-wetland')) {
      const wetlandId = event.target.getAttribute('wetlandId');
      const wetlandType = event.target.getAttribute('data-type');
      console.log('wetlandId', wetlandId);
      console.log('wetlandType', wetlandType);

      const checkbox = document.querySelector(`.table-select-checkbox[data-type="${wetlandType}"][data-id="${wetlandId}"]`);
      checkbox.checked = !checkbox.checked;
      checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    }
  };

  // TODO This is not really working because the checkboxes of the wetland table are not always accessible - only the ones visible are accessible
  $('#map').on('click', selectWetland);


  const siekerWetland = SiekerWetland.loadFromLocalStorage();
  loadProjectToGui(siekerWetland)

};

