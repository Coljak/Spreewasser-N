import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, toolboxSinks, updateDropdown } from '/static/toolbox/toolbox.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  createBaseLayerSwitchGroup, 
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
} from '/static/shared/map_sidebar_utils.js';


const lakesFeatureGroup = new L.FeatureGroup();
lakesFeatureGroup.toolTag = 'sieker-surface-waters'
const waterLevelsFeatureGroup = new L.FeatureGroup();
waterLevelsFeatureGroup.toolTag = 'sieker-surface-waters'




export function initializeSiekerSurfaceWaters(layers) {
    console.log("Initializing Sieker surface waters...", layers);
    map.eachLayer(function(layer) {
        // console.log(layer.toolTag);
        if (
            layer.toolTag === 'infiltration' ||
            layer.toolTag === 'sieker-sink') {
            map.removeLayer(layer);
        }
    });

    // add lakes and water levels


    layers.lakes.features.forEach(feature => {
    // try {
    console.log('feature:', feature);

        let layer = L.geoJSON(feature, {
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
            }
        })
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
        layer.addTo(lakesFeatureGroup);
    });
    // lakesFeatureGroup.addTo(map);
    // project.saveToLocalStorage();
  




    $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.hasClass('toolbox-back-to-initial')) {
      $('#toolboxButtons').removeClass('d-none');
        $('#toolboxPanel').addClass('d-none');
        
        }
    });


    map.addLayer(lakesFeatureGroup);
    // map.addLayer(waterLevelsFeatureGroup);

};