import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown, getBsColor } from '/static/shared/utils.js';
import { updateDropdown, addChangeEventListener, addClickEventListenerToToolboxPanel,  tableCheckSelectedItems, addFeatureCollectionToTable, addFeatureCollectionToLayer } from '/static/toolbox/toolbox.js';
import { ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { SiekerWetland } from '/static/toolbox/sieker_wetland_model.js';
import {Layers} from '/static/toolbox/layers.js';
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
  getCircleMarkerSettings, 
  getLegendItem,
  getLegendSettings,
  removeLegendFromMap,
  
} from '/static/shared/map_sidebar_utils.js';


const siekerWetlandFeatureGroup = new L.FeatureGroup()
siekerWetlandFeatureGroup.toolTag = 'sieker_wetland';

const siekerFilteredWetlandFeatureGroup = new L.FeatureGroup()
siekerFilteredWetlandFeatureGroup.toolTag = 'sieker_wetland';




function filterSiekerWetlands(project) {
  
  fetch('filter_sieker_wetlands/', {
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
      siekerFilteredWetlandFeatureGroup.clearLayers();
      // TODO in dataInfo: number of all measures vs. number of filtered measures. ADD THE LATTER!
      addFeatureCollectionToLayer(data);
      addFeatureCollectionToTable(data)
      addFeatureCollectionResultCards(data.dataInfo, data.measures)

      const measuresTab = $('#navSiekerWetlandMeasures')
      const tab = new bootstrap.Tab(measuresTab);
      tab.show();
    }
  })
};

function addFeatureCollectionResultCards( dataInfo, wetlandMeasures) {
    console.log(wetlandMeasures)
    console.log("Creating card")
    const infoCard = document.getElementById('sieker_wetland-info-card');
    const infoCardBody = document.getElementById('sieker_wetland-info-card-body');
    infoCardBody.innerHTML = '';
    wetlandMeasures.forEach(wetland => {
        const cardBody = document.createElement('div');
        cardBody.classList.add('card-body')
        // card
        cardBody.innerHTML = `<h4 class="card-title m-3">${wetland.name} Abschnitt ${wetland.planning_segment}</h4>`;
        
        const card = document.createElement('div');
        card.classList.add("card")
        card.classList.add("mb-3")
        card.classList.add("wetland-result-card")
        card.setAttribute('data-type', dataInfo.dataType)
        card.setAttribute('data-id', wetland.id)


        wetland.measures.forEach(measure => {
            const innerCard = document.createElement('div');
            innerCard.classList.add("card")
            innerCard.classList.add("mb-3")
            // innerCard.setAttribute('data-type', measure.dataType)
            innerCard.setAttribute('data-id',measure.id)

            const innerCardBody = document.createElement('div');
            innerCardBody.classList.add("card-body")
            innerCardBody.innerHTML = `
                <h5 class="card-title">${measure.wetland_measure}</h5>
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
    $('.wetland-result-card').hide();
}


export function initializeSiekerWetland(data) {

  const userField = ToolboxProject.loadFromLocalStorage().userField;

  const siekerWetland = new SiekerWetland();
  siekerWetland.userField = userField;
  siekerWetland.saveToLocalStorage();


  removeLegendFromMap(map);
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag && layer.toolTag !== 'sieker_wetland') {
            map.removeLayer(layer);
        }
        });
  console.log('Initialize Sieker Wetland');
  map.addLayer(siekerWetlandFeatureGroup);
  

   

    addFeatureCollectionToLayer(data)
    addFeatureCollectionToTable(data)
    
    
    

  $('.table-select-all').prop('checked', true);
  $('.table-select-all').trigger('change')
  $('#cardSiekerWetlandTable').removeClass('d-none');
  
  $('#toolboxPanel').off('change');

  addChangeEventListener(SiekerWetland);

  addClickEventListenerToToolboxPanel(SiekerWetland)
  $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
  if ($target.attr('id') === 'btnFilterSiekerWetlands') {
      const project = SiekerWetland.loadFromLocalStorage();
      if (project.selected_sieker_wetlands.length === 0) {
        handleAlerts({'success': false, 'message': 'Bitte wählen Sie Gewässer aus!'})
      } else {
        map.removeLayer(siekerWetlandFeatureGroup);
        map.addLayer(siekerFilteredWetlandFeatureGroup);
        filterSiekerWetlands(project);
      }
      return;  
    } else if ($target.attr('id') === 'toggleSiekerWetlands') {
      if (map.hasLayer(siekerWetlandFeatureGroup)) {
        map.removeLayer(siekerWetlandFeatureGroup);
        $target.text('Feuchtgebiete einblenden');
      } else {
          map.addLayer(siekerWetlandFeatureGroup);
          $target.text('Feuchtgebiete ausblenden');
      }
    }
    }); 

  $('#navSiekerWetland').on('shown.bs.tab', function (event) {
    const targetPane = $($(event.target).attr('href')); 
    if (targetPane.hasClass('active')) {
      map.addLayer(siekerWetlandFeatureGroup);
      map.removeLayer(siekerFilteredWetlandFeatureGroup);
    }
  });

  $('#navSiekerWetlandMeasures').on('click', function (event) {
    const targetPane = $($(event.target).attr('href'));
    if (targetPane.hasClass('active')) {
      map.removeLayer(siekerWetlandFeatureGroup);
      map.addLayer(siekerFilteredWetlandFeatureGroup);
    }
  });


  function selectWetland(event) {
    if (event.target.classList.contains('select-wetland')) {
      const wetlandId = event.target.getAttribute('wetlandId');
      const wetlandType = event.target.getAttribute('data-type');
      console.log('wetlandId', wetlandId);
      console.log('wetlandType', wetlandType);

      const checkbox = document.querySelector(`.table-select-checkbox[data-type="${wetlandType}"][data-id="${wetlandId}"]`);
      checkbox.checked = !checkbox.checked;
      checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    }
  };

  // TODO This is not really working because the checkboxes of the wetland table are not always accessible - only the ones visible are accessible
  $('#map').on('click', selectWetland);

  // $('input[type="checkbox"][type="sieker"][prefix="wetland"]').prop('checked', true);
  // $('input[type="checkbox"][name="landuse"][prefix="wetland"]').trigger('change');

  // $('input[type="range"]').trigger('change');

};

