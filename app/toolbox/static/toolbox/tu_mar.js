import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { updateDropdown, addLegend, addChangeEventListener, addFeatureCollectionToTable, tableCheckSelectedItems, addClickEventListenerToToolboxPanel, addPointFeatureCollectionToLayer, addFeatureCollectionToLayer } from '/static/toolbox/toolbox.js';
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
import {TuMar} from '/static/toolbox/tu_mar_model.js';
import { Layers } from '/static/toolbox/layers.js';


// const legendSettings = {
//     'header': 'Senkeneignung',
//     'grades': [1, 0.75, 0.5, 0.25, 0],
//     'gradientLabels': [' 100%', ' 75%', ' 50%', ' 25%', ' 0%']
// } 
// const wmsGwcUrl = "http://localhost:8080/geoserver/gwc/service/wms"
const wmsGwcUrl = "http://localhost:8080/geoserver/spreewassern_raster/wms"
// const wmsLayerName = "spreewassern_raster:clc_buek_4326_100m_buek_clc"
const layerNames = {
  'result': `spreewassern_raster:${userId}_mar_result`,
  'aquifer_thickness':'spreewassern_raster:aquifer_classified_v1',
  'depth_groundwater': 'spreewassern_raster:depth_to_gw_classified_v1',
  'land_use': 'spreewassern_raster:land_use',
  'distance_to_source': 'spreewassern_raster:distance_to_source_water_v1',
  'distance_to_well': 'spreewassern_raster:distance_to_extraction_wells_v1',
  'hydraulic_conductivity': 'spreewassern_raster:hydraulic_conductivity_classified_v1',
  }

export function initializeTuMar(data) {

  
 let wmsOverlayLayer = L.tileLayer()
 let legend;

function getTileOverlay(wmsLayerName) {
  wmsOverlayLayer.remove()
  removeLegendFromMap(map)
  wmsOverlayLayer = L.tileLayer.wms(wmsGwcUrl, {
  layers: wmsLayerName,
  format: "image/png",
  transparent: true,
  tileSize: 256,   // ⬅️ important, reduces tile resampling artifacts
  keepBuffer: 10,  // ⬅️ keeps more tiles around when zooming
  updateWhenZooming: false, // don’t request tiles mid-zoom
  _t: Date.now() // this is only a cache buster for rasters that chance
}).addTo(map);

  const legend = L.control.Legend({
    position: "bottomleft"
  });
  legend.onAdd = function (map) {
      var div = L.DomUtil.create("div", "leaflet-legend leaflet-bar");
      var url = `${wmsGwcUrl}?REQUEST=GetLegendGraphic&VERSION=1.1.1&FORMAT=image/png&LAYER=${wmsLayerName}`;
      div.innerHTML +=
        "<img src=" +
        url +
        ' alt="legend" data-toggle="tooltip" title="Map legend">';
      return div;
    };
  legend.addTo(map)

};



  console.log('data', data)
  const sliderLabelsWeighting = data.sliderLabels;
  const sliderLabelsSuitability = data.sliderLabelsSuitability;
  
  removeLegendFromMap(map);
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag && layer.toolTag !== 'tuMar') {
            map.removeLayer(layer);
        }
      });

  $('#toolboxPanel').off('change');
  $('#toolboxPanel').off('click');

    initializeSliders();
  // initializeSliders();
      
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
    addChangeEventListener(TuMar);

    addClickEventListenerToToolboxPanel(TuMar)

    // $('#toolboxPanel').on('input', function (event) {

    // }


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
      if ($target.hasClass('shown')) {
        $target.removeClass('shown')
        $target.text('einblenden')
        wmsOverlayLayer.remove()
        removeLegendFromMap(map)
      } else {
        $target.text('ausblenden')
        
        getTileOverlay(layerNames[dataType])
        $target.addClass('shown')
      }
      // wmsTestLayer.addTo(map);
      
    } else if ($target.is('a.nav-link')) {
      const sustainibilityType = $target.data('type');
      wmsOverlayLayer.remove()
      removeLegendFromMap(map)
      if (sustainibilityType) {
        console.log('sustainibility type', sustainibilityType, 'tiff and legend' )
        
        
      }
    } else if ($target.hasClass('calculate-area')) {
      const tuMar = TuMar.loadFromLocalStorage()
      fetch('mar_calculate_area/', {
            method: 'POST',
            body: JSON.stringify(tuMar),
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
          getTileOverlay(layerNames['result']);
          $('#btn-mar-result-map').text('Ergebnis ausblenden');
      }})
    }   else if ($target.attr('id') === 'btn-mar-result-map') {
        if ($target.hasClass('shown')) {
          console.log("layerNames['result']", layerNames['result'])
          getTileOverlay(layerNames['result']);
          $('#btn-mar-result-map').removeClass('shown');
          $('#btn-mar-result-map').text('Ergebnis ausblenden')
        } else {
          $('#btn-mar-result-map').addClass('shown');
          $('#btn-mar-result-map').text('Ergebnis einblenden');
          removeLegendFromMap(map);
          wmsOverlayLayer.remove();
        }
        

    }
    }); 
    

  $('input[type="checkbox"][name="land_use"]').prop('checked', true);
  $('input[type="checkbox"][name="land_use"]').trigger('change');


}

