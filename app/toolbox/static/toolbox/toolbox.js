import { getGeolocation, handleAlerts, getCSRFToken, saveProject, observeDropdown,  setLanguage, populateDropdown } from '/static/shared/utils.js';
import {Infiltration} from '/static/toolbox/infiltration_model.js';
import {Injection} from '/static/toolbox/injection_model.js';
import {SiekerGek} from '/static/toolbox/sieker_gek_model.js';
import {SiekerSink} from '/static/toolbox/sieker_sink_model.js';
import {SiekerSurfaceWaters} from '/static/toolbox/sieker_surface_waters_model.js';
import {SiekerWetland} from '/static/toolbox/sieker_wetland_model.js';
import { Drainage } from '/static/toolbox/sieker_drainage_model.js';
import {map, removeLegendFromMap, getSelectedUserField} from '/static/shared/map_sidebar_utils.js';
import {Layers} from '/static/toolbox/layers.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { dataTableGerman } from '/static/toolbox/dataTable_german.js'

// all dataTypes mapped to their ProjectClass
const projectClasses = {
    'sink': Infiltration,
    'enlarged_sink': Infiltration,
    'stream': Infiltration,
    'lake': Infiltration,
    'infiltration': Infiltration,
    'infiltration_result': Infiltration,
    'infiltration_result_sink': Infiltration,
    'infiltration_result_enlarged_sink': Infiltration,
    'infiltration_result_inlet': Infiltration,

    'injection': Injection,

    'filtered_sieker_gek': SiekerGek,
    'sieker_gek': SiekerGek,

    'wetland': SiekerWetland,
    'wetland_lake': SiekerWetland,
    'wetland_stream': SiekerWetland,
    'wetland_result': SiekerWetland,

    'sieker_sink': SiekerSink,
    'sieker_lake': SiekerSink,
    'sieker_stream': SiekerSink,
    'sieker_sink_result': SiekerSink,
    'sieker_sink_result_sink': SiekerSink,
    'sieker_sink_result_inlet': SiekerSink,

    'sieker_surface_water': SiekerSurfaceWaters,
    'sieker_water_level': SiekerSurfaceWaters,
    'above_ground_catchment_area': SiekerSurfaceWaters, 

    'drainage': Drainage,
};

function toggleValueInArray(list, val) {
    let value = String(val);
  const index = list.indexOf(value);
  if (index > -1) {
    list.splice(index, 1); // remove
  } else {
    list.push(value); // add
  }
  return list;
};

export function toggleInlet(dataType, inlet_id, layer_id) {
    const featureGroup = Layers[dataType];
    const sinkLayer = featureGroup.getLayer(layer_id)
}

export function getWaterBodies($button, ProjectClass){
    // used in Infiltration and SiekerSink
    console.log('get waterbodies')
  const dataType = $button.data('type');
  console.log('getWaterBodies', dataType)
  const spinner = $button.find('.spinner-border')
  spinner.show();
  $button.prop('disabled', true) 
  let url = `filter_waterbodies/`;
  const project = ProjectClass.loadFromLocalStorage();
  fetch(url, {
    method: 'POST',
    body: JSON.stringify({
      dataType: dataType,
      project: project}),
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
    }
  })
  .then(response => response.json())
  .then(data => {
    console.log('data', data)
    if (data.message.success) {
      addFeatureCollectionToLayer(data, true)
      addFeatureCollectionToTable(data)
      return {'project': project}
    }  else {
      // TODO clear layers
      clearAndRemoveTable(ProjectClass, dataType, data.message.message)
      handleAlerts(data.message);
    } 
  })
  .then(data => tableCheckSelectedItems(data.project, dataType))
  .catch(error => console.error("Error fetching data:", error))
  .finally(() => {
    // Always hide spinner & enable button
    spinner.hide();
    $button.prop('disabled', false);
  });
};


function getWaterLevelTimeseries(waterLevelId) {
    const canvas = document.getElementById(`chart-sieker_water_level-${waterLevelId}`);


    if (Chart.getChart(canvas)) {
        console.log(`Canvas chart ${waterLevelId} is already in use. Skipping.`);
        return; // Do nothing
    } else if (canvas){
        console.log('canvas', canvas);
        const canvasCard = document.querySelector(`#card-sieker_water_level-${waterLevelId}`);
        const spinner = document.querySelector(`#sieker_water_level-spinner-${waterLevelId}`);
        spinner.classList.remove('d-none');
        canvasCard.classList.remove('d-none')
        const url = `get_sieker_surface_water_levels/${waterLevelId}/`;
        fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log("Water level timeseries data: ", data);
            // $('#waterLevelSurfaceWaterTitle').text(data.station_name)
            $(`#waterLevelChartTitle-${waterLevelId}`).text(`Wasserstand Verlauf ${data.station_name}`);
            // const canvas = document.getElementById(`chart-sieker_water_level-${waterLevelId}`);
            const ctx = canvas.getContext('2d');
            if (canvas.chart) {
                try {
                    canvas.chart.destroy();
                } catch {;}
                }
            const deLocale = dateFns.locale?.de;
            spinner.classList.add('d-none');

            canvas.chart = new Chart(ctx, {
            type: 'bar',
            backgroundColor: 'rgb(54, 162, 235 )',
            data: {
                datasets: [{
                    label: 'Wasserstand (cm)',
                    data: data.chart_data
                }]
            },
            options: {
                responsive: true,
                // aspectRation:3,
                maintainAspectRatio: false,
                scales: {
                x: {
                    type: 'time',
                    adapters: { date: { locale: deLocale } },
                    time: { unit: 'month', displayFormats: { month: 'MM-yyyy' } },
                    title: { display: true, text: 'Datum' }
                },
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Wasserstand (cm)' }
                }
                }
            }
            })
        });
    } else return;

}

