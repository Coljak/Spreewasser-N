import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, toolboxSinks, updateDropdown } from '/static/toolbox/toolbox.js';
import { 
  projectRegion, 
  baseMaps, 
  map, 
  initializeMapEventlisteners, 
  initializeDrawControl,
  createBaseLayerSwitchGroup, 
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
} from '/static/shared/map_sidebar_utils.js';



document.addEventListener("DOMContentLoaded", () => {
  // Hide the coordinate form card from plain Monica
  const project = new ToolboxProject();
  project.saveToLocalStorage();

  $('#coordinateFormCard').hide();

  // center map at geolocation
  getGeolocation()
    .then((position) => {
      map.setView([position.latitude, position.longitude], 12);
    })
    .catch((error) => {
        console.error(error.message);
        handleAlerts({ success: false, message: error.message });
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
              
              projectModalForm.reset();
              
              $('#toolboxProjectModal').modal('hide');
              project.saveToLocalStorage();
          } else {
              handleAlerts(data.message);
          }
      });
  });

// // Bounds for DEM image overlay
//   const demBounds = [[47.136744752, 15.57241882],[55.058996788, 5.564783468],];
//   const droughtBounds = [[46.89, 15.33], [55.31, 5.41],];
//   const demOverlay = L.imageOverlay(demUrl, demBounds, { opacity: 0.5 });
//   const droughtOverlay = L.imageOverlay(droughtUrl, droughtBounds, { opacity: 0.5 });
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

const demOverlay = L.imageOverlay(demUrl, demBounds, { opacity: 0.5 });
const toolboxOverlaySoil = L.imageOverlay(toolboxUrl, toolboxBounds, { opacity: 1.0 });
const toolboxOverlaySinks = L.imageOverlay(toolboxSinksUrl, sinksBounds, { opacity: 1.0 });

const toolboxOutlineInjection = new L.geoJSON(outline_injection, {
  attribution: 'Outline Injection',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name);
}
});

const toolboxOutlineSurfaceWater = new L.geoJSON(outline_surface_water, {
  attribution: 'Outline Surface Water',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name);
}
});

const toolboxOutlineInfiltration = new L.geoJSON(outline_infiltration, {
  attribution: 'Outline Infiltration',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name);
}
});

const toolboxOutlineGeste = new L.geoJSON(outline_geste, {
  attribution: 'Geste??',
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name);
}
});

  const overlayLayers = {
    // "droughtOverlay": droughtOverlay,
    "demOverlay": demOverlay,
    "projectRegion": projectRegion,
    "toolboxOverlaySoil": toolboxOverlaySoil,
    "toolboxOverlaySinks": toolboxOverlaySinks,
    "toolboxOutlineInjection": toolboxOutlineInjection,
    "toolboxOutlineSurfaceWater": toolboxOutlineSurfaceWater,
    "toolboxOutlineInfiltration": toolboxOutlineInfiltration,
    "toolboxOutlineGeste": toolboxOutlineGeste,
    "sinks": toolboxSinks,
  };



// swn-drought specific overlays
var featureGroup = new L.FeatureGroup()
map.addLayer(featureGroup);
featureGroup.bringToFront();

initializeMapEventlisteners(map, featureGroup);
initializeDrawControl(map, featureGroup);
 
initializeSidebarEventHandler({
  sidebar: document.querySelector(".sidebar-content"),
  map,
  baseMaps,
  overlayLayers,
  getUserFields: () => localStorage.getItem("userFields") ? JSON.parse(localStorage.getItem("userFields")) : {},
  getFeatureGroup: () => { return featureGroup; },
  getProject: () => ToolboxProject.loadFromLocalStorage(),
});

createNUTSSelectors({getFeatureGroup: () => { return featureGroup; }});

// sidebar Base Layers
createBaseLayerSwitchGroup(baseMaps, map);

var sinkFeaureGroup = new L.FeatureGroup()
map.addLayer(sinkFeaureGroup);

// document.getElementById('toolbox-project-save').addEventListener('click', function () {
//   const project = ToolboxProject.loadFromLocalStorage();

//   saveProject(project);
// });

function initializeSinkFilterEventHandler() {
  $('#filterSinksButton').on('click', function () {
    const project = ToolboxProject.loadFromLocalStorage();
    console.log('project', project);
    fetch('get_selected_sinks/' ,
        {
            method: 'POST',
            body: JSON.stringify(project),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            }
        }
    )
        .then(response => response.json())
        .then(data => {
            console.log('data', data);
            sinkFeaureGroup.clearLayers();
            sinkFeaureGroup.addLayer(L.geoJSON(data));
            map.fitBounds(sinkFeaureGroup.getBounds());
        })
        .catch(error => console.error("Error fetching data:", error));
  });

  $('#id_depth_sink_min').on('change', function () {
    const project = ToolboxProject.loadFromLocalStorage();
    project.infiltration.sinkDepthMin = $(this).val();
    console.log('sinkDepthMin', project.infiltration.sinkDepthMin);
    project.saveToLocalStorage();
  }
  );

  $('#id_depth_sink_max').on('change', function () {
    const project = ToolboxProject.loadFromLocalStorage();
    project.infiltration.sinkDepthMin = $(this).val();
    project.saveToLocalStorage();
  }
  );

  $('#id_area_sink_min').on('change', function () {
    const project = ToolboxProject.loadFromLocalStorage();
    project.infiltration.sinkAreaMin = $(this).val();
    project.saveToLocalStorage();
  }
  );

  $('#id_area_sink_max').on('change', function () {
    const project = ToolboxProject.loadFromLocalStorage();
    project.infiltration.sinkAreaMax = $(this).val();
    project.saveToLocalStorage();
  }
  );

  $('#id_volume_min').on('change', function () {
    const project = ToolboxProject.loadFromLocalStorage();
    project.infiltration.sinkVolumeMin = $(this).val();
    project.saveToLocalStorage();
  }
  );

  $('#id_volume_max').on('change', function () {
    const project = ToolboxProject.loadFromLocalStorage();
    project.infiltration.sinkVolumeMax = $(this).val();
    project.saveToLocalStorage();
  }
  );
};

$('#injectionGo').on('click', function () {
  const project = ToolboxProject.loadFromLocalStorage();
  const userField = project.userField;
  
  fetch('load_infiltration_gui/' + userField + '/')
      .then(response => response.json())
      .then(data => {
          
          
          // Replace HTML content
          $('#toolboxTabContent').html(data.html);

      })
      .then(() => {
        initializeSinkFilterEventHandler();
    
        requestAnimationFrame(() => {
            const project = ToolboxProject.loadFromLocalStorage();
            project.infiltration.sinkAreaMax = $('#id_area_sink_max').val();
            project.infiltration.sinkAreaMin = $('#id_area_sink_min').val();
            project.infiltration.sinkVolumeMax = $('#id_volume_max').val();
            project.infiltration.sinkVolumeMin = $('#id_volume_min').val();
            project.infiltration.sinkDepthMax = $('#id_depth_sink_max').val();
            project.infiltration.sinkDepthMin = $('#id_depth_sink_min').val();
            project.saveToLocalStorage();
        });
    })
    
      .catch(error => console.error("Error fetching data:", error));
});






getUserFieldsFromDb(featureGroup);

});