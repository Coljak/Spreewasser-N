import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { 
  addChangeEventListener,
   addClickEventListenerToToolboxPanel, 
   addFeatureCollectionToTable, 
   getTileOverlay, 
   getTileOverlayWithThreshold,
   addFeatureCollectionToLayer, 
   addPointFeatureCollectionToLayer, 
   loadProjectToGui,
  addLegendForWms, 
  addLegend } from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { Drainage } from '/static/toolbox/sieker_drainage_model.js';
import {Layers} from '/static/toolbox/layers.js';
import {geoserverLayers} from '/static/toolbox/geoserver_layers.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 
} from '/static/shared/map_sidebar_utils.js';



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

async function getFeatures(userField) {
  console.log('getFeatures', userField)

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
          addFeatureCollectionToLayer(dataset, true)
        })  
      }
      if (data.network_type_detail_feature_collections.length > 0) {
        data.network_type_detail_feature_collections.forEach(dataset => {
          ('drainage_type:',  dataset.dataInfo.dataType, dataset.dataInfo);
          addFeatureCollectionToLayer(dataset, true)
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

export function initializeDrainage() {

  $('#toolboxPanel').off('change');
  $('#toolboxPanel').off('click');

  // getTileOverlay(geoserverLayers['drainage_probability'], 'drainage_probability', 'drainage');
  const threshold = $('#id_drainage_threshold_slider').val();
  // getTileOverlayWithThreshold(geoserverLayers['drainage_probability'], 'drainage_probability', 'drainage', threshold)
  // addLegendForWms(geoserverLayers['drainage_probability']);
  fetch('get_drainage_raster_legend/')
  .then(response => response.json())
  .then(data => addLegend(data['legendSettings']))
  
  

  // map.addLayer(siekerSinkFeatureGroup);
  

  initializeSliders();
  addChangeEventListener(Drainage);
  addClickEventListenerToToolboxPanel(Drainage);
      


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
          console.log('parent', parent)
          console.log("`input[parent=${parent}]`", `input[parent=${parent}]`)
          $(`input[parent=${parent}]`).prop('disabled', !$target.is(':checked'));

      } else if ($target.attr('id') == 'button-id-apply-drainage_threshold')  {
        const th = $('#id_drainage_threshold_slider').val();
        getTileOverlayWithThreshold(geoserverLayers['drainage_probability'], 'drainage_probability', 'drainage', th)
      }
  });

  $('#toolboxPanel').on('change', function (event) {
    const $target = $(event.target);
    if ($target.hasClass('form-check-input')) {
            // checkboxes in drainage network
      const inputId = $target.attr('id');
      const inputName = $target.attr('name'); //non_natural_creeks
      const inputPrefix = $target.attr('prefix'); /// 'parent' is parent of 'drainage', else 'drained_area'
      const inputValue = $target.attr('value'); // 5 id of detail
      const inputChecked = $target.is(':checked');
      console.log('click inputName', inputName)
      // console.log('the layer Layers[inputName]:', Layers[inputName])
      if (inputPrefix === 'parent') { 
        
        if (!inputChecked) {
          Layers[inputName].forEach(featureGroup => {
            map.removeLayer(featureGroup)
          })
        } else {
          const checkboxes = $(`input[name=${inputName}][prefix="drainage"]`) 
          // checkboxes.each(checkbox => {
          console.log('checkbox', checkboxes)
          checkboxes.each(function () {
            const name = $(this).attr('detail');
            if ($(this).is(':checked')) {
              console.log('add layer', name, $(this), $(this).is(':checked'))
              map.addLayer(Layers[name])
            } 
            })
        } 
      } else if (inputPrefix === 'drainage') {
        
        const inputDetail = $target.attr('detail');
        if (inputChecked) {
          map.addLayer(Layers[inputDetail])
        } else { 
          map.removeLayer(Layers[inputDetail])
        }
      } else if (inputPrefix === 'drained_area') {
        const layerName = $target.attr('drained_area_type');
        console.log('drained area:', layerName)
        if (inputChecked) {
          map.addLayer(Layers[layerName])
        } else {
          map.removeLayer(Layers[layerName])
        }
      }
    }
            // for drainage network, prefix is drainage, drained_area

  })
  const project = Drainage.loadFromLocalStorage();
  getFeatures(project.userField)
  .then(() => {
    loadProjectToGui(project)
  });

// $('input[type="checkbox"]').trigger('change');
};