// TODO I think      this is not working!
$('#map').on('click', function (event) {
    if (event.target.classList.contains('select-map-feature-checkbox')) {
        const dataType = event.target.getAttribute('data-type');
        const dataId = event.target.getAttribute('data-id');
            // map.closePopup();

    try {     
        // the checkbox is not necessarily available
        const checkbox = document.querySelector(`.table-select-checkbox[data-type="${dataType}"][data-id="${dataId}"]`);
            checkbox.checked = event.target.checked;
        } catch {;}
        const project = projectClasses[dataType].loadFromLocalStorage()
        project[`selected_${dataType}s`] = toggleValueInArray(project[`selected_${dataType}s`], Number(dataId));
        project.saveToLocalStorage();
    }
});

$('#toolboxProjectModal').on('hidden.bs.modal', function () {
        // Reset the form inside the modal
        $('.new-toolbox-project')[0].reset();
        $('#id_project_name').val('')
        $('#projectTypeSelect').prop('disabled', false);
        $('#userFieldSelect').prop('disabled', false);
        $('#saveToolboxProjectButton').data('page-reload', true);
    });

export function makeColoredPin(color, iconPath = null, label = "") {
    const iconHtml = iconPath
        ? `<img src="${iconPath}" class="pin-icon" />`
        : `<span class="pin-label">${label}</span>`;

    return L.divIcon({
        className: "colored-pin",
        html: `
             ${iconHtml}
            <div class="pin-tip" style="border-top-color:${color}"></div>
            <div class="pin-shape" style="background-color:${color}"></div>    
        `,
        iconSize: [28, 38],
        iconAnchor: [12, 38],
        popupAnchor: [138, 138]
    });
}

export const updateDropdown = (parameterType, newId) => {
    
    // the absolute path is needed because most options are exclusively from /monica
    let baseUrl = 'get_options/';

    console.log('updateDropdown baseUrl', baseUrl);
    var select = document.querySelector('.form-select.' + parameterType); 
    fetch(baseUrl + parameterType + '/')
    .then(response => response.json())
    .then(data => {
        console.log('updateDropdown', data);
        populateDropdown(data, select);
    })
    .then(() => {
        if (newId != '') {
            select.value = newId
        }
        $(select).trigger('change');
    })
    .catch(error => console.log('Error in updateDropdown', error));
};

export function tableCheckSelectedItems(project, dataType) {
    console.log('tableCheckSelectedItems', dataType, project)
  if (project[`selected_${dataType}s`] !== undefined) {
    console.log('tableCheckSelectedItems behind first if: ', dataType, project[`selected_${dataType}s`])
    const checkboxes = document.querySelectorAll(`.table-select-checkbox[data-type="${dataType}"]`)
    checkboxes.forEach(checkbox => {
        const checked = project[`selected_${dataType}s`].includes(String(checkbox.dataset.id)) ? true : false;
        // const checked = project[`selected_${dataType}s`].includes(checkbox.dataset.id) ? true : false;

        checkbox.checked = checked;
        })
    }
};


export function addLegend(legendSettings) {
    console.log('addLegend', legendSettings)
    removeLegendFromMap(map)

    let labels = [];
    for (let i = 0; i < legendSettings.grades.length; i++) {
            const value = legendSettings.grades[i];
            const color = colorFunction(value);
            const label = legendSettings.gradientLabels[i];

            labels.push({
                label: label,
                radius: 6,
                type: 'circle',
                // sides: 4,
                weight: 2,
                fillOpacity: 1,
                color: 'black',
                fillColor: color,
                // margin:5
            })
        }

    const legend = L.control.Legend(
        { 
        position: 'bottomright',
        collapsed: false,
        title: legendSettings.header,
        legends: labels

        }).addTo(map);
};

export async function toolboxSinksOutline() {
    // gets the sink outline
    // TODO: obsolte??static 'tool
  try {
      const response = await fetch('toolbox_sinks/');
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const geojsonData = await response.json();

      // Create a Leaflet GeoJSON layer
      const toolboxSinks = L.geoJSON(geojsonData, {
          attribution: 'Toolbox Sinks',
          onEachFeature: function (feature, layer) {
              layer.bindTooltip(feature.properties.name, {
                direction: 'left',      
                offset: [0, 0],        
                permanent: false,       
                sticky: true  
            });
          }
      });

      return toolboxSinks; // Return the Leaflet layer
  } catch (error) {
      console.error("Error loading project region:", error);
      return null;
  }
};

export async function loadProjectFromDb(project_id) {
    console.log('loadProjectFromDb', project_id);
    const response = await fetch(`/toolbox/load-project/${project_id}/`);
    const data = await response.json();
    if (data.success) {
        console.log('received data', data)
        const ProjectClass = ToolboxProject.subclassRegistry[data.project.toolboxType] || ToolboxProject;
        const loadedProject = ProjectClass.fromJson(data.project);
        loadedProject.saveToLocalStorage();
        console.log('Loaded project:', loadedProject);
        return loadedProject;
    } else {
        handleAlerts(data.message);
    }
};

export function addChangeEventListener(projectClass) {
    const CurrentProjectClass = projectClass;
    console.log(projectClass)
    $('#toolboxPanel').on('change', function (event) {
        const $target = $(event.target);
        const project = CurrentProjectClass.loadFromLocalStorage();
        if ($target.hasClass('double-slider')) {
            const inputName = $target.attr('name');
            const minName = inputName + '_min';
            const maxName = inputName + '_max'; 
            const inputVals = $target.val().split(',');
            project[minName] = inputVals[0];
            project[maxName] = inputVals[1];
            project.saveToLocalStorage();
            return;
        } else if ($target.hasClass('single-slider')) {   
            const inputName = $target.attr('name'); 
            const inputVal = $target.val();
            project[inputName] = inputVal;
            project.saveToLocalStorage();
            return;
        } else if ($target.hasClass('form-check-input') && $target.is('[name]') && $target.is('[prefix]')) {
            // checkboxes 
            const inputName = $target.attr('name');
            const inputPrefix = $target.attr('prefix');
            const inputValue = $target.attr('value');
            const inputChecked = $target.is(':checked');

            const key = `${inputPrefix}_${inputName}`;
            console.log('key', key )
            const index = project[key].indexOf(inputValue);
            // console.log("eventListener change ($target.hasClass('form-check-input')")
            toggleValueInArray(project[key], inputValue);

            project.saveToLocalStorage();
            return;
        } else if ($target.hasClass('table-select-all')) {
            
        
            const allSelected = $target.is(':checked');
            const dataType = $target.data('type');

            const key = `selected_${dataType}s`;
            console.log('table-select-all key', key)
            if (!allSelected) {
                console.log('!allSelected')
                project[key] = [];
            } else {
                project[key] = project[`all_${dataType}_ids`]                
            }
           
            tableCheckSelectedItems(project, dataType);
            project.saveToLocalStorage();
            return;
        } else if ($target.hasClass('table-select-checkbox')) {
            const dataType = $target.data('type');
            
            const key = `selected_${dataType}s`;
            const isChecked = $target.is(':checked')
            // in case checkable Popup is open
            try {
                const checkbox = document.querySelector(`.select-map-feature-checkbox[data-type="${dataType}"][data-id="${$target.data('id')}"]`);
                checkbox.checked = isChecked;
            } catch  {;};
            if (!isChecked && $(`.table-select-all[data-type="${dataType}"]`)[0].checked) {
                $(`.table-select-all[data-type="${dataType}"]`)[0].checked = false;
            } 
            toggleValueInArray(project[key], String($target.data('id')));
            project.saveToLocalStorage();
            return;
 
        };
    });
};

