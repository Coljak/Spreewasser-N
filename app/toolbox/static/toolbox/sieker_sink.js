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

    } else {

      handleAlerts(data.message);
      
      clearAndRemoveTable(SiekerSink, dataType, data.message.message)
    }
})
.catch(error => console.error("Error fetching data:", error));
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
    Layers['sieker_sink_result'].clearLayers();
    console.log('project', project);
  
    // const selected_sinks = project['selected_sinks'];
    if (data.message.success) {

      // addPointFeatureCollectionToLayer(data)
      // addFeatureCollectionToTable(data)

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

