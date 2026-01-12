import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import {  toolboxSinksOutline, updateDropdown, loadProjectFromDb, setProjectInfoHeader } from '/static/toolbox/toolbox.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
import { ToolboxProject } from '/static/toolbox/toolbox_project.js';
import { SiekerSink } from '/static/toolbox/sieker_sink_model.js';
import { SiekerGek } from '/static/toolbox/sieker_gek_model.js';
import { SiekerSurfaceWaters } from '/static/toolbox/sieker_surface_waters_model.js';
import { SiekerWetland } from '/static/toolbox/sieker_wetland_model.js';
import { Infiltration } from '/static/toolbox/infiltration_model.js';
import { Injection } from '/static/toolbox/injection_model.js';
import { initializeInfiltration } from '/static/toolbox/infiltration.js';
import { initializeSiekerSurfaceWaters } from '/static/toolbox/sieker_surface_waters.js';
import { initializeSiekerSink } from '/static/toolbox/sieker_sink.js';
import {initializeSiekerGek } from '/static/toolbox/sieker_gek.js';
import {initializeSiekerWetland } from '/static/toolbox/sieker_wetland.js';
import { initializeInjection } from '/static/toolbox/injection.js';
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
import { saveNewProjectModalEvents } from '/static/toolbox/toolbox_modals.js';

// for info elements with help text
function getInfoText(el) {
  setTimeout(() => {
    console.log('el', el)
    el.getBoundingClientRect()
      // Destroy any existing popover on other elements
      $('.bi-info-circle').each(function () {
          if (this !== el) {
              const existing = bootstrap.Popover.getInstance(this);
              if (existing) existing.dispose();
          }
      });

      // Get instance if it already exists
      let popover = bootstrap.Popover.getInstance(el);
      console.log('popover 1', popover)
      if (popover) {
          // Toggle off if already open
          popover.dispose();
          return;
      }
      console.log('el.getAttribute("data-help")', el.getAttribute("data-help"))
      // Create a new popover
      popover = new bootstrap.Popover(el, {
          content: el.getAttribute("data-help"),
          trigger: "manual",       // popover will open manually
          placement: "right",
          html: true,
      });
      console.log('popover 2', popover)

      popover.show();

      // Close all popovers when clicking outside
      document.addEventListener('click', function handler(e) {
          if (!el.contains(e.target)) {
            if (popover  && popover._element) {
              popover.dispose();
            }

              document.removeEventListener('click', handler);
          }
      });
    }, 10);
}


// from db: ToolboxType
const TOOLBOX_TYPES = {
  '1': 'drainage',
  '2': 'infiltration',
  '3': 'injection',
  '4': 'sieker_gek',
  '5': 'sieker_surface_water',
  '6': 'sieker_sink',
  '7': 'wetland'
}; 


function addToolboxProject(userFieldId){
  fetch('/toolbox/load-toolbox-project-modal/', {
  method: 'POST',
  credentials: 'same-origin',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCSRFToken(),
  },
  body: JSON.stringify({ userFieldId: userFieldId, page_reload: 'true', })

})
.then(r => r.text())
.then(html => {
  const container = document.getElementById("modal-container");
  container.innerHTML = html;

  const modalEl = document.getElementById("toolboxProjectModal");
  saveNewProjectModalEvents();
  const modal = new bootstrap.Modal(modalEl);
  modal.show();
});
};

async function startInfiltration() {
  
  const project = Infiltration.loadFromLocalStorage();
  console.log('start Infiltration', project);
  if (!project.userField || project.userField === undefined) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return Promise.reject('No userField selected');
  }
    
  let data = null;
  try {
    const response = await fetch('load_infiltration_gui/' + project.userField + '/');
    data = await response.json();
    if (!data.success) {
      handleAlerts(data)
      return null
    }
  } catch (error) {
    
    return null;
  }
  
  // Replace HTML content
  $('#toolboxButtons').addClass('d-none');
  $('#toolboxPanel').removeClass('d-none');
  $('#toolboxPanel').html(data.html);
  if (!project.id) {
    const infiltration = new Infiltration(data.default_project);
    infiltration.saveToLocalStorage();
  }

  initializeInfiltration(); // initialize UI
  return true;
}



// Sieker

