import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, SiekerSink, updateDropdown } from '/static/toolbox/toolbox.js';
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


const siekerSinkFeatureGroup = new L.FeatureGroup()
siekerSinkFeatureGroup.toolTag = 'sieker-sink';


function createSinkTableSettings(indexVisible) {
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
        "targets": 1, // volume
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 2, // area
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 3, // sink_depth
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 4, // avg_depth
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 5, // max_elevation
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 6, // min_elevation
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 7, // urbanarea_percent
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 8, // wetlands_percent 
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 9, // distance_t
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 10, // dist_lake
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 10, //waterdist
        "orderable": true,
        "searchable": false
      },
      {
        "targets": 11, // umsetzbark 
        "orderable": true,
        "searchable": false
      },
    ]
  }
}

function getSiekerSinks(sinkType, featureGroup) {
  let url = 'filter_sieker_sinks/';
  
  const project = SiekerSink.loadFromLocalStorage();
  fetch(url, {
    method: 'POST',
    body: JSON.stringify(project),
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
    }
  })
  .then(response => response.json())
  .then(data => {
    featureGroup.clearLayers();
    console.log('project', project);
  
    const selected_sinks = project['selected_sinks'];
    if (data.message.success) {
      
      project['selected_sinks'] = [];
      
      // Initialize marker cluster
      let clusterGroup = L.markerClusterGroup();
      let ids = [];

      const tableContainer = document.getElementById('sieker-sink-table-container');

      let tableHTML = ` 
        <table class="table table-bordered table-hover" id="sieker-sink-table">
          <caption>Senke</caption>
          <thead>
            <tr>
              <th><input type="checkbox" class="sink-select-all-checkbox" data-type="sieker_sink">Select all</th>
              <th>Volumen (m³)</th>
              <th>Fläche (m²)</th>
              <th>Tiefe (m)</th>
              <th>Ø Tiefe (m)</th>
              <th>Min. Elevation</th>
              <th>Max. Elevation</th> 
              <th>Urbane Fläche (%)</th>
              <th>Fläche Feuchtgebiet (%)</th>
              <th>Distanz t???</th>
              <th>Distanz See</th>
              <th>Distanz Wasser</th>
              <th>Umsetzbarkeit</th>
            </tr>
          </thead>
          <tbody>
      `;
      console.log('data', data);
      const sink_indices = {}



      data.feature_collection.features.forEach(feature => {
        console.log('feature', feature);
        const p = feature.properties;
        const { id, ...props } = p;
        sink_indices[id] = props;
        ids.push(id);

        let color = 'red';
        if (feature.properties.umsetzbark === 'mittel') {
          color = 'orange';
        } else if (feature.properties.umsetzbark === 'leicht') {
          color = 'green';  
        }

        const circleMarkerSettings = getCircleMarkerSettings(color);
        const marker = L.circleMarker([feature.coordinates[1], feature.coordinates[0]], {
          ...circleMarkerSettings,
          className: 'circle-marker',
        });

        marker.bindPopup(`
            <b>Volumen:</b> ${p.volume} m³<br>
            <b>Fläche:</b> ${p.area} m²<br>
            <b>Tiefe:</b> ${p.sink_depth} m<br>
            <b>Ø Tiefe:</b> ${p.avg_depth} m<br>
            <b>Min. Elevation:</b> ${p.min_elevation} (m)<br>
            <b>Max. Elevation:</b> ${p.max_elevation} (m)<br>
            <b>Urbane Fläche (%):</b> ${p.urbanarea_percent} (m)<br>
            <b>Fläche Feuchtgebiet (%):</b> ${p.wetlands_percent} (m)<br>
            <b>Distanz t???:</b> ${p.distance_t} (m)<br>
            <b>Distanz See:</b> ${p.dist_lake} (m)<br>
            <b>Distanz Wasser:</b> ${p.waterdist} (m)<br>
            <b>Umsetzbarkeit:</b> <span style="color: ${color}; font-weight: bold;">${p.umsetzbark}</span><br>
        `);
        marker.on('mouseover', function () {
          this.openPopup();
        });
        // Hide popup when not hovering
        marker.on('mouseout', function () {
            this.closePopup();
        });
        marker.on('contextmenu', function (event) {
          L.popup()
            .setLatLng(event.latlng)
            .setContent(`
                <b>Sink Options</b><br>
                <button class="btn btn-outline-secondary show-sink-outline" data-type="sieker_sink" sinkId=${p.id}">Show Sink Outline</button>
                <button class="btn btn-outline-secondary select-sink" data-type="sieker_sink" sinkId="${p.id}">Toggle Sink selection</button>
            `)
            .openOn(map);
        });
        // Add marker to cluster
        clusterGroup.addLayer(marker);

        tableHTML += `
        <tr data-sink-id="${p.id}">
            <td><input type="checkbox" class="sink-select-checkbox" data-type=sieker_sink data-id="${p.id}"></td>
            <td>${p.volume}</td>
            <td>${p.area}</td>
            <td>${p.sink_depth}</td>
            <td>${p.avg_depth}</td>
            <td>${p.min_elevation}</td>
            <td>${p.max_elevation}</td>
            <td>${p.urbanarea_percent}%</td>
            <td>${p.wetlands_percent}%</td>
            <td>${p.distance_t}</td>
            <td>${p.dist_lake}</td>
            <td>${p.waterdist}</td>
            <td  style="color: ${color};">${p.umsetzbark}</td>
          </tr>
        `;
        
      });


      // Data Table
      tableHTML += `</tbody></table>`;
      tableContainer.innerHTML = tableHTML;
      const tableSettings = createSinkTableSettings(false);
      $('#sieker-sink-table').DataTable(tableSettings);


      // display card with table

      const tableCard = document.getElementById('cardSiekerSinkTable');
      if (selected_sinks !== undefined && selected_sinks.length > 0) {
        selected_sinks.forEach(sinkId => {
          const checked = ids.includes(sinkId) ? true : false;
          const checkbox = document.querySelector(`.sink-select-checkbox[data-type="${sinkType}"][data-id="${sinkId}"]`);
          if (checkbox && checked) {
            checkbox.checked = checked;
            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
          }
        })
      }
      tableCard.classList.remove('d-none');

            localStorage.setItem(`sieker_sink_indices`, JSON.stringify(sink_indices));
      project.saveToLocalStorage();
      // Add the cluster group to the map
      featureGroup.addLayer(clusterGroup);

      removeLegendFromMap(map);

      const legendItems = [
          getLegendItem('Leicht umsetzbar', getCircleMarkerSettings( 'green')),
          getLegendItem('Mittel umsetzbar', getCircleMarkerSettings( 'orange')),
          getLegendItem('Schwer umsetzbar', getCircleMarkerSettings( 'red')),
        ]
      const legendSettings = getLegendSettings ('Umsetzbarkeit', legendItems) 
      const legend =  L.control.Legend(legendSettings).addTo(map);

    } else {

      handleAlerts(data.message);
      document.getElementById('sieker-sink-table-container').innerHTML = '';
      const tableCard = document.getElementById('cardSiekerSinkTable');
      tableCard.classList.add('d-none');
    }
})
.catch(error => console.error("Error fetching data:", error));
};



