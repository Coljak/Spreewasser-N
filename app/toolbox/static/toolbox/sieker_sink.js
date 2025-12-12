import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { 
  updateDropdown, 
  addChangeEventListener, 
  addClickEventListenerToToolboxPanel, 
  addFeatureCollectionToTable, 
  addFeatureCollectionToLayer, 
  addPointFeatureCollectionToLayer, 
  loadProjectToGui,
  getWaterBodies, 
  clearAndRemoveTable,
  createSinkResultTable,
  tableCheckSelectedItems,
} from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { SiekerSink } from '/static/toolbox/sieker_sink_model.js';
import {Layers} from '/static/toolbox/layers.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 

  highlightLayer, 
  selectUserField,
  handleSaveUserField,
  dismissPolygon,
  getCircleMarkerSettings, 
  getLegendItem,
  getLegendSettings,
  removeLegendFromMap,
} from '/static/shared/map_sidebar_utils.js';



 


function filterSiekerSinks(dataType) {
  let url = 'filter_sieker_sinks/';
  
  const project = SiekerSink.loadFromLocalStorage();
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
    Layers[dataType].clearLayers();
    console.log('project', project);
  
    // const selected_sinks = project['selected_sinks'];
    if (data.message.success) {

      addPointFeatureCollectionToLayer(data)
      addFeatureCollectionToTable(data)
      return {'project': project}
    } else {

      handleAlerts(data.message);
      project['selected_sieker_sinks'] = [];
      clearAndRemoveTable(SiekerSink, dataType, data.message.message)
    }
})
.then(data => tableCheckSelectedItems(data.project, 'sieker_sink'))
// .catch(error => console.error("Error fetching data:", error));
};

function getSiekerSinkResults() {
  let url = 'get_sieker_sink_results/'
  const project = SiekerSink.loadFromLocalStorage();
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
      console.log('getSiekerSinkResult data', data);  
      Layers['sieker_sink_result'].clearLayers();
      
      let resultMap = addFeatureCollectionToLayer({dataInfo: data.inlet_data_info, featureCollection: data.inlet_feature_collection}, true)
      resultMap = addFeatureCollectionToLayer({dataInfo: data.sink_data_info, featureCollection: data.sink_feature_collection}, false, resultMap)
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
            'sink': data.sink_data_info,   

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
    

      const resultTab = document.getElementById('navSiekerSinkResult');
      resultTab.classList.remove('disabled');
      resultTab.removeAttribute('aria-disabled');
      const tab = new bootstrap.Tab(resultTab);
      tab.show();

      map.removeLayer(Layers.sieker_sink);
      map.addLayer(Layers.sieker_stream);
      map.addLayer(Layers.sieker_lake);

    } else {

      handleAlerts(data.message);
      
      clearAndRemoveTable(SiekerSink, dataType, data.message.message)
    }
})
.catch(error => console.error("Error fetching data:", error));
};

 


export function initializeSiekerSink() {
  

  console.log('Initialize Sieker Sink');
  // map.addLayer(siekerSinkFeatureGroup);
  
  initializeSliders();
      
  $('#toolboxPanel').off('change');
  addChangeEventListener(SiekerSink);
  $('#toolboxPanel').off('click');
  addClickEventListenerToToolboxPanel(SiekerSink)
  $('#btnFilterSiekerSinks').on('click', function (event) {
      filterSiekerSinks('sieker_sink');    
    });
  $('#btnGetSiekerSinkResults').on('click', function (event) {
      getSiekerSinkResults();    
    });
  
  const siekerSink = SiekerSink.loadFromLocalStorage();
  loadProjectToGui(siekerSink)
};