async function startSurfaceWaters() {
  console.log("startSurfaceWaters");

  // Load stored project
  const project = SiekerSurfaceWaters.loadFromLocalStorage();

  // Early validation
  if (!project.userField) {
    handleAlerts({
      success: false,
      message: "Bitte wählen Sie ein Suchgebiet aus!"
    });
    return null; // fail silent
  }

  let rawText;

  // ----- Fetch + parse JSON safely -----
  try {
    const response = await fetch(
      `load_surface_waters_gui/${project.userField}/`
    );

    rawText = await response.text();
  } catch (e) {
    handleAlerts({
      success: false,
      message: "Bitte verkleinern Sie das Suchgebiet - die Datenmenge ist zu groß und kann nicht vollständig geladen werden."
    });
    return null;
  }

  let data;

  try {
    data = JSON.parse(rawText);
  } catch (e) {
    handleAlerts({
      success: false,
      message:
        "Ihre Suche liefert zu viele Ergebnisse. Bitte verkleinern Sie das Suchgebiet!"
    });
    return null; // stop here!
  }

  // ----- Stop early if backend returned an error -----
  if (!data.success) {
    handleAlerts(data);
    return null; // STOP — nothing more runs
  }

  // ----- Success: update the UI -----
  $("#toolboxButtons").addClass("d-none");
  $("#toolboxPanel").removeClass("d-none").html(data.html);

  // Create new project if needed
  if (!project.id) {
    const surfaceWaters = new SiekerSurfaceWaters(data.default_project);
    surfaceWaters.saveToLocalStorage();
  }

  // Initialize
  initializeSiekerSurfaceWaters();

  return true;
}


async function startSiekerSinks() {
  console.log("start Infiltration");

  const project = SiekerSink.loadFromLocalStorage();

  // Early validation
  if (!project.userField) {
    handleAlerts({
      success: false,
      message: "Bitte wählen Sie ein Suchgebiet aus!"
    });
    return null; // silent fail
  }

  let data;

  // ---- Load JSON safely ----
  try {
    const response = await fetch(
      `load_sieker_sink_gui/${project.userField}/`
    );
    data = await response.json();
  } catch (e) {
    handleAlerts({
      success: false,
      message: "Fehler beim Laden der Senkendaten."
    });
    return null;
  }

  // ---- Backend returned an application error ----
  if (!data.success) {
    handleAlerts(data);
    return null; // stop immediately
  }

  // ---- Success: update UI ----
  $("#toolboxButtons").addClass("d-none");
  $("#toolboxPanel").removeClass("d-none").html(data.html);

  // Create project if needed
  if (!project.id) {
    const siekerSink = new SiekerSink(data.default_project);
    siekerSink.saveToLocalStorage();
  }

  // Initialize GUI
  initializeSiekerSink();

  return true;
}



async function startSiekerGeks() {
  console.log('start Sieker Geks')
  const project = SiekerGek.loadFromLocalStorage();
  // const userField = project.userField;
  if (!project.userField || project.userField === undefined) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return Promise.reject('No userField selected');
  }

  let data;

    try {
    const response = await fetch(
      `load_sieker_gek_gui/${project.userField}/`
    );
    data = await response.json();
  } catch (e) {
    handleAlerts({
      success: false,
      message: "Fehler beim Laden der Senkendaten."
    });
    return null;
  }

  // ---- Backend returned an application error ----
  if (!data.success) {
    handleAlerts(data);
    return null; // stop immediately
  }

  // Replace HTML content
  $('#toolboxButtons').addClass('d-none');
  $('#toolboxPanel').removeClass('d-none');
  $('#toolboxPanel').html(data.html);
  if (!project.id) {
    const siekerGeks = new SiekerGek(data.default_project);
    siekerGeks.saveToLocalStorage();
  }
  initializeSiekerGek({
    'sliderLabels': data.slider_labels,
    'all_ids': data.all_ids,
  });
  return true;
};                              


