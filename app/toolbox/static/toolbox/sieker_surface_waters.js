import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import {  updateDropdown, addChangeEventListener, addClickEventListenerToToolboxPanel, addPointFeatureCollectionToLayer, addFeatureCollectionToLayer, addFeatureCollectionToTable} from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { SiekerSurfaceWaters } from '/static/toolbox/sieker_surface_waters_model.js';
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






function filterSiekersurfaceWaters() {
    const url = 'filter_sieker_surface_waters/';
    const project = SiekerSurfaceWaters.loadFromLocalStorage();
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
  });

}



function addWaterLevelToResultCard(data) {
    const dataInfo = data.dataInfo;
    const featureCollection = data.featureCollection;
}

export function initializeSiekerSurfaceWaters(layers) {
    

    console.log("Initializing Sieker surface waters...", layers);
    removeLegendFromMap(map);
    map.eachLayer(function(layer) {
        if (layer.toolTag && layer.toolTag !== 'sieker-surface-waters') {
            map.removeLayer(layer);
        }
        });

    $('#toolboxPanel').off('change');
    initializeSliders();
    

    addChangeEventListener(SiekerSurfaceWaters);
    // add lakes and water levels

    addFeatureCollectionToLayer(layers.lakes)
    addFeatureCollectionToTable(layers.lakes)

    addPointFeatureCollectionToLayer(layers.water_levels)
    addWaterLevelToResultCard(layers.water_levels)


    // waterLevels.addTo(Layers['sieker_water_level']);


    // map.addLayer(Layers['sieker_large_lake']);
    // map.addLayer(Layers['sieker_water_level']);

    document.getElementById('toggleSiekerLevels').addEventListener('click', function() {
        if (map.hasLayer(Layers['sieker_water_level'])) {
            map.removeLayer(Layers['sieker_water_level']);
            this.textContent = 'Pegel anzeigen';
        } else {
            map.addLayer(Layers['sieker_water_level']);
            this.textContent = 'Pegel ausblenden';
        }
    });

    document.getElementById('toggleSiekerLakes').addEventListener('click', function() {
        if (map.hasLayer(Layers['sieker_large_lake'])) {
            map.removeLayer(Layers['sieker_large_lake']);
            this.textContent = 'Seen anzeigen';
        } else {
            map.addLayer(Layers['sieker_large_lake']);
            this.textContent = 'Seen ausblenden';
        }
    });
    
    addClickEventListenerToToolboxPanel(SiekerSurfaceWaters)
};

