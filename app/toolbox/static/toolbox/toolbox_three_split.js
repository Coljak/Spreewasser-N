import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import {  toolboxSinksOutline, updateDropdown } from '/static/toolbox/toolbox.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { ToolboxProject } from '/static/toolbox/toolbox_project.js';
import { SiekerSink } from '/static/toolbox/sieker_sink_model.js';
import { SiekerGek } from '/static/toolbox/sieker_gek_model.js';
import { SiekerSurfaceWaters } from '/static/toolbox/sieker_surface_waters_model.js';
import { SiekerWetland } from '/static/toolbox/sieker_wetland_model.js';
import { Infiltration } from '/static/toolbox/infiltration_model.js';
import { initializeInfiltration } from '/static/toolbox/infiltration.js';
import { initializeSiekerSurfaceWaters } from '/static/toolbox/sieker_surface_waters.js';
import { initializeSiekerSink } from '/static/toolbox/sieker_sink.js';
import {initializeSiekerGek } from '/static/toolbox/sieker_gek.js';
import {initializeSiekerWetland } from '/static/toolbox/sieker_wetland.js';
import { TuMar } from '/static/toolbox/tu_mar_model.js';
import { initializeTuMar } from '/static/toolbox/tu_mar.js';
import { initializeDrainage } from '/static/toolbox/sieker_drainage.js';
import { Drainage } from '/static/toolbox/sieker_drainage_model.js';

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

// from db: ToolboxType
const TOOLBOX_TYPES = {
  '1': 'drainage',
  '2': 'infiltration',
  '3': 'injection',
  '4': 'sieker_gek',
  '5': 'sieker_surface_water',
  '6': 'sieker_sink',
  '7': 'sieker_wetland'
}; 



async function startInfiltration(project) {
  console.log('start Infiltration');
  const userField = project.userField;

  if (!userField) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return Promise.reject('No userField selected');
  }

  const response = await fetch('load_infiltration_gui/' + userField + '/');
  const data = await response.json();
  if (!data.success) {
    handleAlerts(data);
    throw new Error('Data load failed gracefully');
  }

  // const infiltration = new Infiltration({ userField: userField });
  // infiltration.saveToLocalStorage();
  // Replace HTML content
  $('#toolboxButtons').addClass('d-none');
  $('#toolboxPanel').removeClass('d-none');
  $('#toolboxPanel').html(data.html);
  userField;
  initializeInfiltration(); // initialize UI
  return true;
}



// Sieker
async function startSurfaceWaters(project) {
  console.log('startSurfaceWaters')
  const userField = project.userField;
  if (!userField) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return Promise.reject('No userField selected');
  }
  return fetch('load_surface_waters_gui/' + userField + '/')
    .then(response => response.json())
    .then(data => {
      console.log('data received', data)
      if (!data.success) {
        handleAlerts(data);
        throw new Error('Data load failed gracefully');
      }

      // const surfaceWaters = new SiekerSurfaceWaters({ userField: userField });
      // surfaceWaters.saveToLocalStorage();
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
      return true;
    })
  
};


async function startSiekerSinks(project) {
  console.log('start Infiltration')
  const userField = project.userField;

  if (!userField) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return Promise.reject('No userField selected');
  }
  return fetch('load_sieker_sink_gui/' + userField + '/')
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        handleAlerts(data);
        throw new Error('Data load failed gracefully');
      }

      // const siekerSink = SiekerSink({ userField: userField });
      // siekerSink.saveToLocalStorage();
      // Replace HTML content
      $('#toolboxButtons').addClass('d-none');
      $('#toolboxPanel').removeClass('d-none');
      $('#toolboxPanel').html(data.html);

      return userField;
    })
    .then(() => {
      initializeSiekerSink();
      return true;
    })

};


async function startSiekerGeks(project) {
  console.log('start Sieker Geks')
  
  const userField = project.userField;
  if (!userField) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return Promise.reject('No userField selected');
  }

  return fetch('load_sieker_gek_gui/' + userField + '/')
    .then(response => response.json())
    .then(data => {
      console.log('data', data);
      if (!data.success) {
        handleAlerts(data);
        throw new Error('Data load failed gracefully');
      }

      // const siekerGeks = new SiekerGek({ userField: userField });
      // siekerGeks.saveToLocalStorage();
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
        return true;
    })
 
};                              


async function startFormerWetlands(project) {
  console.log('start Sieker Wetlands')
  
  const userField = project.userField;
  if (!userField) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return Promise.reject('No userField selected');
  }

  return fetch('load_sieker_wetland_gui/' + userField + '/')
    .then(response => response.json())
    .then(data => {
      if (!data.success) {
        handleAlerts(data);
        throw new Error('Data load failed gracefully');
      }

      // const formerWetlands = new SiekerWetland({ userField: userField });
      // formerWetlands.saveToLocalStorage();
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
        return true;
    });  
};