export function openResultCard(dataType, id) {
    console.log('openResultCard: ', dataType, id)
    $('.gek-result-card').hide()
    const $resultCard = $(`div[data-type="${dataType}"][data-id="${id}"]`)
    $resultCard.show();
    $resultCard[0].scrollIntoView({
        behavior: 'smooth',   
        block: 'start'
        });
};

export function setProjectInfoHeader(project) {
    console.log('setProjectInfoHeader', project);
    if (project.name) {
        $('.title-project-name').text(project.name);
    }
    if (project.userField) {

        const userFields = JSON.parse(localStorage.getItem('userFields')) || [];
        const userFieldName = Object.values(userFields).find((uf => uf.id === project.userField)).name;
        
        if (userFieldName) {
            $('.title-user-field-name').text(userFieldName);
        } else {
            $('.title-user-field-name').text('ID', project.userField);
        }
    }
}

export function loadProjectToGui(project) {

    console.log('loadProjectToGui', project);
    setProjectInfoHeader(project)
    
    const doubleSliders = $('#toolboxPanel input.double-slider');
    if (doubleSliders.length) {
        doubleSliders.each(function () {
            // console.log('double slider this', this)
            const $slider = $(this);
            const min = parseFloat(project[`${$slider.attr('name')}_min`]);
            const max = parseFloat(project[`${$slider.attr('name')}_max`]);
            // console.log('double slider min max', min, max)
            $slider.slider('setValue', [min, max]);
        });
    }
    
        // --- Single sliders ---
    const $singleSliders = $('#toolboxPanel input.single-slider');
    if ($singleSliders.length) {
        $singleSliders.each(function () {
            // console.log('single slider this', this)
            const $slider = $(this);
            const value = project[$slider.attr('name')];
            // console.log('single slider value', value)
            $slider.val(value).trigger('input');
        });
    }

    // --- Checkboxes ---
    const $checkboxes = $('#toolboxPanel .form-check-input[prefix][name]');
    console.log(`checkboxes: $('#toolboxPanel .form-check-input[prefix][name]')`)
    // these checkboxes are in drainage network
    if ($checkboxes.length) {
        $checkboxes.each(function () {
            // console.log('checkbox this', this)
            const $checkbox = $(this);
            const val = $checkbox.val();
            const key = $checkbox.attr('prefix') + '_' + $checkbox.attr('name');
            // console.log('checkbox val key', val, key)
            console.log('checkbox checked key', key, val)
            $checkbox.prop('checked', project[key].includes(val));

        });
    }

    
    for (const [key, value] of Object.entries(project)) {
        if (key.startsWith('all_') && key.endsWith('_ids') && value.length > 0) {
            const dataType = key.replace('all_', '').replace('_ids', '');
      
           if (project.toolboxType === 'sieker_surface_water') {
                console.log('Special case for sieker_surface_water and sieker_gek')
                if (project.sieker_surface_water_filtered === false){
                    tableCheckSelectedItems(project, 'sieker_surface_water')
                } else {
                    $(`button.filter-features[data-type="${dataType}"]`).trigger('click')
                }
                tableCheckSelectedItems(project, 'sieker_water_level')

            } else if (project.toolboxType === 'sieker_gek') {
                console.log('Toolbox Type sieker_gek key', key)
                if (project[key].length >0) {

                    console.log('Special case for sieker_gek, key > 0', project[key])
                    tableCheckSelectedItems(project, dataType)
                }
                
                if (project.all_filtered_sieker_gek_ids.length > 0) {
                    console.log('Special case', dataType, project.all_filtered_sieker_gek_ids)
                    $(`button.filter-features[data-type="${dataType}"]`).trigger('click')
                }

            } else if (project.toolboxType === 'infiltration' && dataType === 'infiltration_result' && project.selected_infiltration_results.length > 0) {
                console.log('Special case for infiltration_result', project.selected_infiltration_results)
                $(`#btnGetInfiltrationResults`).trigger('click')
            } else if (project.toolboxType === 'sieker_sink' && dataType === 'sieker_sink_result' && project.selected_sieker_sink_results.length > 0) {
                console.log('Special case for sieker_sink_result', project.selected_sieker_sink_results)
                $(`#btnGetSiekerSinkResults`).trigger('click')
            } else if (project.toolboxType === 'wetland' && dataType === 'wetland_result' && project.selected_wetland_results.length > 0) {
                $(`#btnGetSiekerWetlandResults`).trigger('click')
            } else {
                console.log('Toolbox Type', project.toolboxType)
                $(`button.filter-features[data-type="${dataType}"]`).trigger('click')
            }    
        }
    }
                
};

