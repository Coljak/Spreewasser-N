import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { updateDropdown, addChangeEventListener, addClickEventListenerToToolboxPanel, addFeatureCollectionToTable, addFeatureCollectionToLayer, addPointFeatureCollectionToLayer, loadProjectToGui } from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { SiekerSink } from '/static/toolbox/sieker_sink_model.js';
import {Layers} from '/static/toolbox/layers.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  openUserFieldNameModal,
  addLayerToSidebar, 
  getUserFieldIdByLeafletId, 
  getLeafletIdByUserFieldId, 
  getUserFieldsFromDb, 
  highlightLayer, 
  selectUserField,
  handleSaveUserField,
  dismissPolygon,
  getCircleMarkerSettings, 
  getLegendItem,
  getLegendSettings,
  removeLegendFromMap,
} from '/static/shared/map_sidebar_utils.js';


const siekerSinkFeatureGroup = Layers['sieker_sink']


function filterSiekerSinks(dataType, featureGroup) {
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
    featureGroup.clearLayers();
    console.log('project', project);
  
    // const selected_sinks = project['selected_sinks'];
    if (data.message.success) {


      addPointFeatureCollectionToLayer(data)
      addFeatureCollectionToTable(data)
      


      const legendItems = [
          getLegendItem('Leicht', getCircleMarkerSettings( 'green')),
          getLegendItem('Mittel', getCircleMarkerSettings( 'orange')),
          getLegendItem('Schwer', getCircleMarkerSettings( 'red')),
        ]
      const legendSettings = getLegendSettings ('Umsetzbarkeit', legendItems);
      const legend =  L.control.Legend(legendSettings).addTo(map);

    } else {

      handleAlerts(data.message);
      const tableCard = document.getElementById('card-sieker_sink-table')
      document.getElementById('sieker_sink-table-container').innerHTML = '';

      tableCard.classList.add('d-none');
    }
})
.catch(error => console.error("Error fetching data:", error));
};



export function initializeSiekerSink() {
  

  removeLegendFromMap(map);
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag && layer.toolTag !== 'sieker_sink') {
            map.removeLayer(layer);
        }
        });
  console.log('Initialize Sieker Sink');
  // map.addLayer(siekerSinkFeatureGroup);
  
  initializeSliders();
      
  $('#toolboxPanel').off('change');

  addChangeEventListener(SiekerSink);
  
  addClickEventListenerToToolboxPanel(SiekerSink)
  $('#btnFilterSiekerSinks').on('click', function (event) {

      filterSiekerSinks('siekerSink', siekerSinkFeatureGroup);
    
    });
  

  function selectSink(event) {
    if (event.target.classList.contains('select-sink')) {
      const sinkId = event.target.getAttribute('sinkId');
      const sinkType = event.target.getAttribute('data-type');
      console.log('sinkId', sinkId);
      console.log('sinkType', sinkType);

      const checkbox = document.querySelector(`.sink-select-checkbox[data-type="${sinkType}"][data-id="${sinkId}"]`);
      checkbox.checked = !checkbox.checked;
      checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    }
  };

  // TODO This is not really working because the checkboxes of the sink table are not always accessible - only the ones visible are accessible
  $('#map').on('click', selectSink);

  $('input[type="checkbox"][name="feasibility"][prefix="sieker_sink"]').prop('checked', true);
  $('input[type="checkbox"][name="feasibility"][prefix="sieker_sink"]').trigger('change');

  const siekerSink = SiekerSink.loadFromLocalStorage();
  loadProjectToGui(siekerSink)
};

