import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown, getBsColor } from '/static/shared/utils.js';
import { updateDropdown, addChangeEventListener, addClickEventListenerToToolboxPanel,  tableCheckSelectedItems, addFeatureCollectionToTable, addFeatureCollectionToLayer, loadProjectToGui } from '/static/toolbox/toolbox.js';
import { ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { SiekerGek } from '/static/toolbox/sieker_gek_model.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import {Layers} from '/static/toolbox/layers.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  openUserFieldNameModal,

  getUserFieldIdByLeafletId, 
  getLeafletIdByUserFieldId, 
  getUserFieldsFromDb, 
  highlightLayer, 
  selectUserField,
  handleSaveUserField,
  dismissPolygon,
  getCircleMarkerSettings, 
  getLegendItem,
  getLegendSettings,
  removeLegendFromMap,
  
} from '/static/shared/map_sidebar_utils.js';





function filterSiekerGeks(project) {
  
  fetch('filter_sieker_geks/', {
    method: 'POST',
    body: JSON.stringify(project),
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    }
  }).then(
    response => response.json()
  ).then(data => {
    
    console.log(data)
    if(data.message.success) {
      Layers['filtered_sieker_gek'].clearLayers();
      // TODO in dataInfo: number of all measures vs. number of filtered measures. ADD THE LADDER!
      

    addFeatureCollectionToLayer(data);
    addFeatureCollectionToTable(data)
    addFeatureCollectionResultCards(data.dataInfo, data.measures)

    const measuresTab = $('#navSiekerGekMeasures')
    const tab = new bootstrap.Tab(measuresTab);
    tab.show();

    }
  })

};

function addFeatureCollectionResultCards( dataInfo, gekMeasures) {
    console.log(gekMeasures)
    console.log("Creating card")
    const infoCard = document.getElementById('sieker_gek-info-card');
    const infoCardBody = document.getElementById('sieker_gek-info-card-body');
    infoCardBody.innerHTML = '';
    gekMeasures.forEach(gek => {
        const cardBody = document.createElement('div');
        cardBody.classList.add('card-body')
        // card
        cardBody.innerHTML = `<h4 class="card-title m-3">${gek.name} Abschnitt ${gek.planning_segment}</h4>`;
        
        const card = document.createElement('div');
        card.classList.add("card")
        card.classList.add("mb-3")
        card.classList.add("gek-result-card")
        card.setAttribute('data-type', dataInfo.dataType)
        card.setAttribute('data-id', gek.id)


        gek.measures.forEach(measure => {
            const innerCard = document.createElement('div');
            innerCard.classList.add("card")
            innerCard.classList.add("mb-3")
            // innerCard.setAttribute('data-type', measure.dataType)
            innerCard.setAttribute('data-id',measure.id)

            const innerCardBody = document.createElement('div');
            innerCardBody.classList.add("card-body")
            innerCardBody.innerHTML = `
                <h5 class="card-title">${measure.gek_measure}</h5>
                <b>Anzahl:</b><span> ${measure.quantity}</span></br>
                <b>Kosten:</b><span> ${measure.costs} €</span></br>
                <div class="result-text-box">${measure.description}</div>
            `;
        
            innerCard.appendChild(innerCardBody)
            cardBody.append(innerCard)
        })
        card.appendChild(cardBody)
        infoCardBody.appendChild(card)
    })
    infoCard.style.display = '';
    $('.gek-result-card').hide();
}


export function initializeSiekerGek(data) {

  


  removeLegendFromMap(map);
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag && layer.toolTag !== 'sieker-gek') {
            map.removeLayer(layer);
        }
        });
  // console.log('Initialize Sieker Gek');
  // map.addLayer(Layers['sieker_gek']);
  
  initializeSliders();

  // This is only for the priority slider that has string labels not numbers
  const slider = document.getElementById('gek_priority_slider');
  const sliderLabelLeft = document.getElementById('gek_priority_start_text');
  const sliderLabelRight = document.getElementById('gek_priority_value');
  const sliderLabels = data['sliderLabels'];
  sliderLabelLeft.innerText = sliderLabels[Math.min(...Object.keys(sliderLabels).map(Number))];
  sliderLabelRight.innerText = sliderLabels[Math.max(...Object.keys(sliderLabels).map(Number))];

  if (slider && sliderLabels) {
    slider.addEventListener('change', function() {
      console.log('sliderChanged', slider.value);
      if (slider.value in sliderLabels) {
        sliderLabelLeft.innerText = sliderLabels[slider.value];
      }
    });
  }
  // end of string labelled slider
   

    addFeatureCollectionToLayer(data)
    addFeatureCollectionToTable(data)
    
    
    



  
  $('#toolboxPanel').off('change');
  $('#toolboxPanel').off('click');

  addChangeEventListener(SiekerGek);
  addClickEventListenerToToolboxPanel(SiekerGek)

  $('.table-select-all').prop('checked', true);
  $('.table-select-all').trigger('change')

  $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.attr('id') === 'btnFilterSiekerGeks') {
      const project = SiekerGek.loadFromLocalStorage();
      if (project.selected_sieker_geks.length === 0) {
        handleAlerts({'success': false, 'message': 'Bitte wählen Sie Gewässer aus!'})
      } else {
        map.removeLayer(Layers['sieker_gek']);
        map.addLayer(Layers['filtered_sieker_gek']);
        // TODO: unsauber- filtered_sieker_gek macht keien Sinn, oder? Toggle nicht eindeutig.
        filterSiekerGeks(project);
      }
      
    
    } else if ($target.attr('id') === 'toggleSiekerGeks') {
      if (map.hasLayer(Layers['sieker_gek'])) {
        map.removeLayer(Layers['sieker_gek']);
        $target.text('Senken einblenden');
      } else {
          map.addLayer(Layers['sieker_gek']);
          $target.text('Senken ausblenden');
      }
    }
    }); 

  $('#navSiekerGek').on('shown.bs.tab', function (event) {
    const targetPane = $($(event.target).attr('href')); 
    if (targetPane.hasClass('active')) {
      map.addLayer(Layers['sieker_gek']);
      map.removeLayer(Layers['filtered_sieker_gek']);
    }
  });

  $('#navSiekerGekMeasures').on('click', function (event) {
    const targetPane = $($(event.target).attr('href'));
    if (targetPane.hasClass('active')) {
      map.removeLayer(Layers['sieker_gek']);
      map.addLayer(Layers['filtered_sieker_gek']);
    }
  });



  $('input[type="checkbox"][name="landuse"][prefix="gek"]').prop('checked', true);
  $('input[type="checkbox"][name="landuse"][prefix="gek"]').trigger('change');

  $('input[type="range"]').trigger('change');
  const siekerGek = SiekerGek.loadFromLocalStorage();
  loadProjectToGui(siekerGek);

};