export function clearToolboxPanel(){
    // destroy all charts
    $('canvas').each(function () {
        const chart = Chart.getChart(this);   // this = canvas element
        if (chart) {
            chart.destroy();
        }
    });
    // clear the toolboxPanel
    $('#toolboxButtons').removeClass('d-none');
    $('#toolboxPanel').html('') 
    $('#toolboxPanel').addClass('d-none');
    // clear all legends from map
    removeLegendFromMap(map);
    map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag) {
            if (layer.clearLayers) {
                layer.clearLayers();  
            }
            map.removeLayer(layer);    
        }
    });
    const newProject = new ToolboxProject();
    newProject.userField = getSelectedUserField();
    newProject.saveToLocalStorage();
};


export function addClickEventListenerToToolboxPanel(projectClass) {

    const ProjectClass = projectClass;
    $('#toolboxPanel').on('click',function (event) {
        console.log('click')
        const $target = $(event.target);
        // !!! button if the button is wrapped with a spinner or info
        const button = $target.closest('button')
        const project = ProjectClass.loadFromLocalStorage();
        if ($target.hasClass('toolbox-back-to-initial')) {
            
            clearToolboxPanel();
            return;
        // table related
        } else if (button.hasClass('toggle-tile-layer')) {
            console.log('toggle-tile-layer')
              const dataType = $target.data('type')
              if ($target.hasClass('shown')) {
                $('button.toggle-tile-layer').removeClass('shown');
                $('button.toggle-tile-layer').text('Layer einblenden')
                document.querySelector('.leaflet-overlayRaster-pane').hidden = true;
                document.querySelector('.leaflet-legend').hidden = true; 
              } else {
                $('button.toggle-tile-layer').text('Layer ausblenden')
                $('button.toggle-tile-layer').addClass('shown');
                
                document.querySelector('.leaflet-overlayRaster-pane').hidden = false;
                document.querySelector('.leaflet-legend').hidden = false; 
                $target.addClass('shown')
              }
              
        } else if (
            $target.hasClass('paginate_button') || 
            $target.hasClass('sorting') ||
            $target.hasClass('sorting_asc') ||
            $target.hasClass('sorting_desc')) {
                console.log('Paginate')
                const dataType =  $target.attr('aria-controls').split('-')[0];
                tableCheckSelectedItems(project, dataType)
                colorTable(dataType)
            return;
        
        } else if (button.hasClass('filter-features')) {
            console.log('hasClass filter-features')
            const dataType = button.data('type')
            const $displayButton = $(`button.toggle-feature-group[data-type="${dataType}"]`)
            if ($displayButton && $displayButton.hasClass('d-none')) {
                console.log('hasClass d-none')
                $displayButton.removeClass('d-none')
            }
        } else if (button.hasClass('toggle-feature-group')) {
            
            const dataType = button.attr('data-type')
            console.log('toggle-feature-group!', dataType)
            
            if (map.hasLayer(Layers[dataType])) {
                // console.log('Layer exists:', dataType);
                map.removeLayer(Layers[dataType]);
                // console.log('Layer removed:', Layers[dataType]);
                button.text('Layer einblenden');
            } else {
                // console.log('Layer added:', dataType);
                map.addLayer(Layers[dataType]);
                button.text('Layer ausblenden');
            }
        } else if (button.hasClass('toggle-grouped-feature-group')) {
            const dataType = button.attr('data-type')
            if (button.hasClass('shown')) {
                Layers[dataType].forEach((layer) => {
                    map.removeLayer(layer);
                    
                }) 
                button.removeClass('shown');
                button.text('Layer einblenden');
            } else {
                $(`input[data-type="${dataType}"]`).each((_, input) => {
                    const prefix = $(input).attr('prefix');
                    const isChecked = $(input).is(':checked');
                    console.log('prefix is checked:', input, prefix, isChecked)
                    
                    if (isChecked && (prefix === 'parent' || prefix === 'drained_area')) {
                        $(input).trigger('change');
                    }
                });
                button.addClass('shown');
                button.text('Layer ausblenden');
            };
            
        } else if ($target.hasClass('save-toolbox-project')) {
            if (!project.id || project.name === '') {
                $('#userFieldSelect').val(project.userField);
                $('#toolboxProjectModal').modal('show');
                
                $('#id_project_name').focus();
                $('#projectTypeSelect').val($target.data('type'));
                $('#projectTypeSelect').prop('disabled', true);
                $('#userFieldSelect').prop('disabled', true);
                $('#saveToolboxProjectButton').data('page-reload', false);

            } else {
                project.saveToDB();
            }
        } else if ($target.hasClass('toolbox-load-project')) {
            console.log('button has class')
            const project_id = $('#id_toolbox_project').val();
            const loadedProject = loadProjectFromDb(project_id);
            loadedProject.then(project => {
                console.log('Loaded project:', project);
                loadProjectToGui(project);
                // necessary for drainage
                // $('input[type="checkbox"]').trigger('change');

            });
        } else if ($target.closest('tr').hasClass('table-parent-row') &&
                    !$target.is('input, button, a')) {
            
            const tRow = $target.closest('tr');
            const id = tRow.data('id');
            const dataType = $(tRow).data('type');
            console.log('dataType', dataType)
            const table = $(`#${dataType}-table`).DataTable();

            const row = table.row(tRow);
            console.log('row', row)
            console.log('child', row.child)
            if (row.child.isShown()) {
                row.child.hide();
                tRow.removeClass('shown table-success');
            } else {
                row.child.show();
                tRow.addClass('shown table-success');
                if (dataType === 'sieker_water_level') {
                    getWaterLevelTimeseries(id);
                } else if (dataType === 'filtered_sieker_gek') {
                    // just toggles the row
                    ;
                } else if (tRow.hasClass('inlet-header-row')) {
                    // several dataTypes therefore inlet-header-row
                    const waterbodyType = tRow.attr('waterbody-type');
                    const waterbodyId = tRow.attr('waterbody-id');
                    console.log('Inlet eventlistener')
                    getInletVolumeChart(waterbodyType, waterbodyId, id);
                }
            }
        } else if ($target.hasClass('download-results')) {
            event.preventDefault();
            console.log('download-results', $target)
            const project = ProjectClass.loadFromLocalStorage();

            let url = `download_toolbox_results/`;
            fetch(url, {
                method: 'POST',
                body: JSON.stringify(project),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                }
            })
            .then(response => response.blob())
            .then(blob => {
                console.log('blob', blob)
                const link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = `${project.toolboxType}.zip`;   // filename for user
                link.click();
                window.URL.revokeObjectURL(link.href);
            });

        }

        if (button.hasClass('filter-waterbodies')) {
            console.log('Click eventlistener filter-waterbodies')
            getWaterBodies(button, ProjectClass);  
        
        }
    });
};

