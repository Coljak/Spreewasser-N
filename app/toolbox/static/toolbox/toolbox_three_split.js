import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, toolboxSinks, updateDropdown } from '/static/toolbox/toolbox.js';
// import {initializeSliders} from '/static/toolbox/custom_slider.js';
import {initializeSliders} from '/static/toolbox/double_slider.js';
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
import { sinkFeatureGroup, enlargedSinkFeatureGroup, lakesFeatureGroup, getWaterBodies, streamsFeatureGroup, inletConnectionsFeatureGroup, createSinkTableSettings, getSinks, addToInletTable, getInlets, updateInletInfoCard, toggleConnection, startInfiltration } from '/static/toolbox/infiltration.js';


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



  const overlayLayers = {
    "demOverlay": demOverlay,
    "projectRegion": projectRegion,
    "toolboxOverlaySoil": toolboxOverlaySoil,
    "toolboxOverlaySinks": toolboxOverlaySinks,
    "toolboxOutlineInjection": toolboxOutlineInjection,
    "toolboxOutlineSurfaceWater": toolboxOutlineSurfaceWater,
    "toolboxOutlineInfiltration": toolboxOutlineInfiltration,
    "sinks": toolboxSinks,
  };



// toolbox specific overlays
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


map.addLayer(sinkFeatureGroup);
map.addLayer(enlargedSinkFeatureGroup);
map.addLayer(lakesFeatureGroup);
map.addLayer(streamsFeatureGroup);
map.addLayer(inletConnectionsFeatureGroup);



// document.getElementById('toolbox-project-save').addEventListener('click', function () {
//   const project = ToolboxProject.loadFromLocalStorage();

//   saveProject(project);
// });

// TODO I tttttttttthink      this is not working!
document.getElementById('map').addEventListener('click', function (event) {
  if (event.target.classList.contains('select-sink')) {
    const sinkId = event.target.getAttribute('sinkId');
    const sinkType = event.target.getAttribute('data-type');
    console.log('sinkId', sinkId);
    console.log('sinkType', sinkType);

    const checkbox = document.querySelector(`.sink-select-checkbox[data-type="${sinkType}"][data-id="${sinkId}"]`);
    checkbox.checked = !checkbox.checked;
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
  }
});




