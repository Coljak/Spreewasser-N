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

    'sieker_wetland': SiekerWetland,

    'sieker_sink': SiekerSink,
    'sieker_lake': SiekerSink,
    'sieker_stream': SiekerSink,
    'sieker_sink_result': SiekerSink,
    'sieker_sink_result_sink': SiekerSink,
    'sieker_sink_result_inlet': SiekerSink,

    'sieker_surface_water': SiekerSurfaceWaters,
    'sieker_water_level': SiekerSurfaceWaters,
    
    'drainage': Drainage,
};

function toggleValueInArray(list, val) {
  const index = list.indexOf(val);
  if (index > -1) {
    list.splice(index, 1); // remove
  } else {
    list.push(val); // add
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
    }  else {
      // TODO clear layers
      clearAndRemoveTable(ProjectClass, dataType, data.message.message)
      handleAlerts(data.message);
    } 
  })
  .catch(error => console.error("Error fetching data:", error))
  .finally(() => {
    // Always hide spinner & enable button
    spinner.hide();
    $button.prop('disabled', false);
  });
};

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
    console.log('tableCheckSelectedItems behind first if: ', dataType)
    const checkboxes = document.querySelectorAll(`.table-select-checkbox[data-type="${dataType}"]`)
    checkboxes.forEach(checkbox => {
        const checked = project[`selected_${dataType}s`].includes(Number(checkbox.dataset.id)) ? true : false;
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
                radius: 5,
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
            console.log("eventListener change ($target.hasClass('form-check-input')")
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

            // in case checkable Popup is open
            try {
                const checkbox = document.querySelector(`.select-map-feature-checkbox[data-type="${dataType}"][data-id="${$target.data('id')}"]`);
                checkbox.checked = $target.is(':checked');
            } catch  {;};

            toggleValueInArray(project[key], $target.data('id'));
            project.saveToLocalStorage();
            return;
        // } else if ($target.hasClass('toggle-sink-result')) {
        //     const dataType = $target.data('type');
        //     const inletId = `${dataType}_${$target.data('id')}` 
        //     const layerId = `${dataType}_${$target.attr('layer-id')}` 
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

export function loadProjectToGui(project) {

    console.log('loadProjectToGui', project);
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
    // these checkboxes are in drainage network
    if ($checkboxes.length) {
        $checkboxes.each(function () {
            // console.log('checkbox this', this)
            const $checkbox = $(this);
            const val = $checkbox.val();
            const key = $checkbox.attr('prefix') + '_' + $checkbox.attr('name');
            console.log('checkbox val key', val, key)
            
            $checkbox.prop('checked', project[key].includes(val));

        });
    }

    
    for (const [key, value] of Object.entries(project)) {
        if (key.startsWith('all_') && key.endsWith('_ids') && value.length > 0) {
            const name = key.replace('all_', '').replace('_ids', '');
            if (!project.toolboxType === 'sieker_surface_water') {
                $(`button.filter-features[data-type="${name}"]`).trigger('click')
            } else {
                if (project.sieker_surface_water_filtered === false){
                    tableCheckSelectedItems(project, 'sieker_surface_water')
                } else {
                    $(`button.filter-features[data-type="${name}"]`).trigger('click')
                }
                tableCheckSelectedItems(project, 'sieker_water_level')
                        
            }
                     
        }
    }
                
};

export function clearToolboxPanel(){
    $('#toolboxButtons').removeClass('d-none');
    $('#toolboxPanel').html('') 
    $('#toolboxPanel').addClass('d-none');
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
        const $target = $(event.target);
        const project = ProjectClass.loadFromLocalStorage();
        if ($target.hasClass('toolbox-back-to-initial')) {
            clearToolboxPanel();
            return;
        // table related
        } else if ($target.hasClass('toggle-tile-layer')) {
            console.log('toggle-tile-layer')
              const dataType = $target.data('type')
              if ($target.hasClass('shown')) {
                $('button.toggle-tile-layer').removeClass('shown');
                $('button.toggle-tile-layer').text('einblenden')
                document.querySelector('.leaflet-overlayRaster-pane').hidden = true;
                document.querySelector('.leaflet-legend').hidden = true; 
              } else {
                $('button.toggle-tile-layer').text('ausblenden')
                $('button.toggle-tile-layer').addClass('shown');
                
                document.querySelector('.leaflet-overlayRaster-pane').hidden = false;
                document.querySelector('.leaflet-legend').hidden = false; 
                $target.addClass('shown')
              }
              
            } else if ($target.hasClass('paginate_button' || $target.hasClass('sorting'))) {
            console.log('Paginate')
            const dataType =  $target.attr('aria-controls').split('-')[0];
            tableCheckSelectedItems(project, dataType)
            return;
        } else if ($target.closest('tr').length && !$target.is('input, button, a')) {
            const $row = $target.closest('tr');
            const $dataType = $row.data('type')
            const $id = $row.data('id')
             console.log('Tablerow: ', $dataType, $row.data('id'))
            if ($dataType === 'filtered_sieker_gek') {
                
                openResultCard($dataType, $id)
            } else if ($row.hasClass('inlet-header-row')) {
                console.log('Tablerow: ', $dataType, $row.data('id'))
                const $detailRow = $row.next('.detail-row'); 
                $detailRow.toggle(200); 
            }
            return;

        } else if ($target.hasClass('toggle-feature-group')) {
            
            const dataType = $target.attr('data-type')
            console.log('toggle-feature-group', dataType)
            
            if (map.hasLayer(Layers[dataType])) {
                map.removeLayer(Layers[dataType]);
                $target.text('einblenden');
            } else {
                map.addLayer(Layers[dataType]);
                $target.text('ausblenden');
            }
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
            const project_id = $('#id_toolbox_project').val();
            const loadedProject = loadProjectFromDb(project_id);
            loadedProject.then(project => {
                console.log('Loaded project:', project);
                loadProjectToGui(project);
                // necessary for drainage
                // $('input[type="checkbox"]').trigger('change');

            });
        } else if ($target.hasClass('filter-waterbodies')) {
            console.log('Click eventlistener filter-waterbodies')
            getWaterBodies($target, ProjectClass);  
        } 
    });
};

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
        "columnDefs": columnDefs
    }
};

