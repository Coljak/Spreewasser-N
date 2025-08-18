import { getGeolocation, handleAlerts, getCSRFToken, saveProject, observeDropdown,  setLanguage, populateDropdown } from '/static/shared/utils.js';
import {Infiltration} from '/static/toolbox/infiltration_model.js';

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



export class SiekerSink {
    constructor (siekerSink = {}) {
        this.id = siekerSink.id ?? null;
        this.userField = siekerSink.userField ?? null;
        this.sieker_sink_volume_max = siekerSink.sieker_sink_volume_max ?? null;
        this.sieker_sink_volume_min = siekerSink.sieker_sink_volume_min ?? null;
        this.sieker_sink_sink_depth_min = siekerSink.sieker_sink_sink_depth_min ?? null;
        this.sieker_sink_sink_depth_max = siekerSink.sieker_sink_sink_depth_max ?? null;
        this.sieker_sink_avg_depth_min = siekerSink.sieker_sink_avg_depth_min ?? null;
        this.sieker_sink_avg_depth_max = siekerSink.sieker_sink_avg_depth_max ?? null;

        // this.sieker_sink_max_elevation_min = siekerSink.sieker_sink_max_elevation_min ?? null;
        // this.sieker_sink_max_elevation_max = siekerSink.sieker_sink_max_elevation_max ?? null;
        // this.sieker_sink_min_elevation_min = siekerSink.sieker_sink_min_elevation_min ?? null;
        // this.sieker_sink_min_elevation_max = siekerSink.sieker_sink_min_elevation_max ?? null;
        this.sieker_sink_urbanarea_percent_min = siekerSink.sieker_sink_urbanarea_percent_min ?? null;
        this.sieker_sink_urbanarea_percent_max = siekerSink.sieker_sink_urbanarea_percent_max ?? null;
        this.sieker_sink_wetlands_percent_min = siekerSink.sieker_sink_wetlands_percent_min ?? null;
        this.sieker_sink_wetlands_percent_max = siekerSink.sieker_sink_wetlands_percent_max ?? null;

        this.sieker_sink_distance_t_min = siekerSink.sieker_sink_distance_t_min ?? null;
        this.sieker_sink_distance_t_max = siekerSink.sieker_sink_distance_t_max ?? null;
        this.sieker_sink_dist_lake_min = siekerSink.sieker_sink_dist_lake_min ?? null;
        this.sieker_sink_dist_lake_max = siekerSink.sieker_sink_dist_lake_max ?? null;

        this.sieker_sink_waterdist_min = siekerSink.sieker_sink_waterdist_min ?? null;
        this.sieker_sink_waterdist_max = siekerSink.sieker_sink_waterdist_max ?? null;

        this.all_sieker_sink_ids = siekerSink.all_sieker_sink_ids ?? [];
        this.selected_sieker_sinks = siekerSink.selected_sieker_sinks ?? [];

        this.sieker_sink_feasibility = siekerSink.feasibility ?? [];

        this.selected_sieker_sinks = siekerSink.selected_sieker_sinks ?? [];

    }

    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new SiekerSink(json);
    }
        // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('projectSiekerSink', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('projectSiekerSink');
        return storedProject ? SiekerSink.fromJson(JSON.parse(storedProject)) : null;
    }
};

export class SiekerSurfaceWaters {
    constructor (siekerSurfaceWaters = {}) {
        this.id = siekerSurfaceWaters.id ?? null;
        this.userField = siekerSurfaceWaters.userField ?? null;
        this.sieker_surface_waters_distance_min = siekerSurfaceWaters.sieker_surface_waters_distance_min ?? null;
        this.all_sieker_large_lake_ids = siekerSurfaceWaters.all_sieker_large_lake_ids ?? [];
        this.selected_sieker_large_lakes = siekerSurfaceWaters.selected_sieker_large_lakes ?? [];

        this.sieker_large_lake_d_max_m_max = siekerSurfaceWaters.sieker_large_lake_d_max_m_max ?? null;
        this.sieker_large_lake_d_max_m_min = siekerSurfaceWaters.sieker_large_lake_d_max_m_min ?? null;
        this.sieker_large_lake_vol_mio_m3_min = siekerSurfaceWaters.sieker_large_lake_vol_mio_m3_min ?? null;
        this.sieker_large_lake_vol_mio_m3_max = siekerSurfaceWaters.sieker_large_lake_vol_mio_m3_max ?? null;
        this.sieker_large_lake_area_ha_min = siekerSurfaceWaters.sieker_large_lake_area_ha_min ?? null;
        this.sieker_large_lake_area_ha_max = siekerSurfaceWaters.sieker_large_lake_area_ha_max ?? null;
        // TODO BADESEEN!



    }
    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new SiekerSurfaceWaters(json);
    }

    // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('projectSiekerSurfaceWaters', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('projectSiekerSurfaceWaters');
        return storedProject ? SiekerSurfaceWaters.fromJson(JSON.parse(storedProject)) : null;
    }
};


export class SiekerGek {
    constructor (siekerGek = {}) {
        this.id = siekerGek.id ?? null;
        this.userField = siekerGek.userField ?? null;
        this.selected_gek_retention = siekerGek.selected_gek_retention ?? [];
        this.gek_priority = siekerGek.gek_priority ?? null;
        this.landuse = siekerGek.landuse ?? [];
        this.all_sieker_gek_ids = siekerGek.all_sieker_gek_ids ?? [];
        this.selected_sieker_geks = siekerGek.selected_sieker_geks ?? [];

        this.all_sieker_gek_measure_ids = siekerGek.all_sieker_gek_measure_ids ?? [];
        this.selected_sieker_gek_measures = siekerGek.selected_sieker_gek_measures ?? [];
    }
    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new SiekerGek(json);
    }

    // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('projectSiekerGeks', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('projectSiekerGeks');
        return storedProject ? SiekerGek.fromJson(JSON.parse(storedProject)) : null;
    }
};


export class ToolboxProject {
  constructor (project = {}) {
    this.id = project.id ?? null;
    this.name = project.name ?? '';
    this.updated = project.updated ?? null;
    this.description = project.description ?? '';
    this.userField = project.userField ?? null;
    this.toolboxType = project.toolboxType ?? 1;
  }

    // Convert instance to JSON for storage
    toJson() {
      return JSON.stringify(this);
  }

  // Save project to localStorage
  saveToLocalStorage() {
      localStorage.setItem('toolbox_project', this.toJson());
      updateButtonState(this)
      console.log('saveToLocalStorage');
  }

  // Load project from localStorage
  static loadFromLocalStorage() {
      const storedProject = localStorage.getItem('toolbox_project');
      return storedProject ? ToolboxProject.fromJson(JSON.parse(storedProject)) : null;
  }

  // Static method to create ToolboxProject from JSON
  static fromJson(json) {
      return new ToolboxProject(json);
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