// TU-Berlin
async function startTuMar(project) {
  const userField = project.userField;
    // if (userField) {
    
      // fetch('load_tu_mar_gui/' + userField + '/')
  return fetch('load_tu_mar_gui/')
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      handleAlerts(data);
      return
    }

    // const tuMar = new TuMar({ userField: userField});
    // tuMar.saveToLocalStorage();
    $('#toolboxButtons').addClass('d-none');
    $('#toolboxPanel').removeClass('d-none');
    $('#toolboxPanel').html(data.html);

    return {
      'sliderLabels': data.slider_labels,
      'sliderLabelsSuitability': data.slider_labels_suitability,
    };
  })
  .then(data => {
    initializeTuMar(data);
    return true;
  })
};


async function startDrainage(project) {
  console.log('start Sieker Drainage')
  
  const userField = project.userField;

  if (!userField) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return Promise.reject('No userField selected');
  }
  
  return fetch('load_sieker_drainage_gui/' + userField + '/')
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      handleAlerts(data);
      throw new Error('Data load failed gracefully');
    }
    
    // const drainage = new Drainage({ userField: userField });
    // drainage.saveToLocalStorage();}
      // Replace HTML content
    $('#toolboxButtons').addClass('d-none');
    $('#toolboxPanel').removeClass('d-none');
    $('#toolboxPanel').html(data.html);

  })
  .then(data => {
      initializeDrainage(data);
      return true;
  })

};



export function startToolbox(project) {
  // const project = ToolboxProject.loadFromLocalStorage();
  const toolboxType = project.toolboxType;
  console.log('startToolbox', toolboxType)
  switch (toolboxType) {
    case 'infiltration':
      console.log('startInfiltration saved');
      return Promise.resolve(startInfiltration(project)); // returns a promise
    case 'injection':
      console.log('startInjection saved');
      return Promise.resolve(startTuMar(project)); // should return a promise
    case 'sieker_surface_waters':
      console.log('startSurfaceWaters saved');
      return Promise.resolve(startSurfaceWaters(project));
    case 'sieker_sink':
      return Promise.resolve(startSiekerSinks(project));
    case 'sieker_gek':
      console.log('startGek clicked');
      return Promise.resolve(startSiekerGeks(project));
    case 'sieker_wetland':
      console.log('startFormerWetlands saved');
      return Promise.resolve(startFormerWetlands(project));
    case 'drainage':
      console.log('startDrainage saved');
      return Promise.resolve(startDrainage(project));
    default:
      return Promise.resolve(); // fallback in case toolboxType is unknown
  }
}



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

  $('#saveToolboxProjectButton').on('click', async () => {
  console.log('saveToolboxProjectButton clicked');
  
  const projectNameInput = $('#id_project_name');
  const projectName = projectNameInput.val().trim();

  // Validate project name
  if (!projectName) {
    projectNameInput.addClass('is-invalid');
    projectNameInput.focus();
    return;
  } else {
    projectNameInput.removeClass('is-invalid');
  }

  const project = ToolboxProject.loadFromLocalStorage();
  // const isNewProject = (project.toolboxType === 'generic');
  const pageReload = $(this).data('page-reload')
  project.name = projectName;
  project.userField = $('#userFieldSelect').val();
  project.toolboxType = $('#projectTypeSelect').val();
  project.description = $('#id_project_description').val().trim();
  project.saveToLocalStorage();
  $('#toolboxProjectModal').modal('hide');
  try {
    const data = await project.saveToDB(); 
    console.log('data', data);

    if (data.success) {

      handleAlerts({ success: data.success, message: data.message });
      // console.log('Is generic project?', isNewProject);
      if (pageReload) { startToolbox(project); }
      
      // Trigger correct start function
      // if (isNewProject) {
        
      // }
    } else {
      handleAlerts(data.message);
    }

  } catch (err) {
    console.error('Failed to save project:', err);
    handleAlerts({ success: false, message: 'Error saving project.' });
  }
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






  $('#startInfiltration').on('click', () => {
    console.log('startInfiltration clicked');
    const project = ToolboxProject.loadFromLocalStorage();
    startInfiltration(project)
  });
  $('#startInjection').on('click', () => {
    console.log('startInjection clicked');
    const project = ToolboxProject.loadFromLocalStorage();
    startTuMar(project);
    // startInjection()
  });
  $('#startSurfaceWaters').on('click', () => {
    console.log('startSurfaceWaters clicked');
    const project = ToolboxProject.loadFromLocalStorage();
    startSurfaceWaters(project);
  });
  $('#startSiekerSinks').on('click', () => {
    const project = ToolboxProject.loadFromLocalStorage();
    console.log('startSiekerSinks clicked');
    startSiekerSinks(project);
  });
  $('#startWaterDevelopment').on('click', () => {
    console.log('startGek clicked');
    const project = ToolboxProject.loadFromLocalStorage();
    startSiekerGeks(project);
  });
  $('#startFormerWetlands').on('click', () => {
    console.log('startFormerWetlands clicked');
    const project = ToolboxProject.loadFromLocalStorage();
    startFormerWetlands(project);
  });
  $('#startDrainage').on('click', () => {
    console.log('startDrainage clicked');
    const project = ToolboxProject.loadFromLocalStorage();
   startDrainage(project)
  });



  getUserFieldsFromDb(featureGroup);
  if (projectRegionSwitch) {
      projectRegionSwitch.checked = true;

      // Dispatch a native 'change' event
      const event = new Event('change', { bubbles: true });
      projectRegionSwitch.dispatchEvent(event);
    }

});