async function startFormerWetlands() {
  console.log('start Sieker Wetlands')

  const project = SiekerWetland.loadFromLocalStorage();
  // const userField = project.userField;
  if (!project.userField || project.userField === undefined) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return Promise.reject('No userField selected');
  }
  let data;
  try {
    const response = await fetch('load_sieker_wetland_gui/' + project.userField + '/');
    data = await response.json();
  } catch (e) {
    handleAlerts({
      success: false,
      message: "Fehler beim Laden der Senkendaten."
    });
    return null;
  }
  if (!data.success) {
    handleAlerts(data);
    return null;
  }
      // Replace HTML content
  $('#toolboxButtons').addClass('d-none');
  $('#toolboxPanel').removeClass('d-none');
  $('#toolboxPanel').html(data.html);

  if (!project.id) {
    const formerWetlands = new SiekerWetland(data.default_project);
    formerWetlands.saveToLocalStorage();
  }

  initializeSiekerWetland({
    'sliderLabels': data.slider_labels,
    'dataInfo': data.dataInfo,
    'featureCollection': data.featureCollection,
    'all_ids': data.all_ids
  });
  return true; 
};

// TU-Berlin
async function startInjection() {
  const project = Injection.loadFromLocalStorage();
  return fetch('load_injection_gui/')
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      handleAlerts(data);
      return
    }

    // const injection = new Injection({ userField: userField});
    // injection.saveToLocalStorage();
    $('#toolboxButtons').addClass('d-none');
    $('#toolboxPanel').removeClass('d-none');
    $('#toolboxPanel').html(data.html);
    if (!project.id) {
      const defaultProject = data.default_project;
      const injection = new Injection(defaultProject);
      injection.saveToLocalStorage();
    }

    return {
      'sliderLabels': data.slider_labels,
      'sliderLabelsSuitability': data.slider_labels_suitability,
    };
  })
  .then(data => {
    initializeInjection(data);
    return true;
  })
};


async function startDrainage() {
  console.log('start Sieker Drainage')
  
  //const userField = project.userField;
  const project = Drainage.loadFromLocalStorage();
  if (!project.userField || project.userField === undefined) {
    handleAlerts({'success': false, 'message': 'Bitte wählen Sie ein Suchgebiet aus!'});
    return null;
  }
  
  let data;
  try {
    const response = await fetch('load_sieker_drainage_gui/' + project.userField + '/');
    data = await response.json();
  } catch (e) {
    handleAlerts({
      success: false,
      message: "Fehler beim Laden der Senkendaten."
    });
    return null;
  }

  if (!data.success) {
    handleAlerts(data);
    return null;
  }
    
      // Replace HTML content
  $('#toolboxButtons').addClass('d-none');
  $('#toolboxPanel').removeClass('d-none');
  $('#toolboxPanel').html(data.html);
  if (!project.id) {
    const drainage = new Drainage(data.default_project);
    drainage.saveToLocalStorage();
  }
   
  $('input[detail]').each(function() {
      const detail = $(this).attr('detail');         // get the key
      const color = data.colors[detail];                  // look up color
      if (color) {
          const id = $(this).attr('id');            // get input id
          $(`label[for="${id}"]`).css('color', color); // set label color
      }
  });
  initializeDrainage();
  return true;

};



export function startToolbox(project) {
  // const project = ToolboxProject.loadFromLocalStorage();
  const toolboxType = project.toolboxType;
  console.log('startToolbox', toolboxType)
  switch (toolboxType) {
    case 'infiltration':
      console.log('startToolbox infiltration');
      return Promise.resolve(startInfiltration()); // returns a promise
    case 'injection':
      console.log('startToolbox injection');
      return Promise.resolve(startInjection()); // should return a promise
    case 'sieker_surface_water':
      console.log('startToolbox sieker_surface_water');
      return Promise.resolve(startSurfaceWaters());
    case 'sieker_sink':
      console.log('startToolbox sieker_sink');
      return Promise.resolve(startSiekerSinks());
    case 'sieker_gek':
      console.log('startToolbox sieker_gek');
      return Promise.resolve(startSiekerGeks());
    case 'wetland':
      console.log('startToolbox wetland');
      return Promise.resolve(startFormerWetlands());
    case 'drainage':
      console.log('startToolbox drainage');
      return Promise.resolve(startDrainage());
    default:
      return Promise.resolve(); // fallback in case toolboxType is unknown
  }
}

$(document).on('click', 'i.bi.bi-info-circle', function() {
    console.log('icon clicked');
    getInfoText(this);
});