$('#toolboxPanel').on('change',  function (event) {
  const $target = $(event.target);
  const project = ToolboxProject.loadFromLocalStorage();
  // console.log('change event', $target);
  if ($target.hasClass('double-slider')) {
    const inputName = $target.attr('name');
    const minName = inputName + '_min';
    const maxName = inputName + '_max'; 
    const inputVals = $target.val().split(',');
    project.infiltration[minName] = inputVals[0];
    project.infiltration[maxName] = inputVals[1];
    project.saveToLocalStorage();
  } else if ($target.hasClass('single-slider')) {   
    const inputName = $target.attr('name'); 
    const inputVal = $target.val();
    project.infiltration[inputName] = inputVal;
    project.saveToLocalStorage();
  }else if ($target.hasClass('form-check-input')) {
    // checkboxes 
    const inputId = $target.attr('id');
    const inputName = $target.attr('name');
    const inputPrefix = $target.attr('prefix');
    const inputValue = $target.attr('value');
    const inputChecked = $target.is(':checked');

    const key = `${inputPrefix}_${inputName}`;

    const index = project.infiltration[key].indexOf(inputValue);

    if (index > -1) {
      // Value exists — remove it
      project.infiltration[key] = project.infiltration[key].filter(
        (v) => v !== inputValue
      );
      console.log('Checkbox unchecked:', inputId, '=', inputValue);
    } else {
      // Value does not exist — add it
      project.infiltration[key].push(inputValue);
      console.log('Checkbox checked:', inputId, '=', inputValue);
    }
    project.saveToLocalStorage();

  } else if ($target.hasClass('sink-select-all-checkbox')) {
    
    const allSelected = $target.is(':checked');
    const sinkType = $target.data('type');
    console.log('sinkType', sinkType);
    
    
    const key = sinkType === 'sink' ? 'selected_sinks' : 'selected_enlarged_sinks';
    if (!allSelected) {
      project.infiltration[key] = [];
    }
    $(`.sink-select-checkbox[data-type="${sinkType}"]`).each(function(){
      const $checkbox = $(this);
      $checkbox.prop('checked', allSelected);
      const sinkId = $checkbox.data('id');
      if (allSelected) {
        console.log("Selected sink:", sinkId);
        project.infiltration[key].push(sinkId);
      } 
    })
    project.saveToLocalStorage();
  } else if ($target.hasClass('sink-select-checkbox')) {
    const sinkType = $target.data('type');
    const key = sinkType === 'sink' ? 'selected_sinks' : 'selected_enlarged_sinks';
    console.log('sinkType', sinkType);
      if ($target.is(':checked')) {
        console.log("Selected sink:", $target.data('id'));
        const project= ToolboxProject.loadFromLocalStorage();
        project.infiltration[key].push($target.data('id'));
        project.saveToLocalStorage();

      } else {
        const sinkId = $target.data('id');
        console.log("Selected sink:", sinkId);
        const project= ToolboxProject.loadFromLocalStorage();
        const index = project.infiltration[key].indexOf(sinkId);
        if (index > -1) {
          project.infiltration[key].splice(index, 1);
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
  } else if ($target.attr('id') === 'btnFilterSinks') {
    getSinks('sink', sinkFeatureGroup);
  
  } else if ($target.attr('id') === 'btnFilterEnlargedSinks') {
    getSinks('enlarged_sink', enlargedSinkFeatureGroup);
  
  } else if ($target.attr('id') === 'btnFilterStreams') {
    getWaterBodies('streams', streamsFeatureGroup);
  
  } else if ($target.attr('id') === 'btnFilterLakes') {
    getWaterBodies('lakes', lakesFeatureGroup);
  
  // } else if ($target.hasClass('evaluate-selected-sinks')) {
  //   console.log('ClassList contains  evaluate-selected-sinks');
  //   const project = ToolboxProject.loadFromLocalStorage();
  //   calculateIndexForSelection(project)
  } else if ($target.attr('id') === 'btnGetInlets') {
      getInlets(); 
  } else if ($target.attr('id') === 'navInfiltrationSinks') {
      map.addLayer(sinkFeatureGroup);
  } else if ($target.attr('id') === 'navInfiltrationEnlargedSinks') {
      map.addLayer(enlargedSinkFeatureGroup);
  } else if ($target.attr('id') === 'navInfiltrationResult') {
      map.removeLayer(sinkFeatureGroup);
      map.removeLayer(enlargedSinkFeatureGroup);
  } else if ($target.attr('id') === 'toggleSinks') {
    if (map.hasLayer(sinkFeatureGroup)) {
      map.removeLayer(sinkFeatureGroup);
      $target.text('einblenden');
    } else {
        map.addLayer(sinkFeatureGroup);
        $target.text('ausblenden');
    }
  } else if ($target.attr('id') === 'toggleEnlargedSinks') {
    if (map.hasLayer(enlargedSinkFeatureGroup)) {
      map.removeLayer(enlargedSinkFeatureGroup);
      $target.text('einblenden');
    } else {
        map.addLayer(enlargedSinkFeatureGroup);
        $target.text('ausblenden');
    }
  } else if ($target.attr('id') === 'toggleStreams') {
    if (map.hasLayer(streamsFeatureGroup)) {
      map.removeLayer(streamsFeatureGroup);
      $target.text('einblenden');
    } else {
        map.addLayer(streamsFeatureGroup);
        $target.text('ausblenden');
    }
  } else if ($target.attr('id') === 'toggleLakes') {
    if (map.hasLayer(lakesFeatureGroup)) {
      map.removeLayer(lakesFeatureGroup);
      $target.text('einblenden');
    } else {
        map.addLayer(lakesFeatureGroup);
        $target.text('ausblenden');
    }
  }
}); 





$('#startInfiltration').on('click', () => {
  console.log('startInfiltration clicked');
  startInfiltration()
});
$('#startInjection').on('click', () => {
  console.log('startInjection clicked');
  // startInjection()
});
$('#startSurfaceWaters').on('click', () => {
  console.log('startSurfaceWaters clicked');
  // startSurfaceWaters()
});
$('#startSiekerSinks').on('click', () => {
  console.log('startSiekerSinks clicked');
  // startSiekerSinks()
});
$('#startWaterDevelopment').on('click', () => {
  console.log('startWaterDevelopment clicked');
  // startWaterDevelopment()
});
$('#startFormerWetlands').on('click', () => {
  console.log('startFormerWetlands clicked');
  // startFormerWetlands()
});
$('#startDrainage').on('click', () => {
  console.log('startDrainage clicked');
  // startDrainage()
});



getUserFieldsFromDb(featureGroup);

});
