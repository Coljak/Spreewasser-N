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

class Infiltration {
    constructor (infiltration = {}) {
        this.id = infiltration.id ?? null;

        this.sink_area_min = infiltration.sink_area_min ?? null;
        this.sink_area_max = infiltration.sink_area_max ?? null;
        this.sink_volume_min = infiltration.sink_volume_min ?? null;
        this.sink_volume_max = infiltration.sink_volume_max ?? null;
        this.sink_depth_min = infiltration.sink_depth_min ?? null;
        this.sink_depth_max = infiltration.sink_depth_max ?? null;
        this.sink_land_use = infiltration.sink_land_use ?? [];

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

