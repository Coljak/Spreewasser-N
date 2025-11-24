import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import {  
    updateDropdown, 
    addChangeEventListener, 
    addClickEventListenerToToolboxPanel, 
    addPointFeatureCollectionToLayer, 
    addFeatureCollectionToLayer, 
    addFeatureCollectionToTable, 
    loadProjectToGui,
    tableCheckSelectedItems,
    clearAndRemoveTable,
    createDetailTable,
} from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { SiekerSurfaceWaters } from '/static/toolbox/sieker_surface_waters_model.js';
import {Layers} from '/static/toolbox/layers.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  map, 
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
        if (data.message.success){
            addFeatureCollectionToLayer(data.lakes, true)
            addFeatureCollectionToTable(data.lakes)
        } else {
            handleAlerts(data.message);
            $('#tabSiekerSurfaceWatersLakes button.reset-double-slider').trigger('click')
        }
        

  });

}


function getAllSiekersurfaceWaters() {
    // returns lakes: {'featureCollection', dataInfo }, message
    const url = 'get_all_sieker_surface_waters/';
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
        if (data.message.success){
            addFeatureCollectionToLayer(data.lakes, true)
            addFeatureCollectionToTable(data.lakes)
        } else {
            handleAlerts(data.message)
        }

  });

}


export function initializeSiekerSurfaceWaters() {
    const project = SiekerSurfaceWaters.loadFromLocalStorage();
    fetch(`get_water_levels/${project.userField}/`, {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message.success) {
            console.log("Water levels data: ", data);
            addPointFeatureCollectionToLayer(data.water_levels, true);
            // createResultTable(data.water_levels);
            // createResultDetailTableRow(data.water_levels.dataInfo)
            createDetailTable(data.water_levels)
        } else {
            clearAndRemoveTable(SiekerSurfaceWaters, data.water_levels.dataType, data.message.message)
            handleAlerts(data.message);
        }
    });

    $('#toolboxPanel').off('change');
    initializeSliders();
    

    addChangeEventListener(SiekerSurfaceWaters);
    // add lakes and water levels
    getAllSiekersurfaceWaters();


    $('#toolboxPanel').on('click', function(event) {
        const $target = $(event.target);
        if ($target.attr('id') === 'toggleSiekerLevels') {
            if (map.hasLayer(Layers['sieker_water_level'])) {
                map.removeLayer(Layers['sieker_water_level']);
                $target.text('Pegel anzeigen');
            } else {
                map.addLayer(Layers['sieker_water_level']);
                $target.text('Pegel ausblenden');
            }
        } else if ($target.attr('id') === 'toggleSiekerLakes') {
            if (map.hasLayer(Layers['sieker_surface_water'])) {
                map.removeLayer(Layers['sieker_surface_water']);
                $target.text('Seen anzeigen');
            } else {
                map.addLayer(Layers['sieker_surface_water']);
                $target.text('Seen ausblenden');
            }
         } else if ($target.attr('id') === 'btnFilterSiekerLakes') {
            const project = SiekerSurfaceWaters.loadFromLocalStorage();
            project.sieker_surface_water_filtered = true;
            filterSiekersurfaceWaters()
         } else if ($target.attr('id') === 'btnUnfilterSiekerLakes') {
            getAllSiekersurfaceWaters()

        }   
    });
    
    addClickEventListenerToToolboxPanel(SiekerSurfaceWaters);

    const siekerSurfaceWaters = SiekerSurfaceWaters.loadFromLocalStorage();
    loadProjectToGui(siekerSurfaceWaters)
    
};

