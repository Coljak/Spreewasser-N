import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown, getBsColor } from '/static/shared/utils.js';
import { ToolboxProject, SiekerGek, updateDropdown, addChangeEventListener } from '/static/toolbox/toolbox.js';
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
  feautureCollectionToLayerAndTable,
} from '/static/shared/map_sidebar_utils.js';


const siekerGekFeatureGroup = new L.FeatureGroup()
siekerGekFeatureGroup.toolTag = 'sieker-gek';

function createSiekerGekTableSettings() {
  return {
    "order": [[1, "asc"]],
    "searching": false,
    "columnDefs": [
      {
        "targets": 0, // Select a checkbox
        "orderable": false,
        "searchable": false
      },
      {
        "targets": 1, // Name
        "orderable": true,
        "searchable": true
      },
      {
        "targets": 2, // Document
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 3, // current landusage
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 4, // planning segment
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 5, // total number of measures
        "orderable": true,
        "searchable": false
      },
    ]
  };
}


function geksToGui( data) {
  const feature_collection = data.feature_collection
  let layer = L.geoJSON(feature_collection, {
    style: {
        color: 'var(--bs-secondary)',
        className: 'gek polygon',
    },
    onEachFeature: function (feature, layer) {
      let popupContent = `
          <h6><b> ${feature.properties.name}</b></h6>
          <b>Anzahl der Einzelmaßnahmen zum Wasserrückhalt:</b> ${feature.properties.number_of_measures}<br>
          <b>Aktuelle Flächennutzung:</b> ${feature.properties.current_landusage}<br>
          <b>Planungsabschnitt:</b> ${feature.properties.planning_segment}<br>
          <b>Dokument: </b><a href="${feature.properties.document}" target="_blank">Link</a><br>
      `;

      let menuContent = popupContent + `<button class="btn btn-outline-secondary select-sieker-gek" data-id="${feature.properties.id}">Auswählen</button>`;
      
      layer.bindTooltip(popupContent);

      layer.on('mouseover', function () {
          // this.setStyle(highlightStyle);
          this.openTooltip();
      });

      layer.on('mouseout', function () {
          // Only reset to default if not clicked
          if (!this.options.isClicked) {
              // this.setStyle(defaultStyle);
          }
      });

      layer.on('click', function (e) {
            // Remove clicked from all
          const popUp = L.popup().setContent(menuContent);
          map.openPopup(popUp, layer.getBounds().getCenter());
          document.querySelectorAll('.polygon.clicked')
              .forEach(el => el.classList.remove('clicked'));

          // Add to this one
          let pathEl = e.target._path; // The actual SVG path element
          if (pathEl) {
              pathEl.classList.add('clicked');
          }
      });

      layer.on('contextmenu', function (event) {
        L.popup()
            .setLatLng(event.latlng)
            .setContent(`
                <h6><b> ${feature.properties.name}</b></h6>
                <button class="btn btn-outline-secondary select-sieker-gek" data-id="${feature.properties.id}">Auswählen</button>
            `)
            .openOn(map);

        setTimeout(() => {
          const button = document.querySelector('.select-sieker-gek');
          if (button) {
              button.addEventListener('click', () => {
                  map.closePopup(); 
                  const gekId = button.getAttribute('data-id');
                  console.log('Selected gek ID:', gekId);
              });
          }
        }, 0);
      });
    }
  });

  let layerGroup = L.featureGroup([layer]).addTo(map);

  layer.addTo(siekerGekFeatureGroup);
    layer.bringToFront();

    const tableContainer = document.getElementById('sieker-gek-table-container');
    let tableHTML = `
    <table class="table table-bordered table-hover" id="sieker-gek-table">
      <caption>Gewässerentwicklungskonzepte</caption>
      <thead>
        <tr>
            <th><input type="checkbox" class="sieker-gek-select-all-checkbox table-select-all" data-type="sieker_gek">Select all</th>
            <th>Name</th>
            <th>Anzahl Maßnahmen</th>
            <th>Landnutzung</th>
            <th>Planungsabschnitt</th>
            <th>Dokument</th>
        </tr>
      </thead>
      <tbody>
    `
    feature_collection.features.forEach(feature => {

      // Add to table
      tableHTML += `
          <tr>
              <td><input type="checkbox" class="sieker-gek-checkbox table-select-checkbox" data-type="sieker_gek" data-id="${feature.properties.id}"></td>
              <td>${feature.properties.name}</td>
              <td>${feature.properties.number_of_measures}</td>
              <td>${feature.properties.current_landusage}</td>
              <td>${feature.properties.planning_segment}</td>
              <td>${feature.properties.document}</td>
          </tr>`;    
    });
    tableHTML += `</tbody></table>`;
    tableContainer.innerHTML = tableHTML;
    const tableSettings = createSiekerGekTableSettings();
    $('#sieker-gek-table').DataTable(tableSettings);
};

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
    response => response.json
  ).then(data => {
    siekerGekFeatureGroup.clearLayers();
    
    if(data.message.success) {
      geksToGui(data)
    }
  })

};

export function initializeSiekerGek(data) {


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
  console.log('sliderLabels')
  console.log('sliderLabelLeft',sliderLabelLeft)
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
    // geksToGui(data)

    const dataInfo = {
        dataType: 'sieker_gek',
        featureColor: 'var(--bs-secondary)',
        className: 'gek polygon',
        featureType: 'polygon',
        tableCaption: 'Gewässerentwicklungskonzepte',
        popUp: {
          header: 'name'
        },
        properties: [{
          popUp : false,
          table: true,
          title:'Name',
          valueName: 'name',
          href: false,
          hrefTarget: null,
        },
          {
          popUp : true,
          table: true,
          title:'Anzahl der Einzelmaßnahmen',
          valueName: 'number_of_measures',
          href: false,
          hrefTarget: null,
        },
        {
          popUp : true,
          table: true,
          title:'Aktuelle Flächennutzung',
          valueName: 'current_landusage',
          href: false,
          hrefTarget: null,
        },
        {
          popUp : true,
          table: true,
          title:'Planungsabschnitt',
          valueName: 'planning_segment',
          href: false,
          hrefTarget: null,
        },
        {
          popUp : true,
          table: true,
          title:'Dokument',
          valueName: 'document',
          href: true,
          hrefTarget: null,
        },
      
      ],
        tableLength: 6
      }

    feautureCollectionToLayerAndTable(data.feature_collection, dataInfo, siekerGekFeatureGroup)


    document.getElementById('cardSiekerGekTable').classList.remove('d-none');
  
  $('#toolboxPanel').off('change');

  addChangeEventListener(SiekerGek);




  $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.hasClass('toolbox-back-to-initial')) {
      $('#toolboxButtons').removeClass('d-none');
        $('#toolboxPanel').addClass('d-none');
        
    } else if ($target.attr('id') === 'btnFilterSiekerGeks') {
      getSiekerGeks('siekerGek', siekerGekFeatureGroup);
    
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

  $('input[type="checkbox"][name="feasibility"][prefix="sieker_gek"]').prop('checked', true);
  $('input[type="checkbox"][name="feasibility"][prefix="sieker_gek"]').trigger('change');

};

