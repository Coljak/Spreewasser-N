import { getGeolocation, handleAlerts, saveProject, observeDropdown,  getCSRFToken, setLanguage, addToDropdown } from '/static/shared/utils.js';
import { ToolboxProject, toolboxSinks, updateDropdown } from '/static/toolbox/toolbox.js';
import {initializeSliders} from '/static/toolbox/custom_slider.js';
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
      initializeSliders();
      $('input[type="checkbox"][name="land_use"]').prop('checked', true);
      $('input[type="checkbox"][name="land_use"]').trigger('change');

      
      const forms = document.querySelectorAll('.weighting-form')
      forms.forEach(form => {
        
        const sliderList = form.querySelectorAll('input.single-slider');
        const length = sliderList.length;
          
        const sliderObj = {};
        let index = 0;
        sliderList.forEach(slider => {
          sliderObj[index] = {
            'val': slider.value,
            'name': slider.name,
            'slider': slider
          };
          index++;
        });
        
        sliderList.forEach(slider => {
          slider.addEventListener('change', function (e) {
            const project = ToolboxProject.loadFromLocalStorage();
            const changedSlider = e.target;
   
            const startIndex = Object.keys(sliderObj).find(
              key => sliderObj[key].slider === changedSlider
            );
            // let changedSlider = sliderObj[startIndex].slider;
            const newVal = parseInt(changedSlider.value);
            let diff = newVal - sliderObj[startIndex].val;
            
            sliderObj[startIndex].val = newVal;
            project.infiltration[changedSlider.name] = sliderObj[startIndex].val;
            console.log("Slider ", startIndex, "new value", newVal, "diff", diff);

            let remainingDiff = diff;
            
            let nextIndex = (parseInt(startIndex) + 1) % length;
            while (remainingDiff !== 0) {

            let sObj = sliderObj[nextIndex];
            let slider = sObj.slider;
            let currentVal = parseInt(slider.value);
            let newVal = currentVal - remainingDiff;
        
            // Clamp between 0 and 100
            if (newVal < 0) {
              remainingDiff = - newVal; 
              newVal = 0;
            } else if (newVal > 100) {
              remainingDiff = newVal - 100;
              newVal = 100;
            } else {
              remainingDiff = 0;
            }
            sObj.val = newVal;
            project.infiltration[sObj.name] = newVal;
            slider.value = newVal;
            slider.dispatchEvent(new Event('input', { bubbles: true }));
        
            nextIndex = (nextIndex + 1) % length;

            if (nextIndex == startIndex) break;
          }
          project.saveToLocalStorage();
          });
        });

        const resetBtn = form.querySelector('input.reset-all');
        resetBtn.addEventListener('click', function (e) {
          let project = ToolboxProject.loadFromLocalStorage();
          // const sliderList = form.querySelectorAll('input.single-slider');
          Object.keys(sliderObj).forEach(idx => {
            sliderObj[idx].slider.value = parseFloat(sliderObj[idx].slider.dataset.defaultValue);
            sliderObj[idx].slider.dispatchEvent(new Event('input'));
            sliderObj[idx].val = parseFloat(sliderObj[idx].slider.dataset.defaultValue);
          });
          project.saveToLocalStorage();
        });

        
        });
    })
    // .catch(error => console.error("Error fetching data:", error));
  } else {
    handleAlerts({ success: false, message: 'Please select a user field!' });
  }
};

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