$('tr.table-parent-row').on('hover', function (event) {
    console.log('hover', event)
});

// for all tables userd in the toolbox
function createTableSettings(dataInfo) {
    const tableLength = dataInfo.tableLength;
    const columnDefs = [];


    for (let i=0; i<tableLength; i++) {
        if (dataInfo.properties[i].table) {
            columnDefs.push({
            "targets": i, // Select a checkbox
            "orderable": dataInfo.properties[i].valueName !== 'id',
            "searchable": false
        })
        }
        
    }
    return {
        "order": [[1, "asc"]],
        "searching": false,
        "columnDefs": columnDefs,
        "stripeClasses": [],
        "language": dataTableGerman,
    }
};

const colorFunction = function (index) {
    if (index === '==') {
        return '#ffffff';
    } else {
        return `hsl(${index}, 90%, 50%)`;
    }
  r
};

const tableColorFunction = function (index) { 
  return `hsl(${index}, 80%, 60%)`;
};



function addPopUpsToFeature(feature, layer, dataInfo) {
    let popupContent = '';
    if (feature.properties[dataInfo.popUp.header]) {
        popupContent += `<h6><b> ${feature.properties[dataInfo.popUp.header]}</b></h6>`;
    }
    dataInfo.properties.forEach(property => {
        

        if (property.popUp) { 
            const value = feature.properties[property.valueName];

            popupContent += property.href
                ? `<a href="${value}" target="_blank">${property.title}</a><br>`
                : `<b>${property.title}:</b> ${value != null ? value : '-'} ${value != null ? (property.unit ?? '') : ''}<br>`;
        }
    });
    
    const popupOptions = {
        offset: [0, -30],   // shift popup upwards
        autoPan: false      // don’t auto-pan map on hover
    };
    
    // Show popup on hover
    layer.on('mouseover', function (event) {
        // open popup at mouse location
        const hoverPopup = L.popup(popupOptions)
            .setLatLng(event.latlng)
            .setContent(popupContent)
            .openOn(map);

        // close when mouse leaves feature
        layer.once('mouseout', function () {
            map.closePopup(hoverPopup);
        });
    });
    let popupClickContent = popupContent;
    if (dataInfo.selectFeatureButton === true) {
        popupClickContent = popupContent + 
            `<div class="form-check">
                <input type="checkbox" class="select-map-feature-checkbox form-check-input" data-type="${dataInfo.dataType}" data-id="${feature.properties.id}">
                <label class="form-check-label">Auswählen</label>
            </div>`;
    };

    // Show persistent popup on click
    layer.on('click', function (event) {
        // close any hover popup first
        map.closePopup();

        const popUp = L.popup(popupOptions)
            .setLatLng(event.latlng)
            .setContent(popupClickContent)
            .openOn(map);
        const checkbox = document.querySelector(`.select-map-feature-checkbox[data-id="${feature.properties.id}"]`)
        if (checkbox){
            const project = projectClasses[dataInfo.dataType].loadFromLocalStorage();
            const isSelected = project[`selected_${dataInfo.dataType}s`].includes(String(feature.properties.id));
            console.log('isSelected', isSelected);
            checkbox.checked = isSelected;
        }   
    });  
}


export function addFeatureCollectionToLayer(data, clearLayer, resultMap={}){
    console.log('addFeatureCollectionToLayer', data)
    let featureCollection = data.featureCollection;
    let dataInfo = data.dataInfo;  
    console.log(dataInfo)
    let colorByIndex = dataInfo.colorByIndex ? dataInfo.colorByIndex : false
    
    console.log('dataInfo.dataType', dataInfo.dataType)
    const featureGroup = Layers[dataInfo.dataType]
    if (clearLayer) {
        featureGroup.clearLayers();
    }
    let color;
    let geojsonLayer = L.geoJSON(featureCollection, {
        style: function (feature) {
            if (dataInfo.colorByIndex) {
                if (dataInfo.colorByIndex === '==') {
                    color = dataInfo.featureColor;
                } else {
                    color = colorFunction(feature.properties[dataInfo.colorByIndex]);
            }
            } else {
                color = dataInfo.featureColor;
            }

            const style = {
                className: dataInfo.className,
                weight: 3,
            };
            if (dataInfo.featureType === "polygon" && colorByIndex && dataInfo.featureColor) {
                style.fillColor = color;                  // dynamic fill
                style.color = dataInfo.featureColor;      // outline color
                style.fillOpacity = 0.5;                 // optional
            }
            // CASE 2: everything else
            else {
                style.color = color;
                style.fillOpacity = 0;
            }

            if (dataInfo.dashArray) {
                style.dashArray = dataInfo.dashArray;
            }
            return style;
        },
        pane: data.pane ?? "polygonPane",
        onEachFeature: function(feature, layer) {
            addPopUpsToFeature(feature, layer, dataInfo);

            resultMap[`${dataInfo.dataType}_${feature.properties.id}`] = layer;
            Layers[dataInfo.dataType].addLayer(layer);
        }
        
        });

    // Layers[dataInfo.dataType].addLayer(geojsonLayer)
    
    if (dataInfo.legendSettings) {
        addLegend(dataInfo.legendSettings)
      }
    
    featureGroup.addTo(map);
    geojsonLayer.bringToFront();

    return resultMap;
};


