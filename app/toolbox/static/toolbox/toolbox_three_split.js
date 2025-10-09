import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import {  toolboxSinksOutline, updateDropdown } from '/static/toolbox/toolbox.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { ToolboxProject } from '/static/toolbox/toolbox_project.js';
import { SiekerSink } from '/static/toolbox/sieker_sink_model.js';
import { SiekerGek } from '/static/toolbox/sieker_gek_model.js';
import { SiekerSurfaceWaters } from '/static/toolbox/sieker_surface_waters_model.js';
import { Infiltration } from '/static/toolbox/infiltration_model.js';
import { initializeInfiltration } from '/static/toolbox/infiltration.js';
import { initializeSiekerSurfaceWaters } from '/static/toolbox/sieker_surface_waters.js';
import { initializeSiekerSink } from '/static/toolbox/sieker_sink.js';
import {initializeSiekerGek } from '/static/toolbox/sieker_gek.js';
import {initializeSiekerWetland } from '/static/toolbox/sieker_wetland.js';
import { TuMar } from '/static/toolbox/tu_mar_model.js';
import { initializeTuMar } from '/static/toolbox/tu_mar.js';

import { 
  projectRegion, 
  demOverlay,
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  openUserFieldNameModal,
  createNUTSSelectors,
  initializeSidebarEventHandler, 
  addLayerToSidebar, 
  getUserFieldIdByLeafletId, 
  getLeafletIdByUserFieldId, 
  getUserFieldsFromDb, 
  highlightLayer, 
  selectUserField,
  dismissPolygon,
} from '/static/shared/map_sidebar_utils.js';


document.addEventListener("DOMContentLoaded", () => {
  // Hide the coordinate form card from plain Monica
  const project = new ToolboxProject();
  project.saveToLocalStorage();

  // center map at geolocation
  getGeolocation()
    .then((position) => {
      map.setView([position.latitude, position.longitude], 12);
    })
    .catch((error) => {
        console.error(error.message);
        handleAlerts({ success: false, message: error.message });

        // Fallback: center map on projectRegion if geolocation fails
      if (typeof projectRegion !== 'undefined' && projectRegion.getBounds) {
        map.fitBounds(projectRegion.getBounds());
      } else {
        // Optional hard fallback if projectRegion is not defined
        map.setView([52.40, 14.174], 10);
      }
    });


  // dropDownMenu in the project modal
  $('#userFieldSelect').on('change', function () { 
    console.log('userFieldSelect change event');
    var userFieldId = $(this).val();
    let project = ToolboxProject.loadFromLocalStorage();
    // TODO: featureGroup as getFeatureGroup
    selectUserField(userFieldId,  project, featureGroup);
    
  });

  $('#saveToolboxProjectButton').on('click', () => {
    console.log('saveToolboxProjectButton clicked');
    
      // Get the project name field
      const projectNameInput = $('#id_project_name');
      const projectName = projectNameInput.val().trim();
  
      // Check if the project name is empty
      if (!projectName) {
          projectNameInput.addClass('is-invalid'); // Bootstrap class for red highlight
          projectNameInput.focus();
          return; // Stop execution if validation fails
      } else {
          projectNameInput.removeClass('is-invalid'); // Remove error class if fixed
      }
  

      const project = new ToolboxProject();
  
      try {
          project.userField = $('#userFieldSelect').val();
      } catch (e) {
          console.log('UserField not found');
      }

      try {
        project.toolboxType = $('#projectTypeSelect').val();
    } catch (e) {
        console.log('ProjectType not found');
    }
  
      project.name = projectName;
      project.description = $('#id_project_description').val();
  
      project.saveToLocalStorage();
  
      fetch('save-project/', {
          method: 'POST',
          body: JSON.stringify(project),
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCSRFToken(),
          }
      })
      .then(response => response.json())
      .then(data => {
          console.log('data', data);
          if (data.message.success) {
              project.id = data.project_id;
              // $('#project-info').find('.card-title').text('Project '+ data.project_name);
              addToDropdown(data.project_id, data.project_name, document.querySelector('.toolbox-project.form-select'));
              // updateDropdown('toolbox-project', data.project_id);
              handleAlerts(data.message);
              
              // $('.new-project-modal-form')[0].reset();
           
              $('#toolboxProjectModal').modal('hide');
              project.saveToLocalStorage();
          } else {
              handleAlerts(data.message);
          }
      });
  });


const demBounds = [
  [47.136744752, 15.57241882],
  [55.058996788, 5.564783468],
];
const toolboxBounds = [
  [51.9015194452089901, 14.5048979594768852],
  [52.7436194452089921, 13.4503979594768843]
];
const sinksBounds = [
  [51.903417526,14.473467455],
  [52.742055454,13.500732582]
];

// const demOverlay = L.imageOverlay(demUrl, demBounds, { opacity: 0.5, pane: 'overlayRasterPane' });
// const toolboxOverlaySoil = L.imageOverlay(toolboxUrl, toolboxBounds, { opacity: 1.0 });
// const toolboxOverlaySinks = L.imageOverlay(toolboxSinksUrl, sinksBounds, { opacity: 1.0 });


const toolboxOutlineInjection = new L.geoJSON(outline_injection, {
  attribution: 'Outline Injection',
  pane: 'overlayPolygonPane',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name, {
        direction: 'left',       // 'top', 'bottom', 'left', 'right', or 'auto'
        offset: [0, 0],         // x, y offset in pixels
        permanent: false,       // only show on hover
        sticky: true  
    });
  }
});