document.addEventListener("DOMContentLoaded", () => {
 

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



  // $('#toolboxSidebar').on('click', async function(event){
  //   if ($(event.target).hasClass('save-new-project')) {
  //     const projectNameInput = $('#id_project_name');
  //   const projectName = projectNameInput.val().trim();

  //   // Validate project name
  //   if (!projectName) {
  //     projectNameInput.addClass('is-invalid');
  //     projectNameInput.focus();
  //     return;
  //   } else {
  //     projectNameInput.removeClass('is-invalid');
  //   }

  //   const project = ToolboxProject.loadFromLocalStorage();
  //   // const isNewProject = (project.toolboxType === 'generic');
  //   const pageReload = $(this).data('page-reload')
  //   project.name = projectName;
  //   project.userField = $('#userFieldSelect').val();
  //   project.toolboxType = $('#projectTypeSelect').val();
  //   project.description = $('#id_project_description').val().trim();
  //   project.saveToLocalStorage();
  //   try {
  //     setProjectInfoHeader(project);
  //   } catch {;}
    

  //   $('#toolboxProjectModal').modal('hide');
  //   try {
  //     const data = await project.saveToDB(); 
  //     console.log('data', data);

  //     if (data.success) {

  //       handleAlerts({ success: data.success, message: data.message });
  //       if (pageReload) {
  //          startToolbox(project); 
  //       } else {
  //         $('#id_toolbox_project').prepend(
  //           $('<option>', { value: project.id, text: project.name })
  //         );
  //         $('#id_toolbox_project').val(project.id);
  //       }

  //       // }
  //     } else {
        
  //       handleAlerts(data.message);
  //     }

  //   } catch (err) {
  //     console.error('Failed to save project:', err);
  //     handleAlerts({ success: false, message: 'Error saving project.' });
  //   }
  //   }
  // });

  // $('.save-new-project').on('click', async function () {
  //   console.log('saveToolboxProjectButton clicked');
    
    
  // });



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
    loadProjectFromDb: (projectId) => loadProjectFromDb(projectId),
    startApplication: (project) => startToolbox(project),
    addProject: (userFieldId) => addToolboxProject(userFieldId),
  });

  createNUTSSelectors({getFeatureGroup: () => { return featureGroup; }});






  $('#startInfiltration').on('click', () => {
    console.log('startInfiltration clicked');
    // const userField = ToolboxProject.loadFromLocalStorage().userField;
    // const project = new Infiltration({ userField: userField });
    // project.saveToLocalStorage();
    startInfiltration();
  });
  $('#startInjection').on('click', () => {
    console.log('startInjection clicked');
    // const userField = ToolboxProject.loadFromLocalStorage().userField;
    // const project = new Injection({ userField: userField });
    // project.saveToLocalStorage();
    startInjection();
    // startInjection()
  });
  $('#startSurfaceWaters').on('click', () => {
    console.log('startSurfaceWaters clicked');
    // const userField = ToolboxProject.loadFromLocalStorage().userField;
    // const project = new SiekerSurfaceWaters({ userField: userField });
    // project.saveToLocalStorage();
    startSurfaceWaters();
  });
  $('#startSiekerSinks').on('click', () => {
    // const userField = ToolboxProject.loadFromLocalStorage().userField;
    // const project = new SiekerSink({ userField: userField });
    // project.saveToLocalStorage();
    startSiekerSinks();
  });
  $('#startWaterDevelopment').on('click', () => {
    console.log('startGek clicked');
    // const userField = ToolboxProject.loadFromLocalStorage().userField;
    // const project = new SiekerGek({ userField: userField });
    // project.saveToLocalStorage();
    startSiekerGeks();
  });
  $('#startFormerWetlands').on('click', () => {
    console.log('startFormerWetlands clicked');
    // const userField = ToolboxProject.loadFromLocalStorage().userField;
    // const project = new SiekerWetland({ userField: userField });
    // project.saveToLocalStorage();
    startFormerWetlands();
  });
  $('#startDrainage').on('click', () => {
    console.log('startDrainage clicked');
    // const userField = ToolboxProject.loadFromLocalStorage().userField;
    // const project = new Drainage({ userField: userField });
    // project.saveToLocalStorage();
   startDrainage()
  });



  getUserFieldsFromDb(featureGroup);
  if (projectRegionSwitch) {
      projectRegionSwitch.checked = true;

      // Dispatch a native 'change' event
      const event = new Event('change', { bubbles: true });
      projectRegionSwitch.dispatchEvent(event);
    }

});
