import { getGeolocation, handleAlerts, getCSRFToken, saveProject, observeDropdown,  setLanguage, populateDropdown } from '/static/shared/utils.js';
import {Infiltration} from '/static/toolbox/infiltration_model.js';
import {SiekerGek} from '/static/toolbox/sieker_gek_model.js';
import {SiekerSink} from '/static/toolbox/sieker_sink_model.js';
import {SiekerSurfaceWaters} from '/static/toolbox/sieker_surface_waters_model.js';

function updateButtonState(project) {
    console.log('updateButtonState', project);
    if (document.getElementById("divInfiltration")){
        
        const hasSink = project.infiltration.selected_sinks.length > 0;
        const hasEnlargedSink = project.infiltration.selected_enlarged_sinks.length > 0;
        const hasStream = project.infiltration.selected_streams.length > 0;
        const hasLake = project.infiltration.selected_lakes.length > 0;
        

        // Adjust to your actual button ID
        if ((hasSink || hasEnlargedSink) && (hasLake || hasStream)) {
            document.getElementById("btnGetInlets").classList.remove('disabled');
            console.log('!(hasSink && hasWaterbody)')
        } else {
            document.getElementById("btnGetInlets").classList.add('disabled');
            console.log('(hasSink && hasWaterbody)')
        };
    }
};



export const updateDropdown = (parameterType, newId) => {
    
    // the absolute path is needed because most options are exclusively from /monica
    let baseUrl = 'get_options/';

    console.log('updateDropdown baseUrl', baseUrl);
    var select = document.querySelector('.form-select.' + parameterType); 
    fetch(baseUrl + parameterType + '/')
        .then(response => response.json())
        .then(data => {
            console.log('updateDropdown', data);
            populateDropdown(data, select);
        })
        .then(() => {
            if (newId != '') {
                select.value = newId
            }
            $(select).trigger('change');
        })
        .catch(error => console.log('Error in updateDropdown', error));
};

// newly filtered items or pagination requires this to be executed in the DataTable
export function tableCheckSelectedItems(project, dataType) {
    console.log('tableCheckSelectedItems')
  if (project[`selected_${dataType}s`] !== undefined && project[`selected_${dataType}s`].length > 0) {
    project[`selected_${dataType}s`].forEach(itemId => {
      const checked = project[`all_${dataType}_ids`].includes(itemId) ? true : false;
      const checkbox = document.querySelector(`.table-select-checkbox[data-type="${dataType}"][data-id="${itemId}"]`);
      if (checkbox && checked) {
        checkbox.checked = checked;
        // checkbox.dispatchEvent(new Event('change', { bubbles: true }));
      }
    })
  }
  
}


export async function toolboxSinks() {
    // gets the sinks as an image
    // TODO: obsolte??static 'tool
  try {
      const response = await fetch('toolbox_sinks/');
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const geojsonData = await response.json();

      // Create a Leaflet GeoJSON layer
      const toolboxSinks = L.geoJSON(geojsonData, {
          attribution: 'Toolbox Sinks',
          onEachFeature: function (feature, layer) {
              layer.bindTooltip(feature.properties.name);
          }
      });

      return toolboxSinks; // Return the Leaflet layer
  } catch (error) {
      console.error("Error loading project region:", error);
      return null;
  }
};

    // eventlistener for the filters
export function addChangeEventListener(projectType) {
    const ProjectClass = projectType;
    console.log(projectType)
    $('#toolboxPanel').on('change', function (event) {
        const $target = $(event.target);
        const project = ProjectClass.loadFromLocalStorage();
        // console.log('change event', $target);
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
            const inputName = $target.attr('name');
            const inputPrefix = $target.attr('prefix');
            const inputValue = $target.attr('value');
            const inputChecked = $target.is(':checked');

            const key = `${inputPrefix}_${inputName}`;
            console.log('key', key)
            console.log('project', project)
            const index = project[key].indexOf(inputValue);

            if (index > -1) {
                // Value exists — remove it
                project[key] = project[key].filter(
                (v) => v !== inputValue
                );
                console.log('Checkbox unchecked:', inputId, '=', inputValue);
            } else {
                // Value does not exist — add it; Dev purposes
                project[key].push(inputValue);
                console.log('Checkbox checked:', inputId, '=', inputValue);
            }
            project.saveToLocalStorage();

        } else if ($target.hasClass('table-select-all')) {
        
            const allSelected = $target.is(':checked');
            const dataType = $target.data('type');

            const key = `selected_${dataType}s`;
            console.log('key', key)
            if (!allSelected) {
                project[key] = [];
            } else {
                project[key] = project[`all_${dataType}_ids`]
            }
            $(`.table-select-checkbox[data-type="${dataType}"]`).each(function(){
                const $checkbox = $(this);
                $checkbox.prop('checked', allSelected);
                const selectedId = $checkbox.data('id');
                if (allSelected) {
                console.log("Selected Id:", selectedId);
                
                project[key].push(selectedId);
                } 
            })
            project.saveToLocalStorage();
        } else if ($target.hasClass('table-select-checkbox')) {
            const dataType = $target.data('type');
            
            const key = `selected_${dataType}s`;

                if ($target.is(':checked')) {
                console.log("Selected Id:", $target.data('id'));
                console.log("key:", key);
                console.log('project[key]', project[key])
                console.log(project)
                project[key].push($target.data('id'));
                project.saveToLocalStorage();

                } else {
                const dataId = $target.data('id');
                console.log("Selected Id:", dataId);
                
                const index = project[key].indexOf(dataId);
                if (index > -1) {
                    project[key].splice(index, 1);
                }
                project.saveToLocalStorage();
                }

                // uncheck the select-all checkbox:
                $(`.table-select-all[data-type="${dataType}"]`).prop("checked", false);

            // You can trigger your map sink selection logic here
        };
        });
    };

export function addClickEventListenerToTable(projectType) {
    const ProjectClass = projectType;
    $('#toolboxPanel').on('click',function (event) {
        const $target = $(event.target);
        const project = ProjectClass.loadFromLocalStorage();
        if ($target.hasClass('paginate_button')) {
            console.log('Paginate')
            const dataType = $('.table-select-all').data('type');
            tableCheckSelectedItems(project, dataType)
        }
    });
}