export function addPointFeatureCollectionToLayer(data) {

    console.log(data)
    let featureCollection = data.featureCollection 
    let dataInfo = data.dataInfo
    let featureGroup = Layers[dataInfo.dataType];
    featureGroup.clearLayers();
    let colorByIndex = dataInfo.colorByIndex ? dataInfo.colorByIndex : false
   

    let points = L.geoJSON(featureCollection, {
        pointToLayer: function (feature, latlng) {
            let color ;
            if (colorByIndex) {
                color = colorFunction(feature.properties[colorByIndex])
                
            } else { 
                color = dataInfo.featureColor 
            }
            const pinPath = dataInfo.pinIconPath ? dataInfo.pinIconPath : '/static/images/pin-transparent_dot.png';
            const pin = makeColoredPin(color, pinPath);
            pin.dataId = feature.properties.id;
            pin.dataType = dataInfo.dataType;
            return L.marker(latlng, {
                icon: pin
            });
        },
        pane: data.pane ?? "pinPane",
        onEachFeature: function(feature, layer) {
            addPopUpsToFeature(feature, layer, dataInfo);
            layer.customId = `${dataInfo.dataType}_${feature.properties.id}`;
            Layers[dataInfo.dataType].addLayer(layer);
        }           
    });
    // Layers[dataInfo.dataType].addLayer(points)

    map.addLayer(featureGroup)
    if (dataInfo.legendSettings) {
        addLegend(dataInfo.legendSettings)
      }
};

function createPropertiesTable(properties, dataInfo) {
    // console.log('createPropertiesTable', properties, dataInfo);
    let tableHTML = `
    <div class="col-4 g-3 mb-1">
        <table class="${dataInfo.dataType} table-sm table-bordered properties-table">
        <tr><td colspan="2"><h5>${dataInfo?.tableCaption}</h5></td></tr>
        <tbody>`;
    dataInfo.properties.forEach(property => {
            if (property.table) {
                tableHTML += `
                    <tr>
                        <th><h6>${property.title}</h6></th>
                        <td>
                    `;
                    const value = properties ? properties[property.valueName] : null;
                    if (value !== undefined && value !== null){
                        tableHTML += `${value} ${property.unit ?? ''}` 
                    } else {
                        tableHTML += `--` 
                    }
                    tableHTML += `
                        </td>
                </tr>
                `;
            }
        })
    tableHTML += `</tbody></table></div>`;
    return tableHTML;
};

export function createSinkResultTable(data) {
    // used in zalf sinks and sieker sinks
    console.log('createSinkResultTable data', data);

    const inlets = data.inlets;
    const dataInfo = data.dataInfo;
    const ProjectClass = projectClasses[dataInfo.dataType];
    const project = ProjectClass.loadFromLocalStorage();
    const selected_items = project[`selected_${dataInfo.dataType}s`];
    project[`selected_${dataInfo.dataType}s`] = [];
    project[`all_${dataInfo.dataType}_ids`] = [];

    const tableContainer = document.getElementById(`${dataInfo.dataType}-table-container`);
    console.log('Data_type for table', dataInfo.dataType);

    // Build table HTML (only main header rows)
    let tableHTML = `
        <table class="table detail-table" id="${dataInfo.dataType}-table">
        <thead>
            <tr>`;
    dataInfo.properties.forEach(property => {
        if (property.table) {
            if (property.valueName === 'id') {
                tableHTML += `
                <th>
                    <div class="form-check form-switch m-0">
                    <input type="checkbox" 
                        class="form-check-input table-select-all switch-input"  
                        data-type="${dataInfo.dataType}" 
                        checked="">
                    </div>
                </th>`; // for checkbox
            } else {
                tableHTML += `<th>${property.title}</th>`;
            }
        }
    });
    tableHTML += '</tr></thead><tbody>';

    // Main rows (inlet-header-row)

    inlets.forEach(inlet => {
        const resultSinkId = `${dataInfo.dataType}_${inlet.sink_type}_${inlet.sink_id}`
        project[`all_${dataInfo.dataType}_ids`].push(resultSinkId);

        tableHTML += `<tr class="inlet-header-row table-parent-row" data-id="${inlet.id}" data-type="${dataInfo.dataType}" waterbody-type="${inlet.waterbody_type}" waterbody-id="${inlet.waterbody_id}">`;

        dataInfo.properties.forEach(property => {
            if (property.table) {
                if (property.valueName === 'id') {
                    tableHTML += `
                        <td>
                            <div class="form-check form-switch m-0">
                                <input type="checkbox" 
                                    class="form-check-input table-select-checkbox toggle-sink-result"  
                                    data-type="${dataInfo.dataType}" 
                                    data-id="${resultSinkId}"
                                    inlet-id="${dataInfo.dataType}_inlet_${inlet.id}" 
                                    sink-id="${resultSinkId}"
                                    sink-embankment-id="${inlet.sink_embankment_id ? 'sink_embankment_' + inlet.sink_embankment_id : ''}"
                                    checked="">
                            </div>
                        </td>`;
                } else {
                    const value = inlet[property.valueName];
                    tableHTML += `<td data-order="${value ?? 0}">${value ?? '--'} ${property.unit ?? ''}</td>`;
                }
            }
        });
        tableHTML += '</tr>';
    });
      
    tableHTML += `</tbody></table>`;
    tableContainer.innerHTML = tableHTML;

    // Save selected items back to local storage
    if (selected_items.length === 0) {
        project[`selected_${dataInfo.dataType}s`] = project[`all_${dataInfo.dataType}_ids`] ?? [];
    } else {
        project[`selected_${dataInfo.dataType}s`] = selected_items.filter(resultId =>
            project[`all_${dataInfo.dataType}_ids`]?.includes(resultId)
        );
    }
    tableCheckSelectedItems(project, dataInfo.dataType);


    project.saveToLocalStorage();

    // Initialize DataTable
    const tableSettings = createTableSettings(dataInfo);
    const table = $(`#${dataInfo.dataType}-table`)
    const dataTable = table.DataTable(tableSettings);
    
    // Attach child rows (detail rows: sink, waterbody, inlet tables + chart)
    inlets.forEach(inlet => {
        const mainRow = dataTable.row($(`tr.inlet-header-row[data-id="${inlet.id}"]`));
        let sinkDataInfo, waterbodyDataInfo;

        
        if (inlet.sink_type === 'enlarged_sink') sinkDataInfo = data.sinkDataInfo.enlarged_sink;
        else sinkDataInfo = data.sinkDataInfo.sink;

        if (inlet.waterbody_type === 'lake') waterbodyDataInfo = data.waterbodyDataInfo.lake;
        else if (inlet.waterbody_type === 'stream') waterbodyDataInfo = data.waterbodyDataInfo.stream;

        const sinkTable = createPropertiesTable(inlet.sink, sinkDataInfo);
        const waterbodyTable = createPropertiesTable(inlet.waterbody, waterbodyDataInfo);
        const inletTable = createPropertiesTable(inlet, data.inletDataInfo);

        const detailHtml = `
            <div class="container-fluid overflow-auto">
                <div class="row mb-2">
                    ${sinkTable}                   
                    ${waterbodyTable}           
                    ${inletTable}
                </div>
                <div class="row">
                    <div class="col-12 chart-container">
                        <canvas id="inlet-chart-${inlet.id}" class="inlet-chart"></canvas>
                    </div>
                </div>
            </div>`;

        // Attach child row and hide initially
        mainRow.child(detailHtml).hide();     
    });

    if (table.length && table.is(':visible')) {
        try {
            table.resizableColumns();
        } catch (e) {
            console.warn("ResizableColumns failed:", e);
        }
    }

    $(`#card-${dataInfo.dataType}-table`).removeClass('d-none');
}


