import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, updateDropdown, SiekerSurfaceWaters, addChangeEventListener } from '/static/toolbox/toolbox.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  openUserFieldNameModal,
  createNUTSSelectors,
  changeBasemap, 
  initializeSidebarEventHandler, 
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




const lakesFeatureGroup = new L.FeatureGroup();
lakesFeatureGroup.toolTag = 'sieker-surface-waters'
const waterLevelsFeatureGroup = new L.FeatureGroup();
waterLevelsFeatureGroup.toolTag = 'sieker-surface-waters'

function createSiekerLargeLakeTableSettings() {
  return {
    "order": [[1, "asc"]],
    "searching": false,
    "columnDefs": [
      {
        "targets": 0, // Select a checkbox
        "orderable": false,
        "searchable": false
      },
      {
        "targets": 1, // Name
        "orderable": true,
        "searchable": true
      },
      {
        "targets": 2, // Stand
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 3, // Badesee
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 4, // Area ha
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 5, // Volumen vol_mio_m3
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 6, // Einzugsgebiet in km²
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 7, // Max Tiefe d_max_m 
        "orderable": true,
        "searchable": false
      },
    ]
  }
};


export function initializeSiekerSurfaceWaters(layers, userField) {

    const project = new SiekerSurfaceWaters();
    project.userField = userField;
    

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


    let layer = L.geoJSON(layers.lakes,  {
        style: {
        color: 'purple',
        weight: 2,
        fillOpacity: 0.5
        },
        onEachFeature: function (feature, layer) {
        // project.infiltration[`selected_${waterbody}`].push(feature.properties.id);
            let popupContent = `
                <h6><b> ${feature.properties.name}</b></h6>
                `;
            layer.bindTooltip(popupContent);
            layer.on('mouseover', function () {
                this.openPopup();
            });
            layer.on('contextmenu', function (event) {
                L.popup()
                    .setLatLng(event.latlng)
                    .setContent(`
                    <h6><b> ${feature.properties.name}</b></h6>
                    <button class="btn btn-outline-secondary select-sieker-lake" data-sieker-lake-id=${feature.properties.id}">Auswählen</button>
                    `)
                    .openOn(map);

                        // Delay attaching event listener until DOM is rendered
                setTimeout(() => {
                    const button = document.querySelector('.select-sieker-lake');
                    if (button) {
                        button.addEventListener('click', () => {
                            map.closePopup(); 
                            // TODO: select lake from table
                            const lakeId = button.getAttribute('data-sieker-lake-id');
                            console.log('Selected lake ID:', lakeId);
                            // ...your code here...
                        });
                    }
                }, 0);
            });

        }
    });
        
    layer.addTo(lakesFeatureGroup);
    layer.bringToFront();
        //------------------------

    const tableContainer = document.getElementById('sieker-lake-table-container');

    let tableHTML = ` 
    <table class="table table-bordered table-hover" id="sieker-large-lake-table">
        <caption>Große Seen</caption>
        <thead>
        <tr>
            <th><input type="checkbox" class="sieker-large-lake-select-all-checkbox table-select-all" data-type="sieker_large_lake">Select all</th>
            <th>Name</th>
            <th>Stand</th>
            <th>Badesee</th>
            <th>Fläche (ha)</th>
            <th>Volumen (Mio. m³)</th>
            <th>Einzugsgebiet (km²)</th>
            <th>Max. Tiefe (m)</th>
        </tr>
        </thead>
        <tbody>
    `;

    
    layers.lakes.features.forEach(feature => {

        // Add to table
        tableHTML += `
            <tr>
                <td><input type="checkbox" class="sieker-large-lake-checkbox table-select-checkbox" data-type="sieker_large_lake" data-id="${feature.properties.id}"></td>
                <td>${feature.properties.name}</td>
                <td>${feature.properties.stand}</td>
                <td>${feature.properties.badesee ? 'Ja' : 'Nein'}</td>
                <td>${feature.properties.area_ha}</td>
                <td>${feature.properties.vol_mio_m3 ? feature.vol_mio_m3 : '--'}</td>
                <td>${feature.properties.einzugsgebiet_km2 ? feature.properties.einzugsgebiet_km2 : '--'}</td>
                <td>${feature.properties.d_max_m ? feature.properties.d_max_m : '--'}</td>
            </tr>`;

        project['all_sieker_large_lake_ids'].push(feature.properties.id)
    });
    tableHTML += `</tbody></table>`;
    tableContainer.innerHTML = tableHTML;
    const tableSettings = createSiekerLargeLakeTableSettings();
    $('#sieker-large-lake-table').DataTable(tableSettings);

    console.log('layers.water_levels: ', layers.water_levels);
    // Add water_levels points
    const waterLevelsCircleMarkerSettings = getCircleMarkerSettings('azure');
    let waterLevels = L.geoJSON(layers.water_levels, {
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, waterLevelsCircleMarkerSettings);
        },
        onEachFeature: function (feature, layer) {
            let popupContent = `
                <h6><b> ${feature.properties.pegelname}</b></h6>
                Zeitraum: ${feature.properties.start_date} - ${feature.properties.end_date}<br>
                Tage: ${feature.properties.t_d}<br>
                Jahre: ${feature.properties.t_a.toFixed(1)}<br>
                Min.: ${feature.properties.min_cm} cm<br>
                Max.: ${feature.properties.max_cm} cm<br>
                Mittel: ${feature.properties.mean_wl} m<br>
            `;
            layer.bindTooltip(popupContent);
            layer.on('mouseover', function () {
                this.openPopup();
            });
            layer.on('contextmenu', function (event) {
                L.popup()
                    .setLatLng(event.latlng)
                    .setContent(`
                    <h6><b> ${feature.properties.pegelname}</b></h6>
                    <button class="btn btn-outline-secondary select-sieker-water-level" data-sieker-water-level-id=${feature.properties.id}">Auswählen</button>
                    `)
                    .openOn(map);   
            });

            // Delay attaching event listener until DOM is rendered
            setTimeout(() => {
                const button = document.querySelector('.select-sieker-water-level');
                if (button) {
                    button.addEventListener('click', () => {
                        map.closePopup();
                    });
                }
            }, 0);
        }
    });

    waterLevels.addTo(waterLevelsFeatureGroup);




            


    layers.water_levels.features.forEach(feature => {
        // Polygons and Popups
        let levelLayer = L.geoJSON(feature, {
            style: {
            color: 'green',
            weight: 2,
            fillOpacity: 0.5
            },
            onEachFeature: function (feature, levelLayer) {
            // project.infiltration[`selected_${waterbody}`].push(feature.properties.id);
            let popupContent = `
                <h6><b> ${feature.properties.pegelname}</b></h6>
                Zeitraum: ${feature.properties.start_date} - ${feature.properties.end_date}<br>
                Tage: ${feature.properties.t_d}<br>
                Jahre: ${feature.properties.t_a.toFixed(1)}<br>
                Min.: ${feature.properties.min_cm} cm<br>
                Max.: ${feature.properties.max_cm} cm<br>
                Mittel: ${feature.properties.mean_wl} m<br>
                `;
            levelLayer.bindTooltip(popupContent);
            levelLayer.on('mouseover', function () {
                this.openPopup();
            });
            }
        })
        levelLayer.on('contextmenu', function (event) {
                L.popup()
                    .setLatLng(event.latlng)
                    .setContent(`
                    <h6><b> ${feature.properties.pegelname}</b></h6>
                    <button class="btn btn-outline-secondary select-sieker-water-level" data-sieker-water-level-id=${feature.properties.id}">Auswählen</button>
                    `)
                    .openOn(map);

                        // Delay attaching event listener until DOM is rendered
            setTimeout(() => {
                const button = document.querySelector('.select-sieker-water-level');
                if (button) {
                    button.addEventListener('click', () => {
                        map.closePopup();
                    });
                }
            }, 0 );
        });
        levelLayer.addTo(waterLevelsFeatureGroup);
        console.log('levelLayer: ', levelLayer);
    });

    $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.hasClass('toolbox-back-to-initial')) {
      $('#toolboxButtons').removeClass('d-none');
        $('#toolboxPanel').addClass('d-none');
        
        }
    });




    map.addLayer(lakesFeatureGroup);
    map.addLayer(waterLevelsFeatureGroup);

    document.getElementById('toggleSiekerLevels').addEventListener('click', function() {
        if (map.hasLayer(waterLevelsFeatureGroup)) {
            map.removeLayer(waterLevelsFeatureGroup);
            this.textContent = 'Pegel anzeigen';
        } else {
            map.addLayer(waterLevelsFeatureGroup);
            this.textContent = 'Pegel ausblenden';
        }
    });

    document.getElementById('toggleSiekerLakes').addEventListener('click', function() {
        if (map.hasLayer(lakesFeatureGroup)) {
            map.removeLayer(lakesFeatureGroup);
            this.textContent = 'Seen anzeigen';
        } else {
            map.addLayer(lakesFeatureGroup);
            this.textContent = 'Seen ausblenden';
        }
    });
    
    project.saveToLocalStorage();
};