const toolboxOutlineSurfaceWater = new L.geoJSON(outline_surface_water, {
  attribution: 'Outline Surface Water',
  pane: 'overlayPolygonPane',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name, {
        direction: 'left',       // 'top', 'bottom', 'left', 'right', or 'auto'
        offset: [0, 0],         // x, y offset in pixels
        permanent: false,       // only show on hover
        sticky: true  
    });
  }
});

const toolboxOutlineInfiltration = new L.geoJSON(outline_infiltration, {
  attribution: 'Outline Infiltration',
  pane: 'overlayPolygonPane',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name, {
      direction: 'left',       // 'top', 'bottom', 'left', 'right', or 'auto'
      offset: [0, 0],         // x, y offset in pixels
      permanent: false,       // only show on hover
      sticky: true  
    });
  }
});

// const allRivers = L.geoJSON(all_rivers_feature_collection, {
//   style: {
//       color: 'hsl(187 98 66)',
//       className: 'all-rivers',
//   },
//   onEachFeature: function (feature, layer) {
//     let popupContent = 
//     `<h6><b> ${feature.properties['name']}</b></h6> `   
          
//   layer.on('add', function () {
//       if (layer._path) {
//           layer._path.setAttribute('data-type', 'all-rivers');
//           layer._path.setAttribute('data-id', feature.properties.id);
//       }
//   });
              
//   layer.bindTooltip(popupContent);
//   layer.on('mouseover', function () {
//           // this.setStyle(highlightStyle);
//         this.openTooltip();
//     });
//   }
// });

// const allLakes = L.geoJSON(all_lakes_feature_collection, {
//   style: {
//       color: 'hsl(191 96 55)',
//       className: 'all-lakes',
//   },
//   onEachFeature: function (feature, layer) {
//     let popupContent = 
//     `<h6><b> ${feature.properties['name']}</b></h6> `   
          
//   layer.on('add', function () {
//       if (layer._path) {
//           layer._path.setAttribute('data-type', 'all-lakes');
//           layer._path.setAttribute('data-id', feature.properties.id);
//       }
//   });
              
//   layer.bindTooltip(popupContent);
//   layer.on('mouseover', function () {
//           // this.setStyle(highlightStyle);
//         this.openTooltip();
//     });
//   }
// });


  const markers = L.markerClusterGroup({
      iconCreateFunction: function (cluster) {
      const count = cluster.getChildCount();

      const html = `
        <div class="custom-cluster-icon">
          <img src="/static/images/water-level-circle_green_small.png" alt="icon" />
          <span class="count">${count}</span>
        </div>
      `;

      return L.divIcon({
        html: html,
        className: 'water-level-cluster-wrapper',
      });
    }

  });



// //https://www.pegelonline.wsv.de/webservice/dokuRestapi
// fetch('https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json?includeTimeseries=true&includeCurrentMeasurement=true') // Replace with your actual API
//   .then(response => response.json())
//   .then(data => {
//     data.forEach(station => {
//       if (station.latitude && station.longitude) {
//         const marker = new L.Marker([station.latitude, station.longitude], {
//           icon: waterLevelPinIcon,
//           title: station.shortname || station.name // Use shortname or name as title
//         });

//         // Create tooltip content
//         const tooltipContent = `
//           <strong>${station.shortname}</strong><br>
//           Nummer: ${station.number}<br>
//           Behörde: ${station.agency}<br>
//           Gewässer: ${station.water?.shortname || 'N/A'}</br>
//           Flusskilometer: ${station.km || 'N/A'}<br>
//           Aktuelle Messung: ${station.timeseries[0].currentMeasurement?.value || 'N/A'} ${station.timeseries[0]?.unit || ''}<br>
//           Wasserstand: ${station.timeseries[0].currentMeasurement?.stateMnwMhw || 'N/A'},  ${station.timeseries[0].currentMeasurement?.stateNswHsw || ''}<br>
//           <a href="https://www.pegelonline.wsv.de/charts/OnlineVisualisierungGanglinie?pegeluuid=${station.uuid}&imgBreite=450&pegelkennwerte=HSW,GLW&dauer=300" target="_blank">Details</a><br>
//           <a href="https://www.pegelonline.wsv.de/webservices/zeitreihe/visualisierung?pegeluuid=${station.uuid}" target="_blank">Zeitreihe</a>
//         `;

