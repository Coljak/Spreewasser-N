import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
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
  clearAndRemoveTable,
  createResultTable,
  getWaterBodies
 } from '/static/toolbox/toolbox.js';
import {ToolboxProject} from '/static/toolbox/toolbox_project.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  openUserFieldNameModal,
  removeLegendFromMap,
} from '/static/shared/map_sidebar_utils.js';
import {Infiltration} from '/static/toolbox/infiltration_model.js';
import { Layers } from '/static/toolbox/layers.js';


function filterSinks( $button) {
  const sinkType = $button.data('type')
  const spinner = $button.find('.spinner-border')
  spinner.show();
  $button.prop('disabled', true)
  const featureGroup = Layers[sinkType]
  let url = `filter_sinks/${sinkType}/`;
  const infiltration = Infiltration.loadFromLocalStorage();
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(infiltration),
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
    }
  })
  .then(response => response.json())
  .then(data => {
    featureGroup.clearLayers();
    
    if (!data.message.success) {
      handleAlerts(data.message);
      infiltration[`selected_${sinkType}s`] = [];
      localStorage.setItem(`${sinkType}_indices`,{})
      clearAndRemoveTable(Infiltration, sinkType, data.message.message)
      throw new Error('Filter returned 0 objects');
    }

    console.log('data', data);
    const sink_indices = {}
    
    addPointFeatureCollectionToLayer(data);

    addFeatureCollectionToTable(data)
    
    localStorage.setItem(`${sinkType}_indices`, JSON.stringify(sink_indices));

    return {'infiltration': infiltration, sinkType: sinkType}
}).then(data => {
  tableCheckSelectedItems(data.infiltration, data.sinkType)
})
.catch(error => console.error("Error fetching data:", error))
.finally(() => {
    // Always hide spinner & enable button
    spinner.hide();
    $button.prop('disabled', false);
  });
};


function getInfiltrationResults() {
    const infiltration = Infiltration.loadFromLocalStorage();
    console.log(typeof infiltration, infiltration);              // should log "object"
    console.log(typeof JSON.stringify(infiltration)); 
    fetch('get_infiltration_results/', {
      method: 'POST',
      body: JSON.stringify(infiltration),
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
      },
      credentials: 'same-origin'   
    })
    .then(response => response.json())
    .then(data => {
      if (data.message.success) {
        console.log('getInfiltration data', data);     
        let resultMap = addFeatureCollectionToLayer({dataInfo: data.inlet_data_info, featureCollection: data.inlet_feature_collection}, true)
        
        resultMap = addFeatureCollectionToLayer({dataInfo: data.sink_data_info, featureCollection: data.sink_feature_collection}, false, resultMap)

        resultMap= addFeatureCollectionToLayer({dataInfo: data.enlarged_sink_data_info, featureCollection: data.enlarged_sink_feature_collection}, false, resultMap)

        resultMap = addFeatureCollectionToLayer({dataInfo: data.sink_embankment_data_info, featureCollection: data.sink_embankment_feature_collection}, false, resultMap)

        console.log('Result Map: ', resultMap)

        
        // console.log(resultMap)
        createResultTable({
          dataInfo: data.result_data_info, 
          inlets: data.results,
          inletDataInfo: data.inlet_data_info,
          waterbodyDataInfo: {
            'lake': data.lake_data_info, 
            'stream': data.stream_data_info
          },
          sinkDataInfo: {
            'sink': data.sink_data_info, 
            'enlarged_sink': data.enlarged_sink_data_info,           
          },
        })


        // $('#toolboxPanel.toggle-sink-result').off('change')
        $('#toolboxPanel').on('change', '.toggle-sink-result', function () {
              const inletId = $(this).attr('inlet-id');
              const sinkId  = $(this).attr('sink-id');
              const sinkEmbankmentId = $(this).attr('sink-embankment-id');
              const show    = $(this).is(':checked');

              // Direct map lookup - FAST and CLEAN
              const inletLayer = resultMap[inletId];
              const sinkLayer  = resultMap[sinkId];

              if (inletLayer) {
                  show ? map.addLayer(inletLayer) : map.removeLayer(inletLayer);
              }
              if (sinkLayer) {
                  show ? map.addLayer(sinkLayer) : map.removeLayer(sinkLayer);
              }
              if (sinkEmbankmentId) {
                const sinkEmbankmentLayer = resultMap[sinkEmbankmentId];
                if (sinkEmbankmentLayer) {
                    show ? map.addLayer(sinkEmbankmentLayer) : map.removeLayer(sinkEmbankmentLayer);
                }
            } 
          });


        const resultTab = document.getElementById('navInfiltrationResult');
        

        resultTab.classList.remove('disabled');
        resultTab.removeAttribute('aria-disabled');

        // Activate the tab using Bootstrap's API
        const tab = new bootstrap.Tab(resultTab);
        tab.show();
        
        // map.addLayer(Layers.inletConnectionsFeatureGroup)
        map.removeLayer(Layers.sink);
        map.removeLayer(Layers.enlarged_sink);
        map.addLayer(Layers.stream);
        map.addLayer(Layers.lake);

      } else {
        handleAlerts(data.message);
      }
  });
};

