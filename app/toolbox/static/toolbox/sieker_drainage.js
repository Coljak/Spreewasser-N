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
  }


function filterDrainages(type, featureGroup) {
  // Implement filtering logic here
};

function showButtonSpinner($button) {
  $button.data('original-text', $button.find('.btn-text').text());
  $button.find('.btn-text').html(`
    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Lädt...
  `);
  $button.prop('disabled', true);
};

function hideButtonSpinner($button) {
  const originalText = $button.data('original-text');
  $button.find('.btn-text').text(originalText);
  $button.prop('disabled', false);
};

function getFeatures(userField) {
  console.log('getFeatures', userField)
  // const $buttons = $('.toggle-vector-layer')
  // $buttons.each($button => {
  //   showButtonSpinner($button)
  // })
  fetch(`load_sieker_drainage_features/${userField}/`)
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      handleAlerts(data)
    } else {
      console.log('received data', data)
      if (data.drainage_type_feature_collections.length > 0) {
        data.drainage_type_feature_collections.forEach(dataset => {
          console.log('drainage_type:', dataset.drainedAreaTypeId, dataset.dataInfo.dataType, dataset.dataInfo);
          addFeatureCollectionToLayer(dataset)
        })  
      }
      if (data.network_type_detail_feature_collections.length > 0) {
        data.network_type_detail_feature_collections.forEach(dataset => {
          ('drainage_type:',  dataset.dataInfo.dataType, dataset.dataInfo);
          addFeatureCollectionToLayer(dataset)
        })  
      }
      
    }
    
  })
  .catch(err => console.log('getFeatures', err))
  .finally(() => {
    console.log('turn off spinner')
    // $buttons.each($button => {
    //   hideButtonSpinner($button)
    // })
  })
}

export function initializeDrainage(userField) {
  const project = new Drainage();
  project.userField = userField;
  project.saveToLocalStorage()

  $('#toolboxPanel').off('change');
  $('#toolboxPanel').off('click');

  getTileOverlay(geoserverLayers['drainage_probability'], 'drainage_probability');

  console.log('Initialize Sieker Drainage with project:', project);
  // map.addLayer(siekerSinkFeatureGroup);
  

  initializeSliders();
  addChangeEventListener(Drainage);
  addClickEventListenerToToolboxPanel(Drainage);
      

  $('#id_drainage_threshold_slider').on('change', () => {   
          const inputName = $target.attr('name'); 
          const inputVal = $target.val();
          project[inputName] = inputVal;
          project.saveToLocalStorage();
          // TODO implement live change of the raster map
          return;
      });

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
      } else if ($target.attr('prefix') == 'parent'){
          const parent = $target.val();
          console.log('parent clicked:', parent, $(`input[parent=${parent}]`))
          $(`input[parent=${parent}]`).prop('disabled', !$target.is(':checked'));

      } else if ($target.attr('id') === 'btnFilterDrainageNetwork') {
        filterDrainages('Drainage', DrainageFeatureGroup);
      } else if ($target.attr('id') === 'btnFilterDrainedArea') {
        filterDrainedArea('KnownDrainage', KnownDrainageFeatureGroup);
      } 
  });

  $('#toolboxPanel').on('change', function (event) {
    const $target = $(event.target);
    const project = Drainage.loadFromLocalStorage();
    if ($target.hasClass('form-check-input')) {
            // checkboxes 
      const inputId = $target.attr('id');
      const inputName = $target.attr('name'); //non_natural_creeks
      const inputPrefix = $target.attr('prefix'); /// 'parent' is parent of 'drainage', else 'drained_area'
      const inputValue = $target.attr('value'); // 5 id of detail
      const inputChecked = $target.is(':checked');
      console.log('click inputName', inputName)
      console.log('the layer Layers[inputName]:', Layers[inputName])
      if (inputPrefix === 'parent') {    
              if (inputChecked) {
                map.addLayer(Layers[inputName])
              } else {
                map.removeLayer(Layers[inputName])
              }
      } else if (inputPrefix === 'drainage') {
        const inputParent = $target.attr('parent');// = 3
        const inputDetail = $target.attr('detail');
        if (inputChecked) {
          map.addLayer(Layers[inputDetail])
        } else { 
          map.removeLayer(Layers[inputDetail])
        }
      } else if (inputPrefix === 'drained_area') {
        if (inputChecked) {
          map.addLayer(Layers[inputName])
        } else { 
          map.removeLayer(Layers[inputName])
        }
      }
    }
            // for drainage network, prefix is drainage, drained_area

  })
  getFeatures(userField);

$('input[type="checkbox"]')
    .prop('checked', true)
    .trigger('change');
};

