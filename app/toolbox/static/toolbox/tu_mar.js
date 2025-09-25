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
  removeLegendFromMap,
} from '/static/shared/map_sidebar_utils.js';
import {TuMar} from '/static/toolbox/tu_mar_model.js';
import { Layers } from '/static/toolbox/layers.js';


// const legendSettings = {
//     'header': 'Senkeneignung',
//     'grades': [1, 0.75, 0.5, 0.25, 0],
//     'gradientLabels': [' 100%', ' 75%', ' 50%', ' 25%', ' 0%']
// } 




//TODO: this is not pretty
const connectionLayerMap = {};


// function filterSinks(sinkType) {
//   const featureGroup = Layers[sinkType]
//   let url = `filter_${sinkType}s/`;
 
//   const tuMar = TuMar.loadFromLocalStorage();
//   fetch(url, {
//     method: 'POST',
//     body: JSON.stringify(tuMar),
//     headers: {
//         'Content-Type': 'application/json',
//         'X-CSRFToken': getCSRFToken(),
//     }
//   })
//   .then(response => response.json())
//   .then(data => {
//     featureGroup.clearLayers();
    
//     if (data.message.success) {
//       const selected_sinks = tuMar[`selected_${sinkType}s`];
//       tuMar[`selected_${sinkType}s`] = [];
     


//       console.log('data', data);
//       const sink_indices = {}
      

//       addPointFeatureCollectionToLayer(data);

//       addFeatureCollectionToTable(data)
//       tuMar[`selected_${sinkType}s`] = selected_sinks.filter(sink => tuMar[`all_${sinkType}_ids`].includes(sink));
//       localStorage.setItem(`${sinkType}_indices`, JSON.stringify(sink_indices));

//       // tuMar.saveToLocalStorage();
//       // Add the cluster group to the map
//       // featureGroup.addLayer(markers);

    
//     } else {
//       handleAlerts(data.message);
//       return;
//     }
//     return {'tuMar': tuMar, sinkType: sinkType}
// }).then(data => {
//   tableCheckSelectedItems(data.tuMar, data.sinkType)
// })
// .catch(error => console.error("Error fetching data:", error));
// };


// function getWaterBodies(dataType){
  
//   let url = `filter_waterbodies/`;

//   const tuMar = TuMar.loadFromLocalStorage();

//   fetch(url, {
//     method: 'POST',
//     body: JSON.stringify({
//       dataType: dataType,
//       project: tuMar}),
//     headers: {
//         'Content-Type': 'application/json',
//         'X-CSRFToken': getCSRFToken(),
//     }
//   })
//   .then(response => response.json())
//   .then(data => {
//     console.log('data', data)
//     if (data.message.success) {
//       addFeatureCollectionToLayer(data)
//       addFeatureCollectionToTable(data)
//     }  else {
//       handleAlerts(data.message);
//     } 
//   })
//   .catch(error => console.error("Error fetching data:", error));
// };





export function initializeTuMar(data) {
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


  // const slider = document.getElementById('wetland_feasibility_slider');
  // const sliderLabelLeft = document.getElementById('wetland_feasibility_start_text');
  // const sliderLabelRight = document.getElementById('wetland_feasibility_value');
  // const sliderLabels = data['sliderLabels'];
  // sliderLabelLeft.innerText = sliderLabels[Math.min(...Object.keys(sliderLabels).map(Number))];
  // sliderLabelRight.innerText = sliderLabels[Math.max(...Object.keys(sliderLabels).map(Number))];

  // if (slider && sliderLabels) {
  //   slider.addEventListener('change', function() {
  //     console.log('sliderChanged', slider.value);
  //     if (slider.value in sliderLabels) {
  //       sliderLabelLeft.innerText = sliderLabels[slider.value];
  //     }
  //   });
  // }

    


    $('#toolboxPanel').off('change'); // Remove any previous change event handlers
    addChangeEventListener(TuMar);
    $('#toolboxPanel').off('click');
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
    } else if ($target.is('a.nav-link')) {
      const sustainibilityType = $target.data('type');
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
      .then(response => response.json)
      .then(console.log('data', data))
    }

    else if ($target.attr('id') === 'navTuMarResult') {
        map.removeLayer(Layers.sink);
        map.removeLayer(Layers.enlarged_sink);


    }  
    }); 

  $('input[type="checkbox"][name="land_use"]').prop('checked', true);
  $('input[type="checkbox"][name="land_use"]').trigger('change');


}

