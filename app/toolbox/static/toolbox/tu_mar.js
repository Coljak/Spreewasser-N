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
  const sliderLabels = data.sliderLabels;
  
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
      
  const form = document.getElementById('tu-mar-weighting-form')

  const sliders = form.querySelectorAll('input.single-slider');
    

  const resetBtn = form.querySelector('input.reset-all');
  resetBtn.addEventListener('click', function (e) {
    // let tuMar = TuMar.loadFromLocalStorage(); // TODO this is not needed but check
    sliders.forEach(widget => {
      widget.value = parseFloat(widget.dataset.defaultValue);
      widget.dispatchEvent(new Event('input'));
      // widget.val = parseFloat(widget.slider.dataset.defaultValue);
    });

  });

  sliders.forEach(slider => {
    console.log('slider:', slider)
    console.log('sliderLabels:', sliderLabels)
    const sliderLabelRight = slider.parentElement.nextElementSibling;
    sliderLabelRight.innerText = sliderLabels[Math.max(...Object.keys(sliderLabels).map(Number))];
    slider.addEventListener('change', function() {
      console.log('sliderChanged', slider.value);
      if (slider.value in sliderLabels) {
        sliderLabelRight.innerText = sliderLabels[slider.value];
      }
    });
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
    $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.attr('id') === 'btnFilterSinks') {
      filterSinks('sink');
    
    } else if ($target.attr('id') === 'btnFilterEnlargedSinks') {
      filterSinks('enlarged_sink');
    
    } else if ($target.attr('id') === 'btnFilterStreams') {
      getWaterBodies('stream');
    
    } else if ($target.attr('id') === 'btnFilterLakes') {
      getWaterBodies('lake');

    } else if ($target.attr('id') === 'btnGetInlets') {
        getInlets(); 
    } else if ($target.attr('id') === 'navTuMarSinks') {
        map.addLayer(Layers.sink);
    } else if ($target.attr('id') === 'navTuMarEnlargedSinks') {
        map.addLayer(Layers.enlarged_sink);
    } else if ($target.attr('id') === 'navTuMarResult') {
        map.removeLayer(Layers.sink);
        map.removeLayer(Layers.enlarged_sink);


    }  
    }); 

  $('input[type="checkbox"][name="land_use"]').prop('checked', true);
  $('input[type="checkbox"][name="land_use"]').trigger('change');


}

