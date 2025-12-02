import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown, getBsColor } from '/static/shared/utils.js';
import { 
  updateDropdown, 
  addChangeEventListener, 
  addClickEventListenerToToolboxPanel,  
  tableCheckSelectedItems, 
  addFeatureCollectionToTable, 
  addFeatureCollectionToLayer, 
  loadProjectToGui,
  createDetailRows, 
  clearAndRemoveTable,
} from '/static/toolbox/toolbox.js';
import { ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { SiekerGek } from '/static/toolbox/sieker_gek_model.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import {Layers} from '/static/toolbox/layers.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 

} from '/static/shared/map_sidebar_utils.js';


function getAllSiekerGeks(project) {
  console.log('Check 1')
  fetch('get_all_sieker_geks/', {
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
      Layers['sieker_gek'].clearLayers();
      // TODO in dataInfo: number of all measures vs. number of filtered measures. ADD THE LADDER!
      
      console.log('GEK', data)
      addFeatureCollectionToLayer(data, true);
      const table = addFeatureCollectionToTable({
        featureCollection: data.featureCollection,
        dataInfo: data.dataInfo,
        tableClasses: 'table table-hover',
      });
      tableCheckSelectedItems(project, data.dataInfo.dataType)


    } else {
      clearAndRemoveTable(SiekerGek, 'sieker_gek', data.message.message)
    }
    return data.dataInfo
  })

};


function filterSiekerGeks(project) {
  console.log('Check 2')
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
      // Layers['sieker_gek'].clearLayers();
      // TODO in dataInfo: number of all measures vs. number of filtered measures. ADD THE LADDER!
      
      console.log('GEK', data)
      addFeatureCollectionToLayer(data, true);
      const table = addFeatureCollectionToTable({
        featureCollection: data.featureCollection,
        dataInfo: data.dataInfo,
        tableClasses: 'table',
        rowClasses: 'table-parent-row',
      })
      createDetailRows(table, data.featureCollection, data.dataInfo, addResultCards)
      
      // addFeatureCollectionResultCards(data.dataInfo, data.measures)

      const measuresTab = $('#navSiekerGekMeasures')
      const tab = new bootstrap.Tab(measuresTab);
      tab.show();

    } else {
      clearAndRemoveTable(SiekerGek, 'sieker_gek', data.message.message)
    }

  })
  .then(tableCheckSelectedItems(project, 'sieker_gek')
  )
};

function addResultCards( dataInfo, featureProperties) {
    console.log("Creating card")

        const cardBody = document.createElement('div');
        cardBody.classList.add('card-body')
        // card
        cardBody.innerHTML = `<h4 class="card-title m-3">${featureProperties.name} Abschnitt ${featureProperties.planning_segment}</h4>`;
        
        const card = document.createElement('div');
        card.classList.add("card")
        card.classList.add("mb-3")
        // card.classList.add("gek-result-card")
        card.setAttribute('data-type', dataInfo.dataType)
        card.setAttribute('data-id', featureProperties.id)


        featureProperties.measures.forEach(measure => {
          console.log('Measure', measure)
            const innerCard = document.createElement('div');
            innerCard.classList.add("card")
            innerCard.classList.add("mb-3")
            // innerCard.setAttribute('data-type', measure.dataType)
            innerCard.setAttribute('data-id',measure.id)

            const innerCardBody = document.createElement('div');
            innerCardBody.classList.add("card-body")
            const items = measure.description.split(',').map(s => s.trim()).filter(Boolean);
            const bulletPoints = `<ul>${items.map(item => `<li>${item}</li>`).join('')}</ul>`;
            innerCardBody.innerHTML = `
                <h5 class="card-title">${measure.gek_measure}</h5>
                <b>Anzahl:</b><span> ${measure.quantity}</span></br>
                <b>Kosten:</b><span> ${measure.costs} €</span></br>
                <div class="result-text-box">${bulletPoints}</div>
            `;
        
            innerCard.appendChild(innerCardBody)
            cardBody.append(innerCard)
        })
        // card.appendChild(cardBody)

  return cardBody.outerHTML;
}

function getLowerSliderVal(sliderLabels, sliderValue) {
  const keys = Object.keys(sliderLabels).map(Number).filter(k => k <= sliderValue); 
  return Math.max(...keys);
}

function getUpperSliderVal(sliderLabels, sliderValue) {
  const keys = Object.keys(sliderLabels).map(Number).filter(k => k <= sliderValue); 
  return Math.min(...keys);
}



export function initializeSiekerGek(data) {
  const project = SiekerGek.loadFromLocalStorage();
  console.log('picked up', project);
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
      console.log(sliderLabels)
      let sliderVal = getLowerSliderVal(sliderLabels, slider.value)
      sliderLabelLeft.innerText = sliderLabels[sliderVal];
    });
  }
  // end of string labelled slider
   

  getAllSiekerGeks(project);
  
  $('#toolboxPanel').off('change');
  $('#toolboxPanel').off('click');
  
  addChangeEventListener(SiekerGek);
  addClickEventListenerToToolboxPanel(SiekerGek)

  // $('.table-select-all').prop('checked', true);
  // $('.table-select-all').trigger('change')

  $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.hasClass('filter-geks')) {
      const project = SiekerGek.loadFromLocalStorage();
      if (project.selected_sieker_geks.length === 0) {
        handleAlerts({'success': false, 'message': 'Bitte wählen Sie Gewässer aus!'})
      } else {
        console.log('Check 3')
        filterSiekerGeks(project);
      }

    }
    }); 

  $('#navSiekerGek').on('shown.bs.tab', function (event) {
    console.log('Check 4')
    const targetPane = $($(event.target).attr('href')); 
    if (targetPane.hasClass('active')) {
      map.addLayer(Layers['sieker_gek']);
      map.removeLayer(Layers['filtered_sieker_gek']);
    }
  });

  $('#navSiekerGekMeasures').on('click', function (event) {
    console.log('Check 5')
    const targetPane = $($(event.target).attr('href'));
    if (targetPane.hasClass('active')) {
      map.removeLayer(Layers['sieker_gek']);
      map.addLayer(Layers['filtered_sieker_gek']);
    }
  });


  const siekerGek = new SiekerGek(project);
  siekerGek.saveToLocalStorage();
  loadProjectToGui(siekerGek);

};