const colorFunction = function (index) {
    console.log('colorFunction index:', index)
    let hue;
    // if the index is an integer, it has a value of 0-100, if not it is 0.0-1.0
    if (Number.isInteger(index)){
       hue  = index
    } else {
        hue  = index * 100
    }
  
  let color = `hsl(${hue}, 90%, 50%)`;
  console.log('colorFunction, color: ', color)
  return color
};

function getLayerByCustomId(layerGroup, customId) {
  let found = null;
  layerGroup.eachLayer(layer => {
    if (layer.customId === customId) found = layer;
  });
  return found;
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
            const isSelected = project[`selected_${dataInfo.dataType}s`].includes(feature.properties.id);
            console.log('isSelected', isSelected);
            checkbox.checked = isSelected;
        }
        
        
    });


        
    
}


export function addFeatureCollectionToLayer(data, clearLayer, resultMap={}){
    console.log('addFeatureCollectionToLayer dataInfo', data.dataInfo)
    console.log('addFeatureCollectionToLayer dataInfo.colorByIndex', data.dataInfo.colorByIndex)
    
    let featureCollection = data.featureCollection;
    let dataInfo = data.dataInfo;  
    let colorByIndex = dataInfo.colorByIndex ? dataInfo.colorByIndex : false
    
    const featureGroup = Layers[dataInfo.dataType]
    if (clearLayer) {
        featureGroup.clearLayers();
    }
    

    let geojsonLayer = L.geoJSON(featureCollection, {
        style: function (feature) {
            let color = colorByIndex
                ? colorFunction(feature.properties[colorByIndex])
                : dataInfo.featureColor;

            const style = {
                className: dataInfo.className,
                weight: 3,
            };
            if (dataInfo.featureType === "polygon" && colorByIndex) {
                style.fillColor = color;                  // dynamic fill
                style.color = dataInfo.featureColor;      // outline color
                style.fillOpacity = 0.7;                 // optional
            }
            // CASE 2: everything else
            else {
                style.color = color;
                // style.fillColor = color;
            }

            if (dataInfo.dashArray) {
                style.dashArray = dataInfo.dashArray;
            }
            return style;
        },
        pane: "polygonPane",
        onEachFeature: function(feature, layer) {
            addPopUpsToFeature(feature, layer, dataInfo);

            resultMap[`${dataInfo.dataType}_${feature.properties.id}`] = layer;

            // layer.customId = `${dataInfo.dataType}_${feature.properties.id}`;
            console.log('feature properties: ', feature.properties);
            Layers[dataInfo.dataType].addLayer(layer);
            console.log('layer ids:', `${dataInfo.dataType}_${feature.properties.id}`);
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
        pane: "polygonPane",
        onEachFeature: function(feature, layer) {
            addPopUpsToFeature(feature, layer, dataInfo);
            layer.customId = `${dataInfo.dataType}_${feature.properties.id}`;
            console.log('customId:', `${dataInfo.dataType}_${feature.properties.id}`)
            Layers[dataInfo.dataType].addLayer(layer);
            console.log('layer ids:', `${dataInfo.dataType}_${feature.properties.id}`)
        }           
    });
    // Layers[dataInfo.dataType].addLayer(points)

    map.addLayer(featureGroup)
    if (dataInfo.legendSettings) {
        addLegend(dataInfo.legendSettings)
      }
};


export function createResultTable( data ){

    const inlets = data.inlets;
    const dataInfo = data.dataInfo;
    const ProjectClass = projectClasses[dataInfo.dataType];
    const project = ProjectClass.loadFromLocalStorage();
    const selected_items = project[`selected_${dataInfo.dataType}s`];
    project[`selected_${dataInfo.dataType}s`] = [];
    
    project[`all_${dataInfo.dataType}_ids`] = [];

    const tableContainer = document.getElementById(`${dataInfo.dataType}-table-container`);
    let tableHTML = `
        <table class="table table-bordered table-hover result-table" id="${dataInfo.dataType}-table">
        <caption>${dataInfo.tableCaption}</caption>
        <thead>
            <tr>`;
            dataInfo.properties.forEach(property => {
                if (property.table) {
            if (property.valueName === 'id') {
                tableHTML += `
                <th>
                    <div class="form-check form-switch m-0"">
                        <input type="checkbox" class="form-check-input table-select-all"  data-type="${dataInfo.dataType}" checked="">
                    </div>
                </th>`;
            } else {
                tableHTML += `<th>${property.title}`
            }
        }
        });
    tableHTML += '</tr></thead><tbody>';
    

    inlets.forEach(inlet => {
        console.log('Create table inlet', inlet)
        project[`all_${dataInfo.dataType}_ids`].push(inlet.id)        
        // Add to table
        tableHTML += `
            <tr data-id="${inlet.id}" data-type="${dataInfo.dataType}" class="inlet-header-row">`    
        dataInfo.properties.forEach(property => {
            if (property.table) {
                if (property.valueName === 'id') {
                tableHTML += `
                    <td>
                        <div class="form-check form-switch m-0">
                            <input type="checkbox" 
                            class="form-check-input table-select-checkbox toggle-sink-result"  
                            data-type="${dataInfo.dataType}" 
                            inlet-id="${dataInfo.dataType}_inlet_${inlet.id}" 
                            sink-id="${dataInfo.dataType}_${inlet.sink_type}_${inlet.sink_id}" 
                            checked="">
                        </div>
                    </td>
                    `;
                } else {
                    const value = inlet[property.valueName];
                    if (value !== undefined && value !== null){
                        tableHTML += `<td data-order="${value}">${value} ${property.unit ?? ''}</td>` 
                    } else {
                        tableHTML += `<td data-order="0">--</td>` 
                    }
                }
            }
        });
        tableHTML += '</tr>';
        // details and chart row

        tableHTML += `
        <tr class="detail-row" data-id="${inlet.id}" style="display:none;">
            <td colspan="${dataInfo.properties.filter(p => p.table).length}">
                <div class="container-fluid">
                    <div class="row mb-2">
                        <div class="col-md-4">
                            <!-- Table 1 -->
                            <table class="table table-sm table-bordered"> 
                            
                             </table>
                        </div>
                        <div class="col-md-4">
                            <!-- Table 2 -->
                            <table class="table table-sm table-bordered"> ... </table>
                        </div>
                        <div class="col-md-4">
                            <!-- Table 3 -->
                            <table class="table table-sm table-bordered"> ... </table>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <canvas id="chart-${inlet.id}"></canvas>
                        </div>
                    </div>
                </div>
            </td>
        </tr>
    `;
        });
    tableHTML += `</tbody></table>`;
    tableContainer.innerHTML = tableHTML;
    // select all previously selected
    console.log('addFeatureCollection dataType', dataInfo.dataType )
    project[`selected_${dataInfo.dataType}s`] = selected_items.filter(sink => project[`all_${dataInfo.dataType}_ids`].includes(sink));
    project.saveToLocalStorage();

    // const tableSettings = createTableSettings(dataInfo);
    // $(`#${dataInfo.dataType}-table`).DataTable(tableSettings);
    
    $(`#card-${dataInfo.dataType}-table`).removeClass('d-none')
};

export function addSinkConnectionResult(feature, dataInfo) {
    const layer= '';

}
///////////////////////////////////////////////////////
export function addFeatureCollectionToTable( data ){
    const featureCollection = data.featureCollection
    const dataInfo = data.dataInfo
    const ProjectClass = projectClasses[dataInfo.dataType]
    const project = ProjectClass.loadFromLocalStorage()
    const selected_items = project[`selected_${dataInfo.dataType}s`];
    project[`selected_${dataInfo.dataType}s`] = [];
    
    project[`all_${dataInfo.dataType}_ids`] = [];

    const tableContainer = document.getElementById(`${dataInfo.dataType}-table-container`);
    let tableHTML = `
        <table class="table table-bordered table-hover" id="${dataInfo.dataType}-table">
        <caption>${dataInfo.tableCaption}</caption>
        <thead>
            <tr>`;
    dataInfo.properties.forEach(property => {
        if (property.table) {
            if (property.valueName === 'id') {
                tableHTML += `<th><input type="checkbox" class="table-select-all" data-type="${dataInfo.dataType}"> Alle</th>`;
            } else {
                tableHTML += `<th>${property.title}`
            }
        }
        });
    tableHTML += '</tr></thead><tbody>';
    

    featureCollection.features.forEach(feature => {
        project[`all_${dataInfo.dataType}_ids`].push(feature.properties.id)
        
        // Add to table
        tableHTML += `
            <tr data-id="${feature.properties.id}" data-type="${dataInfo.dataType}">`

        
        dataInfo.properties.forEach(property => {
            if (property.table) {
                if (property.valueName === 'id') {
                tableHTML += `
                    <td><input type="checkbox" class="table-select-checkbox" data-type="${dataInfo.dataType}" data-id="${feature.properties.id}"></td>
                    `;
                } else {
                    const value = feature.properties[property.valueName];
                    if (value !== undefined && value !== null){
                        tableHTML += `<td data-order="${value}">${value} ${property.unit ?? ''}</td>` 
                    } else {
                        tableHTML += `<td data-order="0">--</td>` 
                    }
                }
            }
        });
        tableHTML += '</tr>';
        });
    tableHTML += `</tbody></table>`;
    tableContainer.innerHTML = tableHTML;
    // select all previously selected
    console.log('addFeatureCollection dataType', dataInfo.dataType )
    project[`selected_${dataInfo.dataType}s`] = selected_items.filter(sink => project[`all_${dataInfo.dataType}_ids`].includes(sink));
    project.saveToLocalStorage();

    const tableSettings = createTableSettings(dataInfo);
    $(`#${dataInfo.dataType}-table`).DataTable(tableSettings);
    
    $(`#card-${dataInfo.dataType}-table`).removeClass('d-none')
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