export function addFeatureCollectionToTable(data) {
    const featureCollection = data.featureCollection;
    const dataInfo = data.dataInfo;
    const tableClasses = data.tableClasses ?? "table table-hover"
    const rowClasses = data.rowClasses ?? "";
    const switchInput = data.switchInput ?? false

    const ProjectClass = projectClasses[dataInfo.dataType];
    const project = ProjectClass.loadFromLocalStorage();
    const selected_items = project[`selected_${dataInfo.dataType}s`];

    project[`selected_${dataInfo.dataType}s`] = [];
    project[`all_${dataInfo.dataType}_ids`] = [];

    const tableContainer = document.getElementById(`${dataInfo.dataType}-table-container`);

    // ---- TABLE ELEMENTS ----
    const table = document.createElement("table");
    table.className = tableClasses;
    table.id = `${dataInfo.dataType}-table`;

    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");

    // ---- BUILD THEAD ----
    dataInfo.properties.forEach(property => {
        if (property.table) {
            const th = document.createElement("th");

            if (property.valueName === "id") {
                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.className = "table-select-all form-check-input";
                checkbox.dataset.type = dataInfo.dataType;

                const label = document.createElement("label");
                label.className = "form-check-label ms-1";
                label.appendChild(checkbox);
                label.append(" Alle"); 

                th.appendChild(label);
                
            } else {
                th.textContent = property.title;
            }

            headRow.appendChild(th);
        }
    });

    thead.appendChild(headRow);

    // ---- TBODY ----
    const tbody = document.createElement("tbody");

    featureCollection.features.forEach(feature => {
        const id = String(feature.properties.id);
        project[`all_${dataInfo.dataType}_ids`].push(id);

        const row = document.createElement("tr");
        row.className = rowClasses;
        row.dataset.id = id;
        row.dataset.type = dataInfo.dataType;

        const color = dataInfo.colorByIndex
            ? tableColorFunction(feature.properties[dataInfo.colorByIndex])
            : "";

        row.dataset.baseColor = color;

        // ---- BUILD ROW CELLS ----
        dataInfo.properties.forEach(property => {
            if (!property.table) return;

            const td = document.createElement("td");

            if (property.valueName === "id") {
                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.className = "table-select-checkbox form-check-input";
                checkbox.dataset.type = dataInfo.dataType;
                checkbox.dataset.id = id;
                td.appendChild(checkbox);
            } else {
                const value = feature.properties[property.valueName];

                if (value !== undefined && value !== null) {
                    td.dataset.order = value;
                    td.textContent = `${value} ${property.unit ?? ""}`;
                } else {
                    td.dataset.order = "0";
                    td.textContent = "--";
                }
            }
            row.appendChild(td);
        });
        tbody.appendChild(row);
    });

    // ---- ASSEMBLE TABLE ----
    table.appendChild(thead);
    table.appendChild(tbody);

    // Clear container & insert table
    tableContainer.innerHTML = "";
    tableContainer.appendChild(table);

    // ---- Restore selection ----
    project[`selected_${dataInfo.dataType}s`] = selected_items
        .filter(id => project[`all_${dataInfo.dataType}_ids`].includes(id));

    project.saveToLocalStorage();

    // ---- DATATABLE INIT + coloring ----
    const tableSettings = createTableSettings(dataInfo);
    const dataTable = $(`#${dataInfo.dataType}-table`).DataTable(tableSettings);
    

    colorTable(dataInfo.dataType);


    if ($(`#${dataInfo.dataType}-table`).length && $(`#${dataInfo.dataType}-table`).is(':visible')) {
        try {
            $(`#${dataInfo.dataType}-table`).resizableColumns();
        } catch (e) {
            console.warn("ResizableColumns failed:", e);
        }
    }
    return dataTable;
}

export function createDetailRows(table, featureCollection, dataInfo, callback) {
    featureCollection.features.forEach(feature => {
        const mainRow = table.row($(`tr.table-parent-row[data-id="${feature.properties.id}"]`))
        console.log('mainRow',  mainRow)
        const detailHtml = callback(dataInfo, feature.properties)
        mainRow.child(detailHtml).hide();
        console.log('childrow created')    
        });


    $(`#card-${dataInfo.dataType}-table`).removeClass('d-none');
    const dataTable = $(`#${dataInfo.dataType}-table`);

    if (dataTable.length && dataTable.is(':visible')) {
        try {
            dataTable.resizableColumns();
        } catch (e) {
            console.warn("ResizableColumns failed:", e);
        }
    }
}


function colorTable(dataType) {
    document.querySelectorAll(`#${dataType}-table tbody tr`).forEach(row => {
        const base = row.dataset.baseColor;
        if (base) row.style.setProperty("--bs-table-bg", base);
        });
        
        $(`#card-${dataType}-table`).removeClass('d-none')
    };

