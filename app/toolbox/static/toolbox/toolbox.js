import { getGeolocation, handleAlerts, getCSRFToken, saveProject, observeDropdown,  setLanguage, populateDropdown } from '/static/shared/utils.js';
import {Infiltration} from '/static/toolbox/infiltration_model.js';
import {SiekerGek} from '/static/toolbox/sieker_gek_model.js';
import {SiekerSink} from '/static/toolbox/sieker_sink_model.js';
import {SiekerSurfaceWaters} from '/static/toolbox/sieker_surface_waters_model.js';
import {map} from '/static/shared/map_sidebar_utils.js';


export const waterLevelPinIcon = L.icon({
        iconUrl: '/static/images/water-level-pin_x2.png',
        iconSize: [40, 40], // size of the icon
        iconAnchor: [20, 40], // point of the icon which will correspond to marker's location
        // popupAnchor: [0, 0] // point from which the popup should open relative to the iconAnchor
        });

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

// newly filtered items or pagination requires this to be executed in the DataTable
export function tableCheckSelectedItems(project, dataType) {
    console.log('tableCheckSelectedItems')
  if (project[`selected_${dataType}s`] !== undefined && project[`selected_${dataType}s`].length > 0) {
    project[`selected_${dataType}s`].forEach(itemId => {
      const checked = project[`all_${dataType}_ids`].includes(itemId) ? true : false;
      const checkbox = document.querySelector(`.table-select-checkbox[data-type="${dataType}"][data-id="${itemId}"]`);
      if (checkbox && checked) {
        checkbox.checked = checked;
        // checkbox.dispatchEvent(new Event('change', { bubbles: true }));
      }
    })
  }  
};




export async function toolboxSinks() {
    // gets the sinks as an image
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
              layer.bindTooltip(feature.properties.name);
          }
      });

      return toolboxSinks; // Return the Leaflet layer
  } catch (error) {
      console.error("Error loading project region:", error);
      return null;
  }
};

// let CurrentProjectClass = null;
    // eventlistener for the filters
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
                console.log('Evenet listener')
                return;
        }
        else if ($target.hasClass('paginate_button')) {
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
        } 
    });
};

// for dataTablesselect * from toolbox_gekretention tg where id = 1
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
  const hue = index * 100
  let color = `hsl(${hue}, 90%, 50%)`;
  return color
};


export function addFeatureCollectionToLayer(featureCollection, dataInfo, featureGroup, colorByIndex){
      console.log('addFeatureCollectionToLayer dataInfo', colorFunction, dataInfo)
  
    let layer = L.geoJSON(featureCollection, {
        style: function (feature) {
            let color;

            if (colorByIndex) {

                color = colorFunction(feature.geometry.properties[colorByIndex]);
            } else {
                color = dataInfo.featureColor;
            }

            return {
                color,
                className: dataInfo.className,
            };
        },
        onEachFeature: function (feature, layer) {
            let popupContent = `<h6><b> ${feature.properties[dataInfo.popUp.header]}</b></h6>`;
            dataInfo.properties.forEach(property => {
            if (property.popUp) { 
                popupContent += property.href
                ? `<a href="${feature.properties[property.valueName]}" target="_blank">${property.title}</a><br>`
                : `<b>${property.title}:</b> ${feature.properties[property.valueName]}<br>`;
                }
            
            });
                
            layer.on('add', function () {
                if (layer._path) {
                    layer._path.setAttribute('data-type', dataInfo.dataType);
                    layer._path.setAttribute('data-id', feature.properties.id);
                }
            });
                    
            layer.bindTooltip(popupContent);
            let menuContent = popupContent + `<button class="btn btn-outline-secondary select-feature" data-type=${dataInfo.dataType} data-id="${feature.properties.id}">Auswählen</button>`;

            layer.on('mouseover', function () {
                // this.setStyle(highlightStyle);
                this.openTooltip();
            });
    
            layer.on('mouseout', function () {
                // Only reset to default if not clicked
                if (!this.options.isClicked) {
                    // this.setStyle(defaultStyle);
                }
            });
    
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
    
            layer.on('contextmenu', function (event) {
            L.popup()
                .setLatLng(event.latlng)
                .setContent(`
                    <h6><b> ${feature.properties.name}</b></h6>
                    <button class="btn btn-outline-secondary select-feature-button" data-type="${dataInfo.dataType} data-id="${feature.properties.id}">Auswählen</button>
                `)
                .openOn(map);
    
            setTimeout(() => {
                const button = document.querySelector('.select-feature-button');
                if (button) {
                    button.addEventListener('click', () => {
                        map.closePopup(); 
                        const featureId = button.getAttribute('data-id');
                        console.log('Selected featureId ID:', featureId);
                    });
                }
            }, 0);
            });
        }
        });
  
    let layerGroup = L.featureGroup([layer]).addTo(map);

    layer.addTo(featureGroup);
    layer.bringToFront();
};


export function addFeatureCollectionToTable(projectClass, featureCollection, dataInfo){
    console.log('addFeatureCollectionToTable, dataInfo:', dataInfo)
    const project = projectClass.loadFromLocalStorage()
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
                    tableHTML += `<td>${feature.properties[property.valueName]}</td>`
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