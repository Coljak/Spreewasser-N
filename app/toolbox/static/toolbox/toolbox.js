import { getGeolocation, handleAlerts, getCSRFToken, saveProject, observeDropdown,  setLanguage, populateDropdown } from '/static/shared/utils.js';
import {Infiltration} from '/static/toolbox/infiltration_model.js';
import {SiekerGek} from '/static/toolbox/sieker_gek_model.js';
import {SiekerSink} from '/static/toolbox/sieker_sink_model.js';
import {SiekerSurfaceWaters} from '/static/toolbox/sieker_surface_waters_model.js';
import {SiekerWetland} from '/static/toolbox/sieker_wetland_model.js';
import {map, removeLegendFromMap} from '/static/shared/map_sidebar_utils.js';
import {Layers} from '/static/toolbox/layers.js';


const projectClasses = {
    'sink': Infiltration,
    'enlarged_sink': Infiltration,
    'stream': Infiltration,
    'lake': Infiltration,
    // 'gek': SiekerGek,
    'filtered_sieker_gek': SiekerGek,
    'sieker_wetland': SiekerWetland,
    'sieker_sink': SiekerSink,
    'sieker_large_lake': SiekerSurfaceWaters,
    'sieker_water_level': SiekerSurfaceWaters,
    'sieker_gek': SiekerGek,
}

function toggleNumberInArray(list, num) {
  const index = list.indexOf(num);
  if (index > -1) {
    list.splice(index, 1); // remove
  } else {
    list.push(num); // add
  }
  return list;
}

