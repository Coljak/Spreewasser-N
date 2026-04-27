import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import {  
    addChangeEventListener, 
    addClickEventListenerToToolboxPanel, 
    addPointFeatureCollectionToLayer, 
    addFeatureCollectionToLayer, 
    addFeatureCollectionToTable, 
    loadProjectToGui,
    tableCheckSelectedItems,
    clearAndRemoveTable,
    createDetailRows,
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
    const project = SiekerSurfaceWaters.loadFromLocalStorage();
    const url = 'filter_sieker_surface_waters/';
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
        return data.lakes.dataInfo;
    })
    .then(dataInfo => {
        console.log('Get all selected surface waters:', project['selected_sieker_surface_waters']);
        tableCheckSelectedItems(project, dataInfo.dataType)});
};


function detailHtml(dataInfo, property) {
    return `<div class="container-fluid">
                <div id="card-sieker_water_level-${property.id}" class="card container-fluid mb-3">
                    <div class="card-body">
                        <h5 id="waterLevelChartTitle-${property.id}">Wasserstand Verlauf</h5>
                        <div id="${dataInfo.dataType}-spinner-${property.id}" 
                            class="d-flex justify-content-center align-items-center in-table-spinner  d-none">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <div class="chart-container">
                            <canvas id="chart-sieker_water_level-${property.id}" class="chart-canvas" ></canvas>
                        </div>
                    </div>
                </div>
            </div>
            `;
};


function getAllCatchments() {
    const project = SiekerSurfaceWaters.loadFromLocalStorage();
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
            addFeatureCollectionToTable(data.catchments)
            Layers['sieker_water_level'].bringToFront();
        } else {
            handleAlerts(data.message)
        }
  });
};


function getAllSiekersurfaceWaters() {
    const project = SiekerSurfaceWaters.loadFromLocalStorage();
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
    return data.lakes.dataInfo;
  })
  .then(dataInfo => {
    console.log('Get all selected surface waters:', project['selected_sieker_surface_waters'])
    tableCheckSelectedItems(project, dataInfo.dataType)});
};

function get_all_water_levels() {
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


            const table = addFeatureCollectionToTable({
                featureCollection: data.water_levels.featureCollection,
                dataInfo: data.water_levels.dataInfo,
                tableClasses: 'table',
                rowClasses: 'table-parent-row',
                switchInput: true,
            })
            createDetailRows(table, data.water_levels.featureCollection, data.water_levels.dataInfo, detailHtml)
        } else {
            console.log('ESLE is reached')
            clearAndRemoveTable(SiekerSurfaceWaters, 'sieker_water_level', data.message.message)
        }
    });
}


export function initializeSiekerSurfaceWaters() {
    
    getAllCatchments();
    getAllSiekersurfaceWaters();
    get_all_water_levels();

    $('#toolboxPanel').off('change');
    $('#toolboxPanel').off('click');
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
        }
    });
    
    addClickEventListenerToToolboxPanel(SiekerSurfaceWaters);

    const siekerSurfaceWaters = SiekerSurfaceWaters.loadFromLocalStorage();
    loadProjectToGui(siekerSurfaceWaters)
    
};

