import { getGeolocation, handleAlerts, getCSRFToken, saveProject, observeDropdown,  setLanguage, populateDropdown } from '/static/shared/utils.js';

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

export class Infiltration {
    constructor (infiltration = {}) {
        this.id = infiltration.id ?? null;
        this.userField = infiltration.userField ?? null;

        this.sink_area_min = infiltration.sink_area_min ?? null;
        this.sink_area_max = infiltration.sink_area_max ?? null;
        this.sink_volume_min = infiltration.sink_volume_min ?? null;
        this.sink_volume_max = infiltration.sink_volume_max ?? null;
        this.sink_depth_min = infiltration.sink_depth_min ?? null;
        this.sink_depth_max = infiltration.sink_depth_max ?? null;
        this.sink_land_use = infiltration.sink_land_use ?? [];
        this.all_sink_ids = infiltration.all_sink_ids ?? [];
        this.selected_sinks = infiltration.selected_sinks ?? [];

        this.enlarged_sink_area_min = infiltration.enlarged_sink_area_min ?? null;
        this.enlarged_sink_area_max = infiltration.enlarged_sink_area_max ?? null;
        this.enlarged_sink_volume_min = infiltration.enlarged_sink_volume_minn ?? null;
        this.enlarged_sink_volume_max = infiltration.enlarged_sink_volume_max ?? null;
        this.enlarged_sink_depth_min = infiltration.enlarged_sink_depth_min ?? null;
        this.enlarged_sink_depth_max = infiltration.enlarged_sink_depth_max ?? null;
        this.enlarged_sink_volume_construction_barrier_min = infiltration.enlarged_sink_volume_construction_barrier_min ?? null;
        this.enlarged_sink_volume_construction_barrier_max = infiltration.enlarged_sink_volume_construction_barrier_max ?? null;
        this.enlarged_sink_volume_gained_min = infiltration.enlarged_sink_volume_gained_min ?? null;
        this.enlarged_sink_volume_gained_max = infiltration.enlarged_sink_volume_gained_max ?? null;
        this.enlarged_sink_land_use = infiltration.enlarged_sink_land_use ?? [];

        this.all_enlarged_sink_ids = infiltration.all_enlarged_sink_ids ?? [];
        this.selected_enlarged_sinks = infiltration.selected_enlarged_sinks ?? [];

        this.stream_min_surplus_volume_min = infiltration.stream_min_surplus_volume_min ?? null;
        this.stream_min_surplus_volume_max = infiltration.stream_min_surplus_volume_max ?? null;
        this.stream_mean_surplus_volume_min = infiltration.stream_mean_surplus_volume_min ?? null;
        this.stream_mean_surplus_volume_max = infiltration.stream_mean_surplus_volume_max ?? null;
        this.stream_max_surplus_volume_min = infiltration.stream_max_surplus_volume_min ?? null;
        this.stream_max_surplus_volume_max = infiltration.stream_max_surplus_volume_max ?? null;
        this.stream_plus_days_min = infiltration.stream_plus_days_min ?? null;
        this.stream_plus_days_max = infiltration.stream_plus_days_max ?? null;
        this.stream_distance_to_userfield = infiltration.stream_distance_to_userfield ?? 0;

        this.lake_min_surplus_volume_min = infiltration.lake_min_surplus_volume_min ?? null;
        this.lake_min_surplus_volume_max = infiltration.lake_min_surplus_volume_max ?? null;
        this.lake_mean_surplus_volume_min = infiltration.lake_mean_surplus_volume_min ?? null;
        this.lake_mean_surplus_volume_max = infiltration.lake_mean_surplus_volume_max ?? null;
        this.lake_max_surplus_volume_min = infiltration.lake_max_surplus_volume_min ?? null;
        this.lake_max_surplus_volume_max = infiltration.lake_max_surplus_volume_max ?? null;
        this.lake_plus_days_min = infiltration.lake_plus_days_min ?? null;
        this.lake_plus_days_max = infiltration.lake_plus_days_max ?? null;
        this.lake_distance_to_userfield = infiltration.lake_distance_to_userfield ?? 0;

        this.selected_lakes = infiltration.selected_lakes ?? [];
        this.selected_streams = infiltration.selected_streams ?? [];

        this.weighting_overall_usability = infiltration.weighting_overall_usability ?? 20;
        this.weighting_soil_index = infiltration.weighting_soil_index ?? 80;

        this.weighting_forest_field_capacity = infiltration.weighting_forest_field_capacity ?? 33;
        this.weighting_forest_hydraulic_conductivity_1m = infiltration.weighting_forest_hydraulic_conductivity_1m ?? 33;
        this.weighting_forest_hydraulic_conductivity_2m = infiltration.weighting_forest_hydraulic_conductivity_2m ?? 33;

        this.weighting_agriculture_field_capacity = infiltration.weighting_agriculture_field_capacity ?? 33;
        this.weighting_agriculture_hydromorphy = infiltration.weighting_agriculture_hydromorphy ?? 33;
        this.weighting_agriculture_soil_type = infiltration.weighting_agriculture_soil_type ?? 33;

        this.weighting_grassland_field_capacity = infiltration.weighting_grassland_field_capacity ?? 25;
        this.weighting_grassland_hydromorphy = infiltration.weighting_grassland_hydromorphy ?? 25;
        this.weighting_grassland_soil_type = infiltration.weighting_grassland_soil_type ?? 25;
        this.weighting_grassland_soil_water_ratio = infiltration.weighting_grassland_soil_water_ratio ?? 25;

    }

    toJson() {
        return JSON.stringify(this);
    }

    static fromJson(json) {
      return new Infiltration(json);
    }
         // Save project to localStorage
    saveToLocalStorage() {
        localStorage.setItem('projectInfiltration', this.toJson());
    }

    // Load project from localStorage
    static loadFromLocalStorage() {
        const storedProject = localStorage.getItem('projectInfiltration');
        return storedProject ? Infiltration.fromJson(JSON.parse(storedProject)) : null;
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
    this.infiltration = new Infiltration(project.infiltration) ?? new Infiltration();
    this.siekerSink = new SiekerSink(project.siekerSink) ?? new SiekerSink();
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
    $('#toolboxPanel').on('change',  function (event) {
        const $target = $(event.target);
        const project = projectType.loadFromLocalStorage();
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
            // Value does not exist — add it
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
            console.log("Selected sink:", $target.data('id'));
            console.log("key:", key);
            console.log('project[key]', project[key])
            console.log(project)
            project[key].push($target.data('id'));
            project.saveToLocalStorage();

            } else {
            const dataId = $target.data('id');
            console.log("Selected sink:", dataId);
            
            const index = project[key].indexOf(dataId);
            if (index > -1) {
                project[key].splice(index, 1);
            }
            project.saveToLocalStorage();
            }

            // You can trigger your map sink selection logic here
        };
        });
    };