// TODO I think      this is not working!
$('#map').on('click', function (event) {
    if (event.target.classList.contains('select-map-feature-button')) {
    const dataType = event.target.getAttribute('data-type');
    const dataId = event.target.getAttribute('data-id');
    console.log('select-map-feature-button', dataType, 'ID:', dataId);
        map.closePopup();

   try {     
    // the checkbox is not necessarily available
    const checkbox = document.querySelector(`.table-select-checkbox[data-type="${dataType}"][data-id="${dataId}"]`);
        checkbox.checked = !checkbox.checked;
    } catch {;}
    const project = projectClasses[dataType].loadFromLocalStorage()
    project[`selected_${dataType}s`] = toggleNumberInArray(project[`selected_${dataType}s`])
    project.saveToLocalStorage();
    }
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
    console.log('tableCheckSelectedItems', project)
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
}

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

export function addChangeEventListener(projectClass) {
    const CurrentProjectClass = projectClass;
    console.log(projectClass)
    $('#toolboxPanel').on('change', function (event) {
        const $target = $(event.target);
        const project = CurrentProjectClass.loadFromLocalStorage();
        // console.log('change event', $target);
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
        }else if ($target.hasClass('form-check-input')) {
            // checkboxes 
            console.log("Checkbox!!")
            const inputId = $target.attr('id');
            const inputName = $target.attr('name');
            const inputPrefix = $target.attr('prefix');
            const inputValue = $target.attr('value');
            const inputChecked = $target.is(':checked');

            const key = `${inputPrefix}_${inputName}`;
            console.log('key', key)
            console.log('project', project)
            
            const index = project[key].indexOf(inputValue);
            console.log('index', index)
            if (index > -1) {
                // Value exists — remove it
                project[key] = project[key].filter(
                (v) => v !== inputValue
                );
                console.log('Checkbox unchecked:', inputId, '=', inputValue);
            } else {
                // Value does not exist — add it; Dev purposes
                project[key].push(inputValue);
                console.log('Checkbox checked:', inputId, '=', inputValue);
            }
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

            if ($target.is(':checked')) {
                console.log("Selected Id:", $target.data('id'));
                console.log("key:", key);
                console.log('project[key]', project[key])
                console.log(project)
                project[key].push($target.data('id'));
                project.saveToLocalStorage();

            } else {
                const dataId = $target.data('id');
                console.log("Selected Id:", dataId);
                $('.table-select-all')[0].checked = false 
                const index = project[key].indexOf(dataId);
                if (index > -1) {
                    project[key].splice(index, 1);
                }
                project.saveToLocalStorage();
            }
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

export function addClickEventListenerToToolboxPanel(projectClass) {
    const ProjectClass = projectClass;
    $('#toolboxPanel').on('click',function (event) {
        const $target = $(event.target);
        const project = ProjectClass.loadFromLocalStorage();
        if ($target.hasClass('toolbox-back-to-initial')) {
            $('#toolboxButtons').removeClass('d-none');
                $('#toolboxPanel').addClass('d-none');
                removeLegendFromMap(map);
                map.eachLayer(function(layer) {
                    console.log(layer.toolTag);
                    if (layer.toolTag) {
                        map.removeLayer(layer);
                    }
                });
                return;
        // table related
        } else if ($target.hasClass('paginate_button')) {
            console.log('Paginate')
            const dataType = $('.table-select-all').data('type');
            tableCheckSelectedItems(project, dataType)
            return;
        } else if ($target.closest('tr').length && !$target.is('input, button, a')) {
            const $row = $target.closest('tr');
            const $dataType = $row.data('type')
            const $id = $row.data('id')
            console.log('Tablerow: ', $dataType, $row.data('id')) 
            if ($dataType === 'filtered_sieker_gek') {
                
                openResultCard($dataType, $id)
            }
            return;
        // actions
        } else if ($target.hasClass('filter-features')) {
            const dataType = $('.table-select-all').data('type');
            console.log('REFACTOR - continue here')
        } else if ($target.hasClass('toggle-feature-group')) {
            console.log('toggle-feature-group')
            const dataType = $target.attr('data-type')
            
            if (map.hasLayer(Layers[dataType])) {
                map.removeLayer(Layers[dataType]);
                $target.text('einblenden');
            } else {
                map.addLayer(Layers[dataType]);
                $target.text('ausblenden');
            }
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
    // index must be 0 <= index <= 1, 0 is red, 1 is green
    console.log('colorFunction index:', index)
  const hue = index * 100
  let color = `hsl(${hue}, 90%, 50%)`;
  console.log('colorFunction, color: ', color)
  return color
};

export function addFeatureCollectionToLayer(options){
    console.log('addFeatureCollectionToLayer')
    let selectable = true;
    
    let featureCollection = options.featureCollection;
    let dataInfo = options.dataInfo;
    
    let colorByIndex = dataInfo.colorByIndex ? dataInfo.colorByIndex : false
    console.log('addFeatureCollectionToLayer dataInfo', dataInfo)
    console.log('addFeatureCollectionToLayer dataInfo.colorByIndex', dataInfo.colorByIndex)
    const featureGroup = Layers[dataInfo.dataType]
    featureGroup.clearLayers();
    // console.log('featureGroup', featureGroup)
    // console.log('featureCollection', featureCollection)
    let layer = L.geoJSON(featureCollection, {
        style: function (feature) {
            let color;

            if (colorByIndex) {
                console.log('addFeatureCollectionToLayer feature.properties[colorByIndex]', feature.properties[colorByIndex])
                color = colorFunction(feature.properties[colorByIndex]);
            } else {
                color = dataInfo.featureColor;
            }

            return {
                color,
                className: dataInfo.className,
            };
        },
        onEachFeature: function (feature, layer) {
            console.log('onEachFeature:', feature)
            let popupContent = '';
            if (feature.properties[dataInfo.popUp.header]) {
                popupContent += `<h6><b> ${feature.properties[dataInfo.popUp.header]}</b></h6>`;
            }
            dataInfo.properties.forEach(property => {
                if (property.popUp) { 
                    popupContent += property.href
                    ? `<a href="${feature.properties[property.valueName]}" target="_blank">${property.title}</a><br>`
                    : `<b>${property.title}:</b> ${feature.properties[property.valueName] ?? '-'} ${feature.properties[property.valueName] ? property.unit ?? '' : ''}<br>
                        `;
                    }    
            });
            // layer.bindTooltip(popupContent);
            
                    
            
            // layer.on('mouseover', function () {
            //     // this.setStyle(highlightStyle);
            //     this.openTooltip();
            // });
            const popupOptions = {
                offset: [0, -30],   // shift popup upwards
                autoPan: false      // don’t auto-pan map on hover
            };

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
    
            layer.on('mouseout', function () {
                // Only reset to default if not clicked
                if (!this.options.isClicked) {
                    // this.setStyle(defaultStyle);
                }
            });

            if (selectable) {
                let menuContent = popupContent + `<button class="btn btn-outline-secondary select-map-feature-button" data-type=${dataInfo.dataType} data-id="${feature.properties.id}">Auswählen</button>`;  
    
                layer.on('click', function (e) {
                    // Remove clicked from all
                    const popUp = L.popup().setContent(menuContent);
                    map.openPopup(popUp, layer.getBounds().getCenter());
                    document.querySelectorAll('.polygon.clicked')
                    .forEach(el => el.classList.remove('clicked'));

                // Add to this one
                let pathEl = e.target._path; // The actual SVG path element
                if (pathEl) {
                    pathEl.classList.add('clicked');
                }
                });
            }
            layer.on('add', function () {
                if (layer._path) {
                    layer._path.setAttribute('data-type', dataInfo.dataType);
                    layer._path.setAttribute('data-id', feature.properties.id);
                }
            });
            layer.addTo(featureGroup);
        }
        });
  
    // let layerGroup = L.featureGroup([layer]).addTo(map);
    if (dataInfo.legendSettings) {
        addLegend(dataInfo.legendSettings)
      }
    
    featureGroup.addTo(map);
    layer.bringToFront();
};


export function addPointFeatureCollectionToLayer(options) {

    console.log(options)
    let featureCollection = options.featureCollection 
    let dataInfo = options.dataInfo
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
        onEachFeature: function (feature, layer) {
            let popupContent = '';
            if (feature.properties[dataInfo.popUp.header]) {
                popupContent += `<h6><b> ${feature.properties[dataInfo.popUp.header]}</b></h6>`;
            }
            dataInfo.properties.forEach(property => {
                if (property.popUp) { 
                    popupContent += property.href
                    ? `<a href="${feature.properties[property.valueName]}" target="_blank">${property.title}</a><br>`
                    : `<b>${property.title}:</b> ${feature.properties[property.valueName] ?? '-'
                        } ${feature.properties[property.valueName] ? property.unit ?? '' : ''}<br>`;
                }
            });

            let popupClickContent = popupContent + `
                <button class="btn btn-outline-secondary select-map-feature-button" 
                    data-type="${dataInfo.dataType}" 
                    data-id=${feature.properties.id}>
                    Auswählen
                </button>
            `;

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

            // Show persistent popup on click
            layer.on('click', function (event) {
                // close any hover popup first
                map.closePopup();

                L.popup(popupOptions)
                    .setLatLng(event.latlng)
                    .setContent(popupClickContent)
                    .openOn(map);
            });


            featureGroup.addLayer(layer)
        }
    });

    map.addLayer(featureGroup)
    if (dataInfo.legendSettings) {
        addLegend(dataInfo.legendSettings)
      }

};

export function addFeatureCollectionToTable( data ){
    const featureCollection = data.featureCollection
    const dataInfo = data.dataInfo
    const ProjectClass = projectClasses[dataInfo.dataType]
    const project = ProjectClass.loadFromLocalStorage()
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
    project.saveToLocalStorage();

    const tableSettings = createTableSettings(dataInfo);
    $(`#${dataInfo.dataType}-table`).DataTable(tableSettings);
    $(`#card-${dataInfo.dataType}-table`).removeClass('d-none')
};

// export function addFeatureCollectionResultCards( dataInfo, gekMeasures) {
//     console.log(gekMeasures)
//     console.log("Creating card")
//     const infoCard = document.getElementById('sieker_gek-info-card');
//     const infoCardBody = document.getElementById('sieker_gek-info-card-body');
//     infoCardBody.innerHTML = '';
//     gekMeasures.forEach(gek => {
//         const cardBody = document.createElement('div');
//         cardBody.classList.add('card-body')
//         // card
//         cardBody.innerHTML = `<h4 class="card-title m-3">${gek.name} Abschnitt ${gek.planning_segment}</h4>`;
        
//         const card = document.createElement('div');
//         card.classList.add("card")
//         card.classList.add("mb-3")
//         card.classList.add("gek-result-card")
//         card.setAttribute('data-type', dataInfo.dataType)
//         card.setAttribute('data-id', gek.id)


//         gek.measures.forEach(measure => {
//             const innerCard = document.createElement('div');
//             innerCard.classList.add("card")
//             innerCard.classList.add("mb-3")
//             // innerCard.setAttribute('data-type', measure.dataType)
//             innerCard.setAttribute('data-id',measure.id)

//             const innerCardBody = document.createElement('div');
//             innerCardBody.classList.add("card-body")
//             innerCardBody.innerHTML = `
//                 <h5 class="card-title">${measure.gek_measure}</h5>
//                 <b>Anzahl:</b><span> ${measure.quantity}</span></br>
//                 <b>Kosten:</b><span> ${measure.costs} €</span></br>
//                 <div class="result-text-box">${measure.description}</div>
//             `;
        
//             innerCard.appendChild(innerCardBody)
//             cardBody.append(innerCard)
//         })
//         card.appendChild(cardBody)
//         infoCardBody.appendChild(card)
//     })
//     infoCard.style.display = '';
// }