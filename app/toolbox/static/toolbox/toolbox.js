import { getGeolocation, handleAlerts, getCSRFToken, saveProject, observeDropdown,  setLanguage, populateDropdown } from '/static/shared/utils.js';



export class Infiltration {
    constructor (infiltration = {}) {
        this.id = infiltration.id ?? null;

        this.sinkAreaMin = infiltration.sinkAreaMin ?? null;
        this.sinkAreaMax = infiltration.sinkAreaMax ?? null;
        this.sinkVolumeMin = infiltration.sinkVolumeMin ?? null;
        this.sinkVolumeMax = infiltration.sinkVolumeMax ?? null;
        this.sinkDepthMin = infiltration.sinkDepthMin ?? null;
        this.sinkDepthMax = infiltration.sinkDepthMax ?? null;

        this.sinksSelected = infiltration.sinksSelected ?? [];

        this.enlargedSinkAreaMin = infiltration.enlargedSinkAreaMin ?? null;
        this.enlargedSinkAreaMax = infiltration.enlargedSinkAreaMax ?? null;
        this.enlargedSinkVolumeMin = infiltration.enlargedSinkVolumeMin ?? null;
        this.enlargedSinkVolumeMax = infiltration.enlargedSinkVolumeMax ?? null;
        this.enlargedSinkDepthMin = infiltration.enlargedSinkDepthMin ?? null;
        this.enlargedSinkDepthMax = infiltration.enlargedSinkDepthMax ?? null;

        this.enlargedSinksSelected = infiltration.enlargedSinksSelected ?? [];
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
      console.log('saveToLocalStorage', this.toJson());
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

// export async function saveProject(project) {
//     fetch('save-project/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(project),
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log('Success:', data);
//     });
// }

// export async function getInfiltrationGui() {
//     const project = ToolboxProject.loadFromLocalStorage();
//     const userField = project.userField;
//     const toolboxType = project.toolboxType;
//     const response = await fetch('get_infiltration_gui/' + userField + '/' );
//     const data = await response.json();
//     console.log('getInfiltrationGui', data);
//     return data;
// };



