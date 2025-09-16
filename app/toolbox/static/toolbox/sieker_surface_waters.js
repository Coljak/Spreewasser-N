import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import {  updateDropdown, addChangeEventListener, addClickEventListenerToToolboxPanel, addFeatureCollectionToLayer, addFeatureCollectionToTable, waterLevelPinIcon } from '/static/toolbox/toolbox.js';
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

export function initializeSiekerSurfaceWaters(layers) {
    

    const project = SiekerSurfaceWaters.loadFromLocalStorage();
    

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
    
    const waterLevelsFeatureGroup = Layers.sieker_water_level
    let waterLevels = L.geoJSON(layers.water_levels.featureCollection, {
        pointToLayer: function (feature, latlng) {
            return L.marker(latlng, {
                icon: waterLevelPinIcon
            });
        },
        onEachFeature: function (feature, layer) {
            let popupContent = `
                <h6><b> ${feature.properties.pegelname}</b></h6>
                Zeitraum: ${feature.properties.period}<br>
                Tage: ${feature.properties.t_d}<br>
                Jahre: ${feature.properties.t_a}<br>
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
    addClickEventListenerToToolboxPanel(SiekerSurfaceWaters)
};