//         marker.bindPopup(tooltipContent);
//         marker.bindTooltip(tooltipContent, {
//           permanent: false,
//           direction: 'top',
//           className: 'water-level-tooltip'
//         });
//         marker.on('click', function () {

//             marker.openPopup();

//         });
//         marker.on('mouseover', function () {
//           marker.openTooltip();
//         });
//         marker.on('mouseout', function () {
//           marker.closeTooltip();
//         });
//         markers.addLayer(marker);
//         ;
//       }
//     });
//     return markers
//   })
//   .catch(error => {
//     console.error('Error fetching data:', error);
//   });

  
  // markers.addTo(map);

  const overlayLayers = {
    "demOverlay": demOverlay,
    "projectRegion": projectRegion,
    // "toolboxOverlaySoil": toolboxOverlaySoil,
    // "toolboxOverlaySinks": toolboxOverlaySinks,
    "toolboxOutlineInjection": toolboxOutlineInjection,
    "toolboxOutlineSurfaceWater": toolboxOutlineSurfaceWater,
    "toolboxOutlineInfiltration": toolboxOutlineInfiltration,
    // "allLakes": allLakes,
    // "allRivers": allRivers,
    // "sinks": toolboxSinksOutline,
    "waterLevels": markers,
  };



  // toolbox specific overlays
  var featureGroup = new L.FeatureGroup({pane: "polygonPane",})
  map.addLayer(featureGroup);
  featureGroup.bringToFront();

  initializeMapEventlisteners(map, featureGroup);
  initializeDrawControl(map, featureGroup);
  
  initializeSidebarEventHandler({
    sidebar: document.querySelector(".sidebar-content"),
    map,
    overlayLayers,
    getUserFields: () => localStorage.getItem("userFields") ? JSON.parse(localStorage.getItem("userFields")) : {},
    getFeatureGroup: () => { return featureGroup; },
    getProject: () => ToolboxProject.loadFromLocalStorage(),
  });

  createNUTSSelectors({getFeatureGroup: () => { return featureGroup; }});





  // document.getElementById('toolbox-project-save').addEventListener('click', function () {
  //   const project = ToolboxProject.loadFromLocalStorage();

  //   saveProject(project);
  // });



  function startInfiltration() {
    console.log('start Infiltration')
    const userField = ToolboxProject.loadFromLocalStorage().userField;


    // const userField = project.userField;
    if (userField) {


      fetch('load_infiltration_gui/' + userField + '/')
      .then(response => response.json())
      .then(data => {
        if (!data.success) {
          handleAlerts(data);
          return;
        }
          // Replace HTML content
        $('#toolboxButtons').addClass('d-none');
        $('#toolboxPanel').removeClass('d-none');
        $('#toolboxPanel').html(data.html);
      })
      .then(() => {
        initializeInfiltration(userField);
        // initializeSliders();

      })
      // .catch(error => console.error("Error fetching data:", error));
    } else {
      handleAlerts({ success: false, message: 'Please select a user field!' });
    }
  };

