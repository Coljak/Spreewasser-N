import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { updateDropdown, addChangeEventListener, addClickEventListenerToToolboxPanel, addFeatureCollectionToTable, getTileOverlay, addFeatureCollectionToLayer, addPointFeatureCollectionToLayer, loadProjectToGui } from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { Drainage } from '/static/toolbox/sieker_drainage_model.js';
import {Layers} from '/static/toolbox/layers.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  openUserFieldNameModal,
  addLayerToSidebar, 
  getUserFieldIdByLeafletId, 
  getLeafletIdByUserFieldId, 
  highlightLayer, 
  selectUserField,
  handleSaveUserField,
  dismissPolygon,
  getCircleMarkerSettings, 
  getLegendItem,
  getLegendSettings,
  removeLegendFromMap,
} from '/static/shared/map_sidebar_utils.js';


const geoserverLayers = {
  // 'result': `spreewassern_raster:${userId}_mar_result`,
  'drainage_probability':'spreewassern_raster:Entwaesserungswahrscheinlichkeit_9Parameter_v2',
  'known_drainage': 'toolbox_vector:toolbox_knowndrainages',
  'drainage_network': 'toolbox_vector:toolbox_drainagenetwork',

  // 'drainage_network_ditches': 'toolbox_vector:drainage_network_ditches',
  // 'drainage_network_drainage': 'toolbox_vector:drainage_network_drainage',
  // 'drainage_network_natural_creeks': 'toolbox_vector:drainage_network_natural_creeks',
  // 'drainage_network_non_natural_creeks': 'toolbox_vector:drainage_network_non_natural_creeks',
  // 'drainage_network_rivers': 'toolbox_vector:drainage_network_rivers',
  }


  function filterDrainages(type, featureGroup) {
    // Implement filtering logic here
  }

export function initializeDrainage(userField) {
  const project = new Drainage();
  project.userField = userField;
  project.saveToLocalStorage()

  getTileOverlay(geoserverLayers['drainage_probability'], 'drainage_probability');




  console.log('Initialize Sieker Drainage with project:', project);
  // map.addLayer(siekerSinkFeatureGroup);
  
  initializeSliders();
      
  $('#toolboxPanel').off('change');

  $('#toolboxPanel').on('click', function (event) {
      const $target = $(event.target);
      if ($target.is('input.reset-all, button.reset-all')) {
          console.log('Reset button clicked:', $target);
  
          // Find the enclosing form
          const $form = $target.closest('form');
  
          // Find all slider inputs inside that form
          $form.find('input.single-slider').each(function () {
              const $slider = $(this);
              const defaultVal = parseFloat($slider.data('default-value'));
  
              $slider.val(defaultVal).trigger('change'); // set value and trigger input event
          });
      } else if ($target.hasClass('toggle-tile-layer')) {
        const dataType = $target.data('type')
        console.log('toggle tile', dataType)
        if ($target.hasClass('shown')) {
          $('button.toggle-tile-layer').removeClass('shown');
          $('button.toggle-tile-layer').text('einblenden')

          Layers[dataType].hidden = true;
          // document.querySelector('.leaflet-legend').hidden = true; 
        } else {
          $('button.toggle-tile-layer').text('ausblenden')
          $('button.toggle-tile-layer').addClass('shown');
          
          Layers[dataType].hidden = false;
          // document.querySelector('.leaflet-legend').hidden = false; 
          $target.addClass('shown')
        }

      } else if ($target.attr('prefix') == 'parent'){
          const parent = $target.val();
          console.log('parent clicked:', parent, $(`input[parent=${parent}]`))
          $(`input[parent=${parent}]`).prop('disabled', !$target.is(':checked'));

      } else if ($target.attr('id') === 'btnFilterDrainageNetwork') {
        filterDrainages('Drainage', DrainageFeatureGroup);
      } else if ($target.attr('id') === 'btnFilterKnownDrainages') {
        filterKnownDrainages('KnownDrainage', KnownDrainageFeatureGroup);
      } 
  });

  addChangeEventListener(Drainage);
  
  addClickEventListenerToToolboxPanel(Drainage);
  // this is only for the slider
  //addChangeEventListener(Drainage);
  $('#id_drainage_threshold_slider').on('change', () => {   
            const inputName = $target.attr('name'); 
            const inputVal = $target.val();
            project[inputName] = inputVal;
            project.saveToLocalStorage();
            // TODO implement live change of the raster map
            return;
        })

  

$('#tabDrainageNetwork input[type="checkbox"]')
    .prop('checked', true)
    .trigger('change');


};