export function initializeInfiltration() {
  console.log('Initialize Infiltraion');
  let inletVolumeChart;

  initializeSliders();
      
  const forms = document.querySelectorAll('.weighting-form')
  forms.forEach(form => { 
    const sliderList = form.querySelectorAll('input.single-slider');
    const length = sliderList.length;   
    const sliderObj = {};
    let index = 0;
    sliderList.forEach(slider => {
      sliderObj[index] = {
        'val': slider.value,
        'name': slider.name,
        'slider': slider
      };
      index++;
    });
    
    sliderList.forEach(slider => {
      slider.addEventListener('change', function (e) {
        const infiltration = Infiltration.loadFromLocalStorage();
        const changedSlider = e.target;

        const startIndex = Object.keys(sliderObj).find(
          key => sliderObj[key].slider === changedSlider
        );
        // let changedSlider = sliderObj[startIndex].slider;
        const newVal = parseInt(changedSlider.value);
        let diff = newVal - sliderObj[startIndex].val;
        
        sliderObj[startIndex].val = newVal;
        infiltration[changedSlider.name] = sliderObj[startIndex].val;
        console.log("Slider ", startIndex, "new value", newVal, "diff", diff);

        let remainingDiff = diff;
        
        let nextIndex = (parseInt(startIndex) + 1) % length;
        while (remainingDiff !== 0) {

        let sObj = sliderObj[nextIndex];
        let slider = sObj.slider;
        let currentVal = parseInt(slider.value);
        let newVal = currentVal - remainingDiff;
    
        // Clamp between 0 and 100
        if (newVal < 0) {
          remainingDiff = - newVal; 
          newVal = 0;
        } else if (newVal > 100) {
          remainingDiff = newVal - 100;
          newVal = 100;
        } else {
          remainingDiff = 0;
        }
        sObj.val = newVal;
        infiltration[sObj.name] = newVal;
        slider.value = newVal;
        slider.dispatchEvent(new Event('input', { bubbles: true }));
    
        nextIndex = (nextIndex + 1) % length;

        if (nextIndex == startIndex) break;
      }
      infiltration.saveToLocalStorage();
      });
    });

    const resetBtn = form.querySelector('input.reset-all');

    // this is unique to infiltration
    resetBtn.addEventListener('click', function (e) {
      const infiltration = Infiltration.loadFromLocalStorage(); 
      Object.keys(sliderObj).forEach(idx => {
        infiltration[sliderObj[idx].name] = parseFloat(sliderObj[idx].slider.dataset.defaultValue);
        sliderObj[idx].slider.value = parseFloat(sliderObj[idx].slider.dataset.defaultValue);
        sliderObj[idx].slider.dispatchEvent(new Event('input'));
        sliderObj[idx].val = parseFloat(sliderObj[idx].slider.dataset.defaultValue);
      });
      infiltration.saveToLocalStorage();
    });
  });




    $('#toolboxPanel').off('change'); // Remove any previous change event handlers
    addChangeEventListener(Infiltration);
    $('#toolboxPanel').on('change', function (event){
      const $target = $(event.target);
      if ($target.hasClass('toggle-sink-result')) {
        console.log('toggle-sink-result')
        const dataType = $target.data('type');
        const inletId = `${dataType}_${$target.data('id')}`;
        const sinkLayerId = `${dataType}_${$target.attr('layer-id')}`;
        
          Layers[dataType].eachLayer(layer => {
            if (layer.customId === sinkLayerId || layer.customId === inletId) {
              if ($target.is(':checked')) {
                Layers[dataType].addLayer(layer);
              } else {
                Layers[dataType].removeLayer(layer)
              }
            }
          });
        
      }
    });



    $('#toolboxPanel').off('click');
    addClickEventListenerToToolboxPanel(Infiltration)
    $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.hasClass('filter-sinks')) {
      filterSinks($target);   
    // } else if ($target.hasClass('filter-waterbodies')) {
    //   getWaterBodies($target);  
    } else if ($target.attr('id') === 'btnGetInfiltrationResults') {
        getInfiltrationResults(); 
    } else if ($target.attr('id') === 'navInfiltrationSinks') {
        map.addLayer(Layers.sink);
    } else if ($target.attr('id') === 'navInfiltrationEnlargedSinks') {
        map.addLayer(Layers.enlarged_sink);
    } else if ($target.attr('id') === 'navInfiltrationResult') {
        map.removeLayer(Layers.sink);
        map.removeLayer(Layers.enlarged_sink);
    } 
    }); 


    
    const infiltration = Infiltration.loadFromLocalStorage();
    loadProjectToGui(infiltration);
    
console.log('GETTING LAYER: ', Layers)
}

