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
        if (layer.toolTag !== 'sieker-surface-waters') {
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
                        <b>Sink Options</b><br>
                        
                        <button class="btn btn-outline-secondary select-${waterbody}" ${waterbody}Id=${feature.properties.id}">Select Waterbody</button>
                    `)
                    .openOn(map);
                    });
        layer.addTo(lakesFeatureGroup);

    //     
    // } catch {
    // console.log('Error processing feature:', feature.properties.id);
    // }
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