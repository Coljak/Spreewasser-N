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



export function initializeSiekerGek([feature_collection, sliderLabels, userField]) {
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

  const slider = document.getElementById('gek_priority_slider');
  const sliderLabelLeft = document.getElementById('gek_priority_start_text');
  const sliderLabelRight = document.getElementById('gek_priority_value');
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

        let menuContent = popupContent + `<button class="btn btn-outline-secondary select-sieker-gek" data-sieker-gek-id="${feature.properties.id}">Auswählen</button>`;
        
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
                    <button class="btn btn-outline-secondary select-sieker-gek" data-sieker-gek-id="${feature.properties.id}">Auswählen</button>
                `)
                .openOn(map);

            setTimeout(() => {
                const button = document.querySelector('.select-sieker-gek');
                if (button) {
                    button.addEventListener('click', () => {
                        map.closePopup(); 
                        const gekId = button.getAttribute('data-sieker-gek-id');
                        console.log('Selected gek ID:', gekId);
                    });
                }
            }, 0);
        });
    }
});

// Store in a group for resetting clicks
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
              <td><input type="checkbox" class="sieker-gek-checkbox table-select-checkbox" data-type="sieker_gek" data-sieker-gek-id="${feature.properties.id}"></td>
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

    document.getElementById('cardSiekerGekTable').classList.remove('d-none');








      
  $('#toolboxPanel').off('change');

  addChangeEventListener(SiekerGek);

  // $('#toolboxPanel').on('change',  function (event) {
  //   const $target = $(event.target);
  //   const project = SiekerGek.loadFromLocalStorage();
  //   if ($target.hasClass('double-slider')) {
  //     const inputName = $target.attr('name');
  //     const minName = inputName + '_min';
  //     const maxName = inputName + '_max'; 
  //     const inputVals = $target.val().split(',');
  //     project[minName] = inputVals[0];
  //     project[maxName] = inputVals[1];
  //     project.saveToLocalStorage();
  //   } else if ($target.hasClass('single-slider')) {   
  //     const inputName = $target.attr('name'); 
  //     const inputVal = $target.val();
  //     project[inputName] = inputVal;
  //     project.saveToLocalStorage();
  //   }else if ($target.hasClass('form-check-input')) {
  //     // checkboxes 
  //     console.log("Checkbox!!")
  //     const inputId = $target.attr('id');
  //     console.log("inputId", inputId)
  //     const inputName = $target.attr('name');
  //     console.log("inputName", inputName)
  //     const inputPrefix = $target.attr('prefix');
  //     console.log("inputPrefix", inputPrefix)
  //     const inputValue = $target.attr('value');
  //     console.log("inputValue", inputValue)
  //     const inputChecked = $target.is(':checked');
  //     console.log("inputChecked", inputChecked)


  //     const index = project[inputName].indexOf(inputValue);
  //     console.log("index", index)

  //     if (index > -1) {
  //       // Value exists — remove it
  //       project[inputName] = project[inputName].filter(
  //         (v) => v !== inputValue
  //       );
  //       console.log('Checkbox unchecked:', inputId, '=', inputValue);
  //     } else {
  //       // Value does not exist — add it
  //       project[inputName].push(inputValue);
  //       console.log('Checkbox checked:', inputId, '=', inputValue);
  //     }
  //     project.saveToLocalStorage();

  //   } else if ($target.hasClass('sieker-gek-select-all-checkbox')) {
      
  //     const allSelected = $target.is(':checked');
      
  //     if (!allSelected) {
  //       project['selected_sieker_geks'] = [];
  //     }
  //     $('.gek-select-checkbox').each(function(){
  //       const $checkbox = $(this);
  //       $checkbox.prop('checked', allSelected);
  //       const gekId = $checkbox.data('id');
  //       if (allSelected) {
  //         console.log("Selected gek:", gekId);
  //         project['selected_sieker_geks'].push(gekId);
  //       } 
  //     })
  //     project.saveToLocalStorage();
  //   } else if ($target.hasClass('sieker-gek-select-checkbox')) {
  //     if ($target.is(':checked')) {
  //       console.log("Selected gek:", $target.data('id'));
  //       const project= SiekerGek.loadFromLocalStorage();
  //       project['selected_sieker_geks'].push($target.data('id'));
  //       project.saveToLocalStorage();

  //     } else {
  //       const gekId = $target.data('id');
  //       console.log("Selected gek:", gekId);
  //       const project= SiekerGek.loadFromLocalStorage();
  //       const index = project[key].indexOf(gekId);
  //       if (index > -1) {
  //         project[key].splice(index, 1);
  //       }
  //       project.saveToLocalStorage();
  //     }

  //       // You can trigger your map gek selection logic here
  //     };
  //   });




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

