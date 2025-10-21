import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { updateDropdown, addChangeEventListener, addClickEventListenerToToolboxPanel, addFeatureCollectionToTable, addFeatureCollectionToLayer, addPointFeatureCollectionToLayer, loadProjectToGui } from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { Drainage } from '/static/toolbox/sieker_drainage_model.js';
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




function filterDrainages(dataType, featureGroup) {
  let url = 'filter_sieker_drainages/';
  
  const project = Drainage.loadFromLocalStorage();
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
      const tableCard = document.getElementById('card-sieker_drainage-table')
      document.getElementById('sieker_drainage-table-container').innerHTML = '';

      tableCard.classList.add('d-none');
    }
})
.catch(error => console.error("Error fetching data:", error));
};



export function initializeDrainage(userField) {
  const project = new Drainage();
  project.userField = userField;
  project.saveToLocalStorage()

  removeLegendFromMap(map);
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag && layer.toolTag !== 'sieker_drainage') {
            map.removeLayer(layer);
        }
        });
  console.log('Initialize Sieker Drainage with project:', project);
  // map.addLayer(siekerSinkFeatureGroup);
  
  initializeSliders();
      
  $('#toolboxPanel').off('change');

  addChangeEventListener(Drainage);
  
  addClickEventListenerToToolboxPanel(Drainage)
  $('#btnFilterDrainages').on('click', function (event) {

      filterDrainages('Drainage', DrainageFeatureGroup);
    
    });
  


  $('input[type="checkbox"][name="feasibility"][prefix="sieker_drainage"]').prop('checked', true);
  $('input[type="checkbox"][name="feasibility"][prefix="sieker_drainage"]').trigger('change');

};

