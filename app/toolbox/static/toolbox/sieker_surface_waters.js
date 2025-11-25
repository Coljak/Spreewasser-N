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

function getAllCatchments(project) {
    const url = 'get_all_above_ground_catchment_areas/';
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
            data.catchments['pane'] = 'backgroundPane';
            addFeatureCollectionToLayer(data.catchments, true)
            // addFeatureCollectionToTable(data.catchments)
            
            // createDetailTable(data.catchments)

            Layers['sieker_water_level'].bringToFront();
        } else {
            handleAlerts(data.message)
        }

  });

};


function getAllSiekersurfaceWaters(project) {
    // returns lakes: {'featureCollection', dataInfo }, message
    const url = 'get_all_sieker_surface_waters/';
    
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
        console.log('data', data)
        if (data.message.success){
            addFeatureCollectionToLayer(data.lakes, true)
            addFeatureCollectionToTable(data.lakes)
            Layers['sieker_surface_water'].bringToBack();
        } else {
            handleAlerts(data.message)
        }

  });

};

function get_all_water_levels(project) {
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

            createDetailTable(data.water_levels)
        } else {
            console.log('ESLE is reached')
            clearAndRemoveTable(SiekerSurfaceWaters, 'sieker_water_level', data.message.message)
        }
    });
}


export function initializeSiekerSurfaceWaters() {
    const project = SiekerSurfaceWaters.loadFromLocalStorage();
    getAllCatchments(project);
    getAllSiekersurfaceWaters(project);
    get_all_water_levels(project);

    $('#toolboxPanel').off('change');
    initializeSliders();
    
    
    addChangeEventListener(SiekerSurfaceWaters);
    // add lakes and water levels


    $('#toolboxPanel').on('click', function(event) {
        const $target = $(event.target);
         if ($target.attr('id') === 'btnFilterSiekerLakes') {
            const project = SiekerSurfaceWaters.loadFromLocalStorage();
            project.sieker_surface_water_filtered = true;
            filterSiekersurfaceWaters()
         } else if ($target.attr('id') === 'btnUnfilterSiekerLakes') {
            getAllSiekersurfaceWaters()
        }  else if ($target.hasClass('toggle-feature-group') && $target.data('type') === 'above_ground_catchment_area') {
            Layers['sieker_water_level'].bringToFront();
            Layers['sieker_surface_water'].bringToFront();
        }
    });
    
    addClickEventListenerToToolboxPanel(SiekerSurfaceWaters);

    const siekerSurfaceWaters = SiekerSurfaceWaters.loadFromLocalStorage();
    loadProjectToGui(siekerSurfaceWaters)
    
};

