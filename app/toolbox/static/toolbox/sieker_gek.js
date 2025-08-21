import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown, getBsColor } from '/static/shared/utils.js';
import { updateDropdown, addChangeEventListener, addClickEventListenerToTable,  tableCheckSelectedItems, addFeatureCollectionToTable, addFeatureCollectionToLayer, addFeatureCollectionResultCards } from '/static/toolbox/toolbox.js';
import { ToolboxProject} from '/static/toolbox/toolbox_project.js';
import { SiekerGek } from '/static/toolbox/sieker_gek_model.js';
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


const siekerGekFeatureGroup = new L.FeatureGroup()
siekerGekFeatureGroup.toolTag = 'sieker-gek';

const siekerFilteredGekFeatureGroup = new L.FeatureGroup()
siekerFilteredGekFeatureGroup.toolTag = 'sieker-gek';

// function createSiekerGekTableSettings() {
//   return {
//     "order": [[1, "asc"]],
//     "searching": false,
//     "columnDefs": [
//       {
//         "targets": 0, // Select a checkbox
//         "orderable": false,
//         "searchable": false
//       },
//       {
//         "targets": 1, // Name
//         "orderable": true,
//         "searchable": true
//       },
//       {
//         "targets": 2, // Document
//         "orderable": true,
//         "searchable": false
//       },
//       {
//         "targets": 3, // current landusage
//         "orderable": true,
//         "searchable": false
//       },
//       {
//         "targets": 4, // planning segment
//         "orderable": true,
//         "searchable": false
//       },
//       {
//         "targets": 5, // total number of measures
//         "orderable": true,
//         "searchable": false
//       },
//     ]
//   };
// }




function filterSiekerGeks() {
  const project = SiekerGek.loadFromLocalStorage();
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
      siekerFilteredGekFeatureGroup.clearLayers();
      // TODO in dataInfo: number of all measures vs. number of filtered measures. ADD THE LADDER!
      

    const dataInfoResult = {
      "dataType": "filtered_sieker_gek",
      "featureColor": "var(--bs-success)",
      "className": "gek polygon",
      "featureType": "polygon",
      "tableCaption": "Gewässerentwicklungskonzepte",
      "popUp": {
        "header": "name"
      },
      "properties": [
        {
          "popUp": false,
          "table": false,
          "title": "id",
          "valueName": "id",
          "href": false
        },
        {
          "popUp": false,
          "table": true,
          "title": "Name",
          "valueName": "name",
          "href": false
        },
        {
          "popUp": true,
          "table": true,
          "title": "Anzahl der Einzelmaßnahmen",
          "valueName": "number_of_measures",
          "href": false
        },
        {
          "popUp": true,
          "table": true,
          "title": "Aktuelle Flächennutzung",
          "valueName": "current_landusage",
          "href": false
        },
        {
          "popUp": true,
          "table": true,
          "title": "Planungsabschnitt",
          "valueName": "planning_segment",
          "href": false
        },
        {
          "popUp": true,
          "table": true,
          "title": "Wasserverband",
          "valueName": "assosiaction",
          "href": false
        },
        {
          "popUp": true,
          "table": true,
          "title": "Dokument",
          "valueName": "document",
          "href": false
        }
      ],
      "tableLength": 6
    }
    addFeatureCollectionToLayer(data.featureCollection, dataInfoResult, siekerFilteredGekFeatureGroup);
    addFeatureCollectionToTable(SiekerGek, data.featureCollection, dataInfoResult)
    addFeatureCollectionResultCards(data.featureCollection, data.dataInfo, data.measures)

      
      // addFeatureCollectionToTable(SiekerGek, data.featureCollection, data.dataInfo)
      // feautureCollectionToLayerAndTable(SiekerGek, data.featureCollection, data.dataInfo, siekerFilteredGekFeatureGroup);
      const measuresTab = $('#navSiekerGekMeasures')
      const tab = new bootstrap.Tab(measuresTab);
      tab.show();

    }
  })

};

export function initializeSiekerGek(data) {

  const userField = ToolboxProject.loadFromLocalStorage().userField;

  const siekerGek = new SiekerGek();
  siekerGek.userField = userField;
  siekerGek.saveToLocalStorage();


  removeLegendFromMap(map);
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag && layer.toolTag !== 'sieker-gek') {
            map.removeLayer(layer);
        }
        });
  console.log('Initialize Sieker Gek');
  map.addLayer(siekerGekFeatureGroup);
  
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
   

    addFeatureCollectionToLayer(data.featureCollection, data.dataInfo, siekerGekFeatureGroup)
    addFeatureCollectionToTable(SiekerGek, data.featureCollection, data.dataInfo)
    
    
    addClickEventListenerToTable(SiekerGek)


    document.getElementById('cardSiekerGekTable').classList.remove('d-none');
  
  $('#toolboxPanel').off('change');

  addChangeEventListener(SiekerGek);




  $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.hasClass('toolbox-back-to-initial')) {
      $('#toolboxButtons').removeClass('d-none');
        $('#toolboxPanel').addClass('d-none');
        
    } else if ($target.attr('id') === 'btnFilterSiekerGeks') {
      const project = SiekerGek.loadFromLocalStorage();
      if (project.selected_sieker_geks.length === 0) {
        handleAlerts({'success': false, 'message': 'Bitte wählen Sie Gewässer aus!'})
      } else {
        map.removeLayer(siekerGekFeatureGroup);
        map.addLayer(siekerFilteredGekFeatureGroup);
        filterSiekerGeks();
      }
      
    
    } else if ($target.attr('id') === 'toggleSiekerGeks') {
      if (map.hasLayer(siekerGekFeatureGroup)) {
        map.removeLayer(siekerGekFeatureGroup);
        $target.text('Senken einblenden');
      } else {
          map.addLayer(siekerGekFeatureGroup);
          $target.text('Senken ausblenden');
      }
    }
    }); 

  $('#navSiekerGek').on('shown.bs.tab', function (event) {
    const targetPane = $($(event.target).attr('href')); 
    if (targetPane.hasClass('active')) {
      map.addLayer(siekerGekFeatureGroup);
      map.removeLayer(siekerFilteredGekFeatureGroup);
    }
  });

  $('#navSiekerGekMeasures').on('click', function (event) {
    const targetPane = $($(event.target).attr('href'));
    if (targetPane.hasClass('active')) {
      map.removeLayer(siekerGekFeatureGroup);
      map.addLayer(siekerFilteredGekFeatureGroup);
    }
  });


  function selectGek(event) {
    if (event.target.classList.contains('select-gek')) {
      const gekId = event.target.getAttribute('gekId');
      const gekType = event.target.getAttribute('data-type');
      console.log('gekId', gekId);
      console.log('gekType', gekType);

      const checkbox = document.querySelector(`.gek-select-checkbox[data-type="${gekType}"][data-id="${gekId}"]`);
      checkbox.checked = !checkbox.checked;
      checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    }
  };

  // TODO This is not really working because the checkboxes of the gek table are not always accessible - only the ones visible are accessible
  $('#map').on('click', selectGek);

  $('input[type="checkbox"][name="landuse"][prefix="gek"]').prop('checked', true);
  $('input[type="checkbox"][name="landuse"][prefix="gek"]').trigger('change');

  $('input[type="range"]').trigger('change');

};

