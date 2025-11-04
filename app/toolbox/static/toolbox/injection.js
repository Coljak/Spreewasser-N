import { getGeolocation, handleAlerts, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { 
  updateDropdown, 
  addLegend, 
  addChangeEventListener, 
  addFeatureCollectionToTable, 
  tableCheckSelectedItems, 
  addClickEventListenerToToolboxPanel, 
  addPointFeatureCollectionToLayer, 
  addFeatureCollectionToLayer, 
  loadProjectToGui,
addLegendForWms,
getTileOverlay,
 } from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  openUserFieldNameModal,
  getUserFieldIdByLeafletId, 
  getLeafletIdByUserFieldId, 
  highlightLayer, 
  selectUserField,
  dismissPolygon,
  removeLegendFromMap,
} from '/static/shared/map_sidebar_utils.js';
import {Injection} from '/static/toolbox/injection_model.js';
import { Layers } from '/static/toolbox/layers.js';





const geoserverLayers = {
  'result': `spreewassern_raster:${userId}_mar_result`,
  'aquifer_thickness':'spreewassern_raster:aquifer_classified_v1',
  'depth_groundwater': 'spreewassern_raster:depth_to_gw_classified_v1',
  'land_use': 'spreewassern_raster:land_use',
  'distance_to_source': 'spreewassern_raster:distance_to_source_water_v1',
  'distance_to_well': 'spreewassern_raster:distance_to_extraction_wells_v1',
  'hydraulic_conductivity': 'spreewassern_raster:hydraulic_conductivity_classified_v1',
  }
// TODO same as in drainage- check if needs to be removed
// let wmsOverlayLayer = L.tileLayer();
// wmsOverlayLayer.toolTag = 'injection';





export function initializeInjection(data) {
  console.log('initializeInjection')

  

  const sliderLabelsWeighting = data.sliderLabels;
  const sliderLabelsSuitability = data.sliderLabelsSuitability;


  $('#toolboxPanel').off('change');
  $('#toolboxPanel').off('click');

    initializeSliders();
      
  const weightingForm = document.querySelector('.weighting-form')
  const weightingSliders = weightingForm.querySelectorAll('input.single-slider');
  weightingSliders.forEach(slider => {
    console.log('slider:', slider)
    console.log('sliderLabels:', sliderLabelsWeighting)
    const sliderLabelRight = slider.parentElement.nextElementSibling;
    sliderLabelRight.innerText = sliderLabelsWeighting[Math.max(...Object.keys(sliderLabelsWeighting).map(Number))];
    slider.addEventListener('change', function() {
      console.log('sliderChanged', slider.value);
      if (slider.value in sliderLabelsWeighting) {
        sliderLabelRight.innerText = sliderLabelsWeighting[slider.value];
      }
    });
  })

  const suitabilityForms = document.querySelectorAll('.suitability-form')
  suitabilityForms.forEach(form => {
    const suitabilitySliders = form.querySelectorAll('input.single-slider');
    suitabilitySliders.forEach(slider => {
      const sliderLabelRight = slider.parentElement.nextElementSibling;
      // sliderLabelRight.innerText = sliderLabelsSuitability[slider.value];
      slider.addEventListener('change', function() {
      if (slider.value in sliderLabelsSuitability) {
        sliderLabelRight.innerText = sliderLabelsSuitability[slider.value];
      }
    });
    slider.dispatchEvent(new Event('change'))
  })
  })
    addChangeEventListener(Injection);

    addClickEventListenerToToolboxPanel(Injection)


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
    }  else if ($target.is('a.nav-link')) {
      const sustainibilityType = $target.data('type');
      Layers['injection'].remove()
      removeLegendFromMap(map)
      if (sustainibilityType) {
        console.log('sustainibility type', sustainibilityType, 'tiff and legend' )
          getTileOverlay(geoserverLayers[sustainibilityType], 'injection')
          if(!$('button.toggle-tile-layer').hasClass('shown')){
            console.log('IS not shown')
            document.querySelector('.leaflet-legend').hidden = true; 
          } else {
            document.querySelector('.leaflet-legend').hidden = false;
          }
        
      }
    } else if ($target.hasClass('calculate-area')) {
      const injection = Injection.loadFromLocalStorage()
      fetch('mar_calculate_area/', {
            method: 'POST',
            body: JSON.stringify(injection),
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCSRFToken()
            }
      })
      .then(response => response.json())
      .then(msg =>{ 
        console.log('msg', msg)
        if (msg.success === true){
          $('#btn-mar-result-map').removeClass('disabled');
          getTileOverlay(geoserverLayers['result'], 'injection');
          $('#btn-mar-result-map').text('Ergebnis ausblenden');
      }})
    }   else if ($target.attr('id') === 'btn-mar-result-map') {
        if ($target.hasClass('shown')) {
          console.log("layerNames['result']", geoserverLayers['result'])
          getTileOverlay(geoserverLayers['result'], 'injection');
          $('#btn-mar-result-map').removeClass('shown');
          $('#btn-mar-result-map').text('Ergebnis ausblenden')
        } else {
          $('#btn-mar-result-map').addClass('shown');
          $('#btn-mar-result-map').text('Ergebnis einblenden');
          removeLegendFromMap(map);
          Layers['injection'].remove();
        }
        

    }
    }); 
    

  $('input[type="checkbox"][name="land_use"]').prop('checked', true);
  $('input[type="checkbox"][name="land_use"]').trigger('change');

const injection = Injection.loadFromLocalStorage();
loadProjectToGui(injection)
}