export function clearAndRemoveTable(ProjectClass, dataType, message) {
    console.log('clearAndRemove dataType:', dataType, 'Class:', ProjectClass, 'msg', message)
    const project = ProjectClass.loadFromLocalStorage();
    const tableContainer = document.getElementById(`${dataType}-table-container`);
    tableContainer.innerHTML = `<h6>${message}</h6>`;
    $(`#card-${dataType}-table`).removeClass('d-none')

    project[`all_${dataType}_ids`] = [];
    project.saveToLocalStorage();

}

export function addLegendForWms(wmsLayerName) {
    const wmsUrl = '/toolbox/proxy/wms/';
  const legend = L.control.Legend({
    position: "bottomleft"
  });
  legend.onAdd = function (map) {
      var div = L.DomUtil.create("div", "leaflet-legend leaflet-bar");
      var url = `${wmsUrl}?REQUEST=GetLegendGraphic&VERSION=1.1.1&FORMAT=image/png&LAYER=${wmsLayerName}`;
       
      div.innerHTML +=
        "<img src=" +
        url +
        ' alt="legend" data-toggle="tooltip" title="Map legend">';
      return div;
    };
  legend.addTo(map)
};

export function getTileOverlay(wmsLayer, layersName, toolTag) {
    const wmsUrl = '/toolbox/proxy/wms/';
    if (Layers[layersName]) {
        Layers[layersName].remove()
        removeLegendFromMap(map)
    }
  Layers[layersName] = L.tileLayer.wms(wmsUrl, {
    layers: wmsLayer,
    pane: 'overlayRasterPane',
    format: "image/png",
    transparent: true,
    tileSize: 256,   
    keepBuffer: 10,  
    updateWhenZooming: false, // don’t request tiles mid-zoom
    _t: Date.now() // this is only a cache buster - necessary to alter request 
    }).addTo(map);
    Layers[layersName].toolTag = toolTag
};

export function getTileOverlayWithThreshold(wmsLayer, layersName, toolTag, threshold) {
    const wmsUrl = '/toolbox/proxy/wms_sld/';
    if (Layers[layersName]) {
        Layers[layersName].remove()
        // removeLegendFromMap(map)
    }
  Layers[layersName] = L.tileLayer.wms(wmsUrl, {
    layers: wmsLayer,
    pane: 'overlayRasterPane',
    format: "image/png",
    transparent: true,
    threshold: threshold,
    tileSize: 256,   
    keepBuffer: 10,  
    updateWhenZooming: false, // don’t request tiles mid-zoom
    _t: Date.now() // this is only a cache buster - necessary to alter request 
    }).addTo(map);
    Layers[layersName].toolTag = toolTag
};



function getInletVolumeChart(waterbodyType, waterbodyId, inletId) {
    // 
    console.log('getInletVolumeChart', waterbodyType, waterbodyId, inletId)
    // const spinner = document.querySelector('#inletChartSpinnerWrapper'); 
    const canvas = document.getElementById(`inlet-chart-${inletId}`);
    // const observer = new MutationObserver((mutations) => {
    //     mutations.forEach(mutation => {
    //         console.log('Mutation:', mutation);
    //     });
    //     });
    // observer.observe(canvas, { attributes: true });                                                         



    if (Chart.getChart(canvas)) {
        console.log(`Canvas inlet-chart-${inletId} is already in use. Skipping.`);
        return; // Do nothing
    };
    if (!canvas){return;}
    const ctx = canvas.getContext('2d');
    fetch(`get_injection_volume_chart/${waterbodyType}/${waterbodyId}/`)
    .then(response => response.json())
    .then(data => {
        console.log('Chart data', data);
        const chartData = data.chart_data;

        const deLocale = dateFns.locale?.de;


        // let inletVolumeChart = new Chart(ctx, {
        //   type: 'bar',
        //   data: { 
        //     datasets: [{ 
        //       label: 'Abfluss (m³/s)', 
        //       data: chartData ,
        //       backgroundColor: 'rgb(54, 162, 235 )',   // DodgerBlue, fully opaque
        //       borderColor: 'rgb(54, 162, 235 )',
        //       hoverBackgroundColor: 'rgb(54, 162, 235 )', // DodgerBlue, semi-transparent
        //       borderWidth: 1
        //     }] 
        //   },
        //   options: {
        //     transitions: {
        //         active: {
        //             animation: {
        //             duration: 0 // disables fade animation
        //             }
        //         }
        //     },
        //     transitions: {
        //         active: {
        //             animation: {
        //             duration: 0
        //             }
        //         }
        //     },

        //     interaction: {
        //         mode: 'nearest',
        //         intersect: true,
        //     },
        //     plugins: {
        //         tooltip: {
        //             enabled: true,
        //             },
                
        //     },
        //     elements: {
        //         bar: {
        //         backgroundColor: 'rgb(54, 162, 235)',
        //         hoverBackgroundColor: 'rgb(54, 162, 235)',  // stays same on hover
        //         borderSkipped: false,
        //         hoverStyle: false,
        //         }
        //     },
            

        //     responsive: true,
        //     // aspectRation:4,
        //     maintainAspectRatio: false,
        //     scales: {
        //       x: {
        //         type: 'time',
        //         adapters: { date: { locale: deLocale } },
        //         time: { unit: 'month', displayFormats: { month: 'MM-yyyy' } },
        //         title: { display: true, text: 'Datum' }
        //       },
        //       y: {
        //         beginAtZero: true,
        //         title: { display: true, text: 'Abfluss (m³/s)' }
        //       }
        //     }
        //   }
        // })

        let inletVolumeChart = new Chart(ctx, {
        type: 'bar',
        backgroundColor: 'rgb(54,162,235)',
        data: {
            datasets: [{
            label: 'Abfluss (m³/s)',
            data: chartData,        
            }]
        },
        options: {

            transitions: {
            active: {
                animation: { duration: 0 } // disable active transition
            }
            },


            responsive: true,
            maintainAspectRatio: false,

            scales: {
            x: {
                type: 'time',
                adapters: { date: { locale: deLocale } },
                time: { unit: 'month', displayFormats: { month: 'MM-yyyy' } },
                title: { display: true, text: 'Datum' }
            },
            y: {
                beginAtZero: true,
                title: { display: true, text: 'Abfluss (m³/s)' }
            }
            }
        }
        });

    });

};