// Sieker
  function startSurfaceWaters() {
    console.log('startSurfaceWaters')
    const userField = ToolboxProject.loadFromLocalStorage().userField;

    const siekerSurfaceWaters = new SiekerSurfaceWaters();
    siekerSurfaceWaters.userField = userField;
    siekerSurfaceWaters.saveToLocalStorage();
    // const userField = project.userField;
    if (userField) {
    
      fetch('load_surface_waters_gui/' + userField + '/')
      .then(response => response.json())
      .then(data => {
        console.log('data received', data)
        if (!data.success) {
          handleAlerts(data);
          return;
        }
          // Replace HTML content
        $('#toolboxButtons').addClass('d-none');
        $('#toolboxPanel').removeClass('d-none');
        $('#toolboxPanel').html(data.html);
        console.log('returning data.layers', data.layers)
        return data.layers;
      })
      .then((data) => {
        console.log('Before initialize, ', data)
          initializeSiekerSurfaceWaters(data);
          
      })
      .catch(error => console.error("Error fetching data:", error));
    } else {
      handleAlerts({ success: false, message: 'Please select a user field!' });
    }
  };


  function startSiekerSinks() {
    console.log('start Infiltration')
    const userField = ToolboxProject.loadFromLocalStorage().userField;

    // const userField = project.userField;
    if (userField) {
    
      fetch('load_sieker_sink_gui/' + userField + '/')
      .then(response => response.json())
      .then(data => {
        if (!data.success) {
          handleAlerts(data);
          return;
        }
          // Replace HTML content
        $('#toolboxButtons').addClass('d-none');
        $('#toolboxPanel').removeClass('d-none');
        $('#toolboxPanel').html(data.html);
      })
      .then(() => {
        initializeSiekerSink(userField);
        // initializeSliders();

      })
      // .catch(error => console.error("Error fetching data:", error));
    } else {
      handleAlerts({ success: false, message: 'Please select a user field!' });
    }
  };


  function startSiekerGeks() {
    console.log('start Sieker Geks')
    
    const userField = ToolboxProject.loadFromLocalStorage().userField;
    const siekerGek = new SiekerGek;
    siekerGek.saveToLocalStorage();

    // const userField = project.userField;
    if (userField) {
      
      fetch('load_sieker_gek_gui/' + userField + '/')
      .then(response => response.json())
      .then(data => {
        if (!data.success) {
          handleAlerts(data);
          return;
        }
          // Replace HTML content
        $('#toolboxButtons').addClass('d-none');
        $('#toolboxPanel').removeClass('d-none');
        $('#toolboxPanel').html(data.html);

        return {
          'sliderLabels': data.slider_labels,
          'dataInfo': data.dataInfo,
          'featureCollection': data.featureCollection,
          'all_ids': data.all_ids
        };
      })
      .then(data => {
          initializeSiekerGek(data);
      })
      // .catch(error => console.error("Error fetching data:", error));
    } else {
      handleAlerts({ success: false, message: 'Please select a user field!' });
    }
  };                              


  function startFormerWetlands() {
    console.log('start Sieker Wetlands')
    
    const userField = ToolboxProject.loadFromLocalStorage().userField;
    

    // const userField = project.userField;
    if (userField) {
      
      fetch('load_sieker_wetland_gui/' + userField + '/')
      .then(response => response.json())
      .then(data => {
        if (!data.success) {
          handleAlerts(data);
          return;
        }
          // Replace HTML content
        $('#toolboxButtons').addClass('d-none');
        $('#toolboxPanel').removeClass('d-none');
        $('#toolboxPanel').html(data.html);

        return {
          'sliderLabels': data.slider_labels,
          'dataInfo': data.dataInfo,
          'featureCollection': data.featureCollection,
          'all_ids': data.all_ids
        };
      })
      .then(data => {
          initializeSiekerWetland(data);
      })
      // .catch(error => console.error("Error fetching data:", error));
    } else {
      handleAlerts({ success: false, message: 'Please select a user field!' });
    }
  };

  // TU-Berlin
  function startTuMar() {
    const userField = ToolboxProject.loadFromLocalStorage().userField;
      if (userField) {
      
        fetch('load_tu_mar_gui/' + userField + '/')
        .then(response => response.json())
        .then(data => {
          if (!data.success) {
            handleAlerts(data);
            return
          }
          $('#toolboxButtons').addClass('d-none');
          $('#toolboxPanel').removeClass('d-none');
          $('#toolboxPanel').html(data.html);
          const tuMar = new TuMar();
          tuMar.userField = userField;
          tuMar.saveToLocalStorage();

          return {
            'sliderLabels': data.slider_labels,
            'sliderLabelsSuitability': data.slider_labels_suitability,
            // 'dataInfo': data.dataInfo,
            // 'featureCollection': data.featureCollection,
            // 'all_ids': data.all_ids
          };
        })
        .then(data => {
          initializeTuMar(data);
        })
      }
  }





  $('#startInfiltration').on('click', () => {
    console.log('startInfiltration clicked');

    startInfiltration()
  });
  $('#startInjection').on('click', () => {
    console.log('startInjection clicked');
    startTuMar();
    // startInjection()
  });
  $('#startSurfaceWaters').on('click', () => {
    console.log('startSurfaceWaters clicked');
    startSurfaceWaters();
  });
  $('#startSiekerSinks').on('click', () => {
    
    console.log('startSiekerSinks clicked');
    startSiekerSinks();
  });
  $('#startWaterDevelopment').on('click', () => {
    console.log('startGek clicked');
    startSiekerGeks();
  });
  $('#startFormerWetlands').on('click', () => {
    console.log('startFormerWetlands clicked');
    startFormerWetlands();
  });
  $('#startDrainage').on('click', () => {
    console.log('startDrainage clicked');
    // startDrainage()
  });



  getUserFieldsFromDb(featureGroup);
  if (projectRegionSwitch) {
      projectRegionSwitch.checked = true;

      // Dispatch a native 'change' event
      const event = new Event('change', { bubbles: true });
      projectRegionSwitch.dispatchEvent(event);
    }

});