export function initializeSiekerSink() {
  removeLegendFromMap(map);
  map.eachLayer(function(layer) {
        console.log(layer.toolTag);
        if (layer.toolTag && layer.toolTag !== 'sieker-sink') {
            map.removeLayer(layer);
        }
        });
  console.log('Initialize Sieker Sink');
  map.addLayer(siekerSinkFeatureGroup);
  
  initializeSliders();
      
  $('#toolboxPanel').off('change');
  $('#toolboxPanel').on('change',  function (event) {
    const $target = $(event.target);
    const project = SiekerSink.loadFromLocalStorage();
    if ($target.hasClass('double-slider')) {
      const inputName = $target.attr('name');
      const minName = inputName + '_min';
      const maxName = inputName + '_max'; 
      const inputVals = $target.val().split(',');
      project[minName] = inputVals[0];
      project[maxName] = inputVals[1];
      project.saveToLocalStorage();
    } else if ($target.hasClass('single-slider')) {   
      const inputName = $target.attr('name'); 
      const inputVal = $target.val();
      project[inputName] = inputVal;
      project.saveToLocalStorage();
    }else if ($target.hasClass('form-check-input')) {
      // checkboxes 
      console.log("Checkbox!!")
      const inputId = $target.attr('id');
      console.log("inputId", inputId)
      const inputName = $target.attr('name');
      console.log("inputName", inputName)
      const inputPrefix = $target.attr('prefix');
      console.log("inputPrefix", inputPrefix)
      const inputValue = $target.attr('value');
      console.log("inputValue", inputValue)
      const inputChecked = $target.is(':checked');
      console.log("inputChecked", inputChecked)


      const index = project[inputName].indexOf(inputValue);
      console.log("index", index)

      if (index > -1) {
        // Value exists — remove it
        project[inputName] = project[inputName].filter(
          (v) => v !== inputValue
        );
        console.log('Checkbox unchecked:', inputId, '=', inputValue);
      } else {
        // Value does not exist — add it
        project[inputName].push(inputValue);
        console.log('Checkbox checked:', inputId, '=', inputValue);
      }
      project.saveToLocalStorage();

    } else if ($target.hasClass('sink-select-all-checkbox')) {
      
      const allSelected = $target.is(':checked');
      
      if (!allSelected) {
        project['selected_sieker_sinks'] = [];
      }
      $('.sink-select-checkbox').each(function(){
        const $checkbox = $(this);
        $checkbox.prop('checked', allSelected);
        const sinkId = $checkbox.data('id');
        if (allSelected) {
          console.log("Selected sink:", sinkId);
          project['selected_sieker_sinks'].push(sinkId);
        } 
      })
      project.saveToLocalStorage();
    } else if ($target.hasClass('sink-select-checkbox')) {
        if ($target.is(':checked')) {
          console.log("Selected sink:", $target.data('id'));
          const project= SiekerSink.loadFromLocalStorage();
          project['selected_sieker_sinks'].push($target.data('id'));
          project.saveToLocalStorage();

        } else {
          const sinkId = $target.data('id');
          console.log("Selected sink:", sinkId);
          const project= SiekerSink.loadFromLocalStorage();
          const index = project[key].indexOf(sinkId);
          if (index > -1) {
            project[key].splice(index, 1);
          }
          project.saveToLocalStorage();
        }

        // You can trigger your map sink selection logic here
      };
    });

  $('#toolboxPanel').on('click', function (event) {
    const $target = $(event.target);
    if ($target.hasClass('toolbox-back-to-initial')) {
      $('#toolboxButtons').removeClass('d-none');
        $('#toolboxPanel').addClass('d-none');
        
    } else if ($target.attr('id') === 'btnFilterSiekerSinks') {
      getSiekerSinks('siekerSink', siekerSinkFeatureGroup);
    
    } else if ($target.attr('id') === 'toggleSiekerSinks') {
      if (map.hasLayer(siekerSinkFeatureGroup)) {
        map.removeLayer(siekerSinkFeatureGroup);
        $target.text('Senken einblenden');
      } else {
          map.addLayer(siekerSinkFeatureGroup);
          $target.text('Senken ausblenden');
      }

    } 
    }); 

  function selectSink(event) {
    if (event.target.classList.contains('select-sink')) {
      const sinkId = event.target.getAttribute('sinkId');
      const sinkType = event.target.getAttribute('data-type');
      console.log('sinkId', sinkId);
      console.log('sinkType', sinkType);

      const checkbox = document.querySelector(`.sink-select-checkbox[data-type="${sinkType}"][data-id="${sinkId}"]`);
      checkbox.checked = !checkbox.checked;
      checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    }
  };

  // TODO This is not really working because the checkboxes of the sink table are not always accessible - only the ones visible are accessible
  $('#map').on('click', selectSink);

  $('input[type="checkbox"][name="feasibility"][prefix="sieker_sink"]').prop('checked', true);
  $('input[type="checkbox"][name="feasibility"][prefix="sieker_sink"]').trigger('change